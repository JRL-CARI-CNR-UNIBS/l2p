"""
This file contains code for calling LLMs and saving raw model outputs 
Currently, this builder class contains the generic method to run any LLMs. 
It also offers extension to OpenAI and Huggingface, but can generalise to any third-party LLM store.
"""

import transformers
from transformers import AutoTokenizer
import torch
import os, tiktoken, logging, argparse
from retry import retry
from openai import OpenAI
from abc import ABC, abstractmethod
from typing_extensions import override

LOG: logging.Logger = logging.getLogger(__name__)

class LLM(ABC):
    def __init__(self, model: str, api_key: str | None = None) -> None:
        if model not in self.valid_models():
            LOG.warning(
                f"{model} is not in the valid model list for {type(self).__name__}. Valid models are: {', '.join(self.valid_models())}."
            )
        self.model: str = model
        self.api_key: str | None = api_key
       
    @abstractmethod 
    def query(self, prompt: str) -> str:
        """
        Abstract method to query an LLM with a given prompt and return the response.
        
        Args:
            prompt (str): The prompt to send to the LLM
        Returns:
            str: The response from the LLM
        """
        pass
    
    def query_with_system_prompt(self, system_prompt: str, prompt: str) -> str:
        """
        Abstract methody to query an LLM with a given prompt and system prompt and return the response.
        
        Args:
            system_prompt (str): The system prompt to send to the LLM
            prompt (str): The prompt to send to the LLM
        Returns:
            str: The response from the LLM
        """
        return self.query(system_prompt + "\n" + prompt)
    
    def valid_models(self) -> list[str]:
        """
        List of valid model parameters, e.g., 'gpt4o-mini' for GPT
        """
        return []


class OPENAI(LLM):
    """Accessing OpenAI"""
    
    def __init__(self, model: str, api_key: str | None = None, client=None, stop=None, max_tokens=4e3, 
                 temperature=0, top_p=1, frequency_penalty=0.0, presence_penalty=0.0, seed=0) -> None:
        # Call the parent class constructor to handle model and api_key
        super().__init__(model, api_key)
        
        # Initialize the OpenAI client or use the one provided
        self.client = client if client else OpenAI(api_key=api_key)
        
        # Store other parameters
        self.temperature = temperature
        self.top_p = top_p
        self.freq_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop
        
        self.context_length = {
            "gpt-3.5-turbo-0125": 16e3, # 16k tokens
            "gpt-3.5-turbo-instruct": 4e3, # 4k tokens
            "gpt-4-1106-preview": 128e3, # 128k tokens
            "gpt-4-turbo-2024-04-09": 128e3, # 128k tokens
            "gpt-4": 8192, # ~8k tokens
            "gpt-4-32k": 32768, # ~32k tokens
            "gpt-4o": 32768, # ~32k tokens
            "gpt-4o-mini": 32768, # ~32k tokens
        }[model]
        
        self.max_tokens = max_tokens if max_tokens is not None else self.context_length
        self.tok = tiktoken.get_encoding("cl100k_base") # For GPT3.5+
        self.in_tokens = 0
        self.out_tokens = 0
        
    @retry(tries=2, delay=60)
    def connect_openai(self, client, model, messages, temperature, max_tokens,
                    top_p, frequency_penalty, presence_penalty, stop):
        return client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop
        )

    @override
    def query(self, prompt: str, messages=None, end_when_error=False, max_retry=5, est_margin = 200) -> str:
        if prompt is None and messages is None:
            raise ValueError("Prompt and messages cannot both be None")
        if messages is not None:
            messages = messages
        else:
            messages = [{'role': 'user', 'content': prompt}]

        # calculate # of tokens to request. At most self.max_tokens, and prompt + request < self.context_length
        current_tokens = int(sum([len(self.tok.encode(m['content'])) for m in messages])) # estimate current usage
        requested_tokens = int(min(self.max_tokens, self.context_length - current_tokens - est_margin)) # request with safety margin
        print(f"Requesting {requested_tokens} tokens from {self.model} (estimated {current_tokens - est_margin} prompt tokens with a safety margin of {est_margin} tokens)")
        self.in_tokens += current_tokens

        # request response
        n_retry = 0
        conn_success = False
        while not conn_success:
            n_retry += 1
            if n_retry >= max_retry:
                break
            try:
                print(f'[INFO] connecting to the LLM ({requested_tokens} tokens)...')
                response = self.connect_openai(
                    client=self.client,
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=requested_tokens,
                    top_p=self.top_p,
                    frequency_penalty=self.freq_penalty,
                    presence_penalty=self.presence_penalty,
                    stop=self.stop
                )
                llm_output = response.choices[0].message.content # response['choices'][0]['message']['content']
                conn_success = True
            except Exception as e:
                print(f'[ERROR] LLM error: {e}')
                if end_when_error:
                    break
        if not conn_success:
            raise ConnectionError(f'Failed to connect to the LLM after {max_retry} retries')
        
        response_tokens = len(self.tok.encode(llm_output)) # Estimate response tokens
        self.out_tokens += response_tokens

        return llm_output
    
    def get_tokens(self) -> tuple[int, int]:
        return self.in_tokens, self.out_tokens
    
    def reset_tokens(self):
        self.in_tokens = 0
        self.out_tokens = 0
        
    @override    
    def valid_models(self) -> list[str]:
        """
        List of valid model parameters for OpenAI.
        Returns a list of valid OpenAI model names.
        """
        return [
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo-instruct",
            "gpt-4-1106-preview",
            "gpt-4-turbo-2024-04-09",
            "gpt-4",
            "gpt-4-32k",
            "gpt-4o",
            "gpt-4o-mini"
        ]


