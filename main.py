import os
import requests
from fastapi import FastAPI, Request
from hermes import AIAgent

app = FastAPI(title='Hermes Agent API')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

@app.get('/')
def health_check():
    return {'status': 'healthy', 'service': 'Hermes Agent'}

@app.post('/webhook')
async def telegram_webhook(request: Request):
    data = await request.json()
    
    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        user_text = data['message']['text']
        
        # Run Hermes AIAgent
        agent = AIAgent(skip_memory=True)
        response_text = agent.run(user_text)
        
        # Reply back to user on Telegram
        if TELEGRAM_TOKEN:
            telegram_url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
            requests.post(telegram_url, json={
                'chat_id': chat_id,
                'text': response_text
            })
            
    return {'status': 'ok'}
