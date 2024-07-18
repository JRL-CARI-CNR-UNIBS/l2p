"""
This file contains code for calling LLMs and saving raw model outputs 
"""

import os
import tiktoken
from retry import retry
from openai import OpenAI

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None))

@retry(tries=2, delay=60)
def connect_openai(engine, messages, temperature, max_tokens,
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

class LLM_Chat:
    # Simple abstract class for the LLM chat
    def __init__(self, *args, **kwargs):
        pass

    def get_output(self, prompt=None, messages=None):
        raise NotImplementedError
    
    def get_tokens(self) -> tuple[int, int]:
        raise NotImplementedError
    
    def reset_tokens(self):
        raise NotImplementedError

class GPT_Chat(LLM_Chat):
    def __init__(self, engine, stop=None, max_tokens=4e3, temperature=0, top_p=1,
                 frequency_penalty=0.0, presence_penalty=0.0, seed=0):
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
            "gpt-4o-mini": 32768,
        }[engine]
        self.max_tokens = max_tokens if max_tokens is not None else self.context_length
        self.tok = tiktoken.get_encoding("cl100k_base") # For GPT3.5+
        self.in_tokens = 0
        self.out_tokens = 0
        print(f"Seed is not used for OpenAI models. Discarding seed {seed}")

    def get_output(self, prompt=None, messages=None, end_when_error=False, max_retry=5, est_margin = 200):
        if prompt is None and messages is None:
            raise ValueError("prompt and messages cannot both be None")
        if messages is not None:
            messages = messages
        else:
            messages = [{'role': 'user', 'content': prompt}]

        # Calculate the number of tokens to request. At most self.max_tokens, and prompt + request < self.context_length
        current_tokens = int(sum([len(self.tok.encode(m['content'])) for m in messages])) # Estimate current usage
        requested_tokens = int(min(self.max_tokens, self.context_length - current_tokens - est_margin)) # Request with safety margin
        print(f"Requesting {requested_tokens} tokens from {self.engine} (estimated {current_tokens - est_margin} prompt tokens with a safety margin of {est_margin} tokens)")
        self.in_tokens += current_tokens

        # Request the response
        n_retry = 0
        conn_success = False
        while not conn_success:
            n_retry += 1
            if n_retry >= max_retry:
                break
            try:
                print(f'[INFO] connecting to the LLM ({requested_tokens} tokens)...')
                response = connect_openai(
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

def get_llm(engine, **kwargs) -> LLM_Chat:
    if "gpt-" in engine:
        return GPT_Chat(engine, **kwargs)

if __name__ == '__main__':
    model = get_llm("gpt-3.5-turbo-0125")
    print(model.get_output("Hello world!"))

    # # for any models in Huggingface API inference
    # model_name = "openai-community/gpt2"
    # HF_api_key = "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"
    # API_URL = f"https://api-inference.huggingface.co/models/{model_name}"

    # headers = {"Authorization": f"Bearer {HF_api_key}",
    #            "Content-Type": "application/json"}

    # def HF_query(prompt, max_length=50, temperature=0.7):
    #     data = {
    #         "inputs": prompt,
    #         "parameters": {
    #             "max_length": max_length,
    #             "temperature": temperature
    #         }
    #     }

    #     response = requests.post(API_URL, headers=headers, json=data)
    #     if response.status_code == 200:
    #         generated_text = response.json()[0]['generated_text']
            
    # 		# removing the input prompt from the generated text
    #         filtered_text = generated_text.replace(prompt, "").strip()
    #         return filtered_text
    #     else:
    #         raise Exception(f"Failed to generate text: {response.status_code} {response.text}")


    # # for OpenAI LLM inference
    # client = OpenAI()
    # def GPT_query(prompt):
    #     completion = client.chat.completions.create(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "system", "content": "You are an assistant skilled in generating PDDL components."},
    #             {"role": "user", "content": prompt}
    #         ],
    #     )
    #     # extract the generated text
    #     return completion.choices[0].message.content