class HUGGING_FACE(LLM):
    def __init__(self, model_path: str, max_tokens=4e3, temperature=0.01, top_p=0.9):
        self.model = transformers.pipeline(
          "text-generation",
          model=model_path,
          model_kwargs={"torch_dtype": torch.bfloat16},
          device_map="auto",
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.in_tokens = 0
        self.out_tokens = 0
    
    # Retry decorator to handle retries on request
    @retry(tries=2, delay=60)
    def connect_huggingface(self, input, temperature, max_tokens, top_p, numSample):
        if numSample > 1:
            responses = []
            sequences = self.model(
                input,
                do_sample=True,
                top_k=1,
                num_return_sequences=numSample,
                max_new_tokens=max_tokens,
                return_full_text=False,
                temperature=temperature,
                top_p=top_p,
                pad_token_id=self.tokenizer.eos_token_id
            )

            for seq in sequences:
                response = seq['generated_text']  
                responses.append(response)
            return responses
        
        else:
            sequences = self.model(
                input,
                do_sample=True,
                num_return_sequences=1,
                max_new_tokens=max_tokens,
                return_full_text=False,
                temperature=temperature,
                top_p=top_p,
                pad_token_id=self.tokenizer.eos_token_id
            )

            seq = sequences[0]
            response = seq['generated_text']
            
            return response
    
    @override
    def query(self, prompt: str, numSample=1, max_retry=3, est_margin=200) -> str:
        if prompt is None:
            raise ValueError("Prompt cannot be None")
        
        # Estimate current usage of tokens
        current_tokens = len(self.tokenizer.encode(prompt))
        requested_tokens = min(self.max_tokens, self.max_tokens - current_tokens - est_margin)
        
        print(f"Requesting {requested_tokens} tokens from {self.model} (estimated {current_tokens - est_margin} prompt tokens with a safety margin of {est_margin} tokens)")
        
        # Retry logic for Hugging Face request
        n_retry = 0
        conn_success = False
        while not conn_success and n_retry < max_retry:
            n_retry += 1
            try:
                print(f"[INFO] Connecting to Hugging Face model ({requested_tokens} tokens)...")
                llm_output = self.connect_huggingface(
                    input=prompt,
                    temperature=self.temperature,
                    max_tokens=requested_tokens,
                    top_p=self.top_p,
                    numSample=numSample
                )
                conn_success = True
            except Exception as e:
                print(f"[ERROR] Hugging Face error: {e}")
                if n_retry >= max_retry:
                    raise ConnectionError(f"Failed to connect to the Hugging Face model after {max_retry} retries")

        # Token management
        response_tokens = len(self.tokenizer.encode(llm_output))
        self.out_tokens += response_tokens
        self.in_tokens += current_tokens
        
        return llm_output
        
    def get_tokens(self) -> tuple[int, int]:
        return self.in_tokens, self.out_tokens
    
    def reset_tokens(self):
        self.in_tokens = 0
        self.out_tokens = 0
    

if __name__ == '__main__':
    
    # test out OpenAI GPT
    api_key = os.environ.get('OPENAI_API_KEY')
    model_name = "gpt-4o-mini"
    openai_llm = OPENAI(model=model_name, api_key=api_key)
    
    prompt = "What is the capital of France?"
    response = openai_llm.query(prompt)
    print(f"Response from {model_name}: {response}")
    
    # test out Huggingface model
    parser = argparse.ArgumentParser(description="Define Parameters")
    parser.add_argument('-test_dataset', action='store_true') # test custom prompt by default, set flag to run predictions over a specific dataset 
    parser.add_argument("--temp", type=float, default=0.01, help = "temperature for sampling")
    parser.add_argument("--max_len", type=int, default=4e3, help = "max number of tokens in answer")
    parser.add_argument("--num_sample", type=int, default=1, help = "number of answers to sample")
    parser.add_argument("--model_path", type=str, default="/path/to/model", help = "path to llm")
    args = parser.parse_args()    

    huggingface_model = HUGGING_FACE(model_path=args.model_path, max_tokens=args.max_len, temperature=args.temp)
    
    prompt = "What is the capital of the United States?"
    input = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>{prompt}<|eot_id|>\n"""
    response = huggingface_model.query(prompt=input, numSample=args.num_sample, max_retry=3)
    print(f"Response: {response}")
