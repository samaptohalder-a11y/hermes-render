import os
import requests

class AIAgent:
    def __init__(self, skip_memory=False):
        self.api_key = os.getenv('OPENROUTER_API_KEY')

    def run(self, prompt: str) -> str:
        if not self.api_key:
            return 'Error: OPENROUTER_API_KEY environment variable is not set.'
        
        # Example call to OpenRouter API
        try:
            response = requests.post(
                url='https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'meta-llama/llama-3.3-70b-instruct',
                    'messages': [{'role': 'user', 'content': prompt}]
                }
            )
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            return f'AI Execution Error: {str(e)}'
