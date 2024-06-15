"""
This file contains code for calling LLMs and saving raw model outputs 
"""

import os
import time
import json
import copy
import requests
from openai import OpenAI

# for any models in Huggingface API inference
model_name = "openai-community/gpt2"
HF_api_key = "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"
API_URL = f"https://api-inference.huggingface.co/models/{model_name}"

headers = {"Authorization": f"Bearer {HF_api_key}",
           "Content-Type": "application/json"}

def HF_query(prompt, max_length=50, temperature=0.7):
    data = {
        "inputs": prompt,
        "parameters": {
            "max_length": max_length,
            "temperature": temperature
        }
    }

    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        generated_text = response.json()[0]['generated_text']
        
		# removing the input prompt from the generated text
        filtered_text = generated_text.replace(prompt, "").strip()
        return filtered_text
    else:
        raise Exception(f"Failed to generate text: {response.status_code} {response.text}")


# for OpenAI LLM inference
client = OpenAI()
def GPT_query(prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant skilled in generating PDDL components."},
            {"role": "user", "content": prompt}
        ],
    )
    # extract the generated text
    return completion.choices[0].message.content