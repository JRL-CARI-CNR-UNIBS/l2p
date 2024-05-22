import requests

API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-1.3B"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
output = query({
	"inputs": "Generate a PDDL file"
})

print(output)