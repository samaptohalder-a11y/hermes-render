import os
import requests
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from hermes import AIAgent

app = FastAPI(title='Hermes Agent API')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

class ChatRequest(BaseModel):
    message: str

@app.get('/')
def health_check():
    return {'status': 'healthy', 'service': 'Hermes Agent'}

@app.post('/chat')
def chat_endpoint(request: ChatRequest, authorization: str = Header(None)):
    expected_key = os.getenv('AGENT_API_KEY')
    if expected_key and authorization != f'Bearer {expected_key}':
        raise HTTPException(status_code=401, detail='Unauthorized')
    try:
        agent = AIAgent(skip_memory=True)
        agent_response = agent.run(request.message)
        return {'status': 'success', 'prompt': request.message, 'response': str(agent_response)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Agent Execution Error: {str(e)}')

@app.post('/webhook')
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if 'message' in data and 'text' in data['message']:
            chat_id = data['message']['chat']['id']
            user_text = data['message']['text']
            agent = AIAgent(skip_memory=True)
            response_text = agent.run(user_text)
            if TELEGRAM_TOKEN:
                telegram_url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
                requests.post(telegram_url, json={'chat_id': chat_id, 'text': response_text})
    except Exception as e:
        print(f'Webhook error: {e}')
    return {'status': 'ok'}
