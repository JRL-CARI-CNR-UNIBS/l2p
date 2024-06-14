"""
This file contains code for calling LLMs and saving raw model outputs 
"""

import os
import time
import json
import copy
import requests

#model_name = "openai-community/gpt2"
model_name = "meta-llama/Meta-Llama-3-8B"

api_key = "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"

API_URL = f"https://api-inference.huggingface.co/models/{model_name}"

headers = {"Authorization": f"Bearer {api_key}",
           "Content-Type": "application/json"}

def query(prompt, max_length=50, temperature=0.7):
    data = {
        "inputs": prompt,
        "parameters": {
            "max_length": max_length,
            "temperature": temperature
        }
    }

    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()[0]['generated_text']
    else:
        raise Exception(f"Failed to generate text: {response.status_code} {response.text}")

if __name__ == "__main__":
    prompt = "This is my PDDL file:"
    generated_text = query(prompt)
    print(generated_text)