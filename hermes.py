import os
import requests

class AIAgent:
    def __init__(self, skip_memory=False):
        self.api_key = os.getenv('OPENROUTER_API_KEY')

    def run(self, prompt: str) -> str:
        if not self.api_key:
            return 'Error: OPENROUTER_API_KEY environment variable is not set.'
        
        try:
            response = requests.post(
                url='https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'openrouter/free',
                    'messages': [{'role': 'user', 'content': prompt}]
                }
            )
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            else:
                return f'OpenRouter API Error: {data}'
        except Exception as e:
            return f'AI Execution Error: {str(e)}'
