"""
This file contains code for calling LLMs and saving raw model outputs 
"""

import os
import tiktoken
import requests
from retry import retry
from openai import OpenAI

class LLM_Chat:
    def __init__(self, *args, **kwargs):
        pass

    def get_output(self, prompt=None, messages=None):
        raise NotImplementedError
    
    def get_tokens(self) -> tuple[int, int]:
        raise NotImplementedError
    
    def reset_tokens(self):
        raise NotImplementedError

class GPT_Chat(LLM_Chat):
    def __init__(self, client, engine, stop=None, max_tokens=4e3, temperature=0, top_p=1,
                 frequency_penalty=0.0, presence_penalty=0.0, seed=0):
        self.client = client
        self.engine = engine
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
        }[engine]
        self.max_tokens = max_tokens if max_tokens is not None else self.context_length
        self.tok = tiktoken.get_encoding("cl100k_base") # For GPT3.5+
        self.in_tokens = 0
        self.out_tokens = 0
        
    @retry(tries=2, delay=60)
    def connect_openai(self, client, engine, messages, temperature, max_tokens,
                    top_p, frequency_penalty, presence_penalty, stop):
        return client.chat.completions.create(
            model=engine,
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
        print(f"Requesting {requested_tokens} tokens from {self.engine} (estimated {current_tokens - est_margin} prompt tokens with a safety margin of {est_margin} tokens)")
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
                    engine=self.engine,
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

class HF_Chat(LLM_Chat):
    def __init__(self, engine, api_key, max_tokens=4069, temperature=0.2):
        self.model_name = engine
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.API_URL = f"https://api-inference.huggingface.co/models/{self.model_name}"
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
    
    # def reset_tokens(self):
    #     self.in_tokens = 0
    #     self.out_tokens = 0

if __name__ == '__main__':
    
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None))
    model = GPT_Chat(client=client, engine="gpt-4o-mini")
    llm_response = model.get_output(prompt="Any TV show recommendations?")
    print(llm_response)
    
    model = HF_Chat(engine="mistralai/Mistral-7B-Instruct-v0.3", api_key="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")
    llm_response = model.get_output(prompt="Any TV show recommendations?")
    print(llm_response)
