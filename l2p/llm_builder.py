"""
This file contains code for calling LLMs and saving raw model outputs 
Currently, this builder class contains the generic method to run any LLMs. 
It also offers extension to OpenAI, OLLAMA, and Huggingface.
"""

import os
import tiktoken
import requests
# import torch
from retry import retry
from openai import OpenAI
# from transformers import AutoModelForCausalLM, AutoTokenizer

class LLM_Chat:
    """Generic method that dynamically chooses between LLM engines"""
    
    def __init__(self, *args, **kwargs):
        pass

    def get_output(self, prompt=None, messages=None):
        raise NotImplementedError
    
    def get_tokens(self) -> tuple[int, int]:
        raise NotImplementedError
    
    def reset_tokens(self):
        raise NotImplementedError

class GPT_Chat(LLM_Chat):
    def __init__(self, client, model, stop=None, max_tokens=4e3, temperature=0, top_p=1,
                 frequency_penalty=0.0, presence_penalty=0.0, seed=0):
        self.client = client
        self.model = model
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

    def get_output(self, prompt=None, messages=None, end_when_error=False, max_retry=5, est_margin = 200):
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


class HF_Inference_Chat(LLM_Chat):
    def __init__(self, model, api_key, max_tokens=4069, temperature=0.2):
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.API_URL = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.in_tokens = 0
        self.out_tokens = 0

    def get_output(self, prompt=None, messages=None):
        if prompt is None and messages is None:
            raise ValueError("prompt and messages cannot both be None")
        if messages is not None:
            prompt = ' '.join([m['content'] for m in messages])
        
        data = {
            "inputs": prompt,
            "parameters": {
                "max_length": self.max_tokens,
                "temperature": self.temperature
            }
        }
        
        print(f'[INFO] connecting to the LLM ...')
        response = requests.post(self.API_URL, headers=self.headers, json=data)
        if response.status_code == 200:
            generated_text = response.json()[0]['generated_text']
            filtered_text = generated_text.replace(prompt, "").strip()
            # filtered_text = filtered_text.split('\n')[0]
            # self.out_tokens += len(self.tokenizer(filtered_text)['input_ids'])
            # self.in_tokens += len(self.tokenizer(prompt)['input_ids'])
            return filtered_text
        else:
            raise Exception(f"Failed to generate text: {response.status_code} {response.text}")

    def get_tokens(self) -> tuple[int, int]:
        return self.in_tokens, self.out_tokens
    
    def reset_tokens(self):
        self.in_tokens = 0
        self.out_tokens = 0
    

class HF_Transformer_Chat(LLM_Chat): pass
    # def __init__(self, model, tokenizer_name=None, max_tokens=1024, temperature=0.7):
    #     self.model = model
    #     self.tokenizer_name = tokenizer_name or model
    #     self.max_tokens = max_tokens
    #     self.temperature = temperature
        
    #     # Load model and tokenizer
    #     self.model = AutoModelForCausalLM.from_pretrained(model)
    #     self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_name)
        
    #     self.in_tokens = 0
    #     self.out_tokens = 0

    # def get_output(self, prompt=None, messages=None):
    #     if prompt is None and messages is None:
    #         raise ValueError("Prompt and messages cannot both be None")
    #     if messages is not None:
    #         prompt = ' '.join([m['content'] for m in messages])
        
    #     inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=self.max_tokens)
    #     input_ids = inputs["input_ids"].to(self.model.device)

    #     with torch.no_grad():
    #         output = self.model.generate(
    #             input_ids,
    #             max_length=self.max_tokens,
    #             temperature=self.temperature
    #         )

    #     generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
    #     response_tokens = len(self.tokenizer.encode(generated_text))
        
    #     self.in_tokens += len(inputs["input_ids"][0])
    #     self.out_tokens += response_tokens

    #     return generated_text

    # def get_tokens(self) -> tuple[int, int]:
    #     return self.in_tokens, self.out_tokens
    
    # def reset_tokens(self):
    #     self.in_tokens = 0
    #     self.out_tokens = 0
    

class OLLAMA_Chat(LLM_Chat):
    def __init__(self, engine, stop=None, max_tokens=8e3, temperature=0, top_p=1,
                 frequency_penalty=0.0, presence_penalty=0.0, seed=0):
        self.engine = engine
        self.url = os.environ.get("OLLAMA_URL", ).strip("/").replace("api/generate", "api/chat")
        if not self.url.endswith("/"):
            self.url += "/"
        if not self.url.endswith("api/chat/"):
            self.url += "api/chat/"
        self.temperature = temperature
        self.seed = seed
        self.top_p = top_p
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.in_tokens = 0
        self.out_tokens = 0
        self.tok = tiktoken.get_encoding("cl100k_base") # For GPT3.5+

    def get_response(self, prompt=None, messages=None):
        if prompt is None and messages is None:
            raise ValueError("prompt and messages cannot both be None")
        if messages is not None:
            messages = messages
        else:
            messages = [{'role': 'user', 'content': prompt}]

        self.in_tokens += sum([len(self.tok.encode(m['content'])) for m in messages])

        to_send = {
            "model": self.engine,
            "messages": messages,
            "stream": False,
            "options": {
                "seed": self.seed,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "presence_penalty": self.presence_penalty,
                "frequency_penalty": self.frequency_penalty
            }
        }

        resp = requests.post(self.url, json=to_send)
        if resp.status_code != 200:
            print(f"Failed to connect to OLLAMA at {self.url}: {resp.status_code}. \n\t{resp.text}")
            raise ConnectionError(f"Failed to connect to OLLAMA at {self.url}: {resp.status_code}. \n\t{resp.text}")
        ans = resp.json()["message"]["content"]

        self.out_tokens += len(self.tok.encode(ans))

        return ans

    def token_usage(self) -> tuple[int, int]:
        print("WARNING: Ollama token usage is currently estimated with GPT tokenization.")
        return self.in_tokens, self.out_tokens
    
    def reset_token_usage(self):
        self.in_tokens = 0
        self.out_tokens = 0
    

def get_llm(engine, model, **kwargs) -> LLM_Chat:
    if engine == "gpt":
        return GPT_Chat(model=model, **kwargs)
    elif engine == "ollama":
        return OLLAMA_Chat(model, **kwargs)
    elif engine == "hf_inference":
        return HF_Inference_Chat(model=model, **kwargs)
    elif engine == "hf_transformer":
        return HF_Transformer_Chat(model=model, **kwargs)


if __name__ == '__main__':
    
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None))
    
    # Use get_llm to create the model instance
    model = get_llm(engine="gpt", model="gpt-4o-mini", client=client)
    
    # Call the model's method
    llm_response = model.get_output(prompt="Any TV show recommendations?")
    print(llm_response)
    
    model = get_llm(engine="hf_inference", model="mistralai/Mistral-7B-Instruct-v0.3", api_key="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")
    llm_response = model.get_output(prompt="Any TV show recommendations?")
    print(llm_response)
