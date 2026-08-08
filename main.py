import os
import uvicorn
import requests
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from hermes import AIAgent

app = FastAPI(title='Hermes Agent API')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
FB_PAGE_ID = os.getenv('FB_PAGE_ID')
FB_PAGE_ACCESS_TOKEN = os.getenv('FB_PAGE_ACCESS_TOKEN')

HERMES_CONTEXT = 'You are Hermes, an autonomous AI agent. You are helpful, precise, and direct. User prompt: '

class ChatRequest(BaseModel):
    message: str

class FBPostRequest(BaseModel):
    prompt: str

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
        agent_response = agent.run(HERMES_CONTEXT + request.message)
        return {'status': 'success', 'prompt': request.message, 'response': str(agent_response)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Agent Execution Error: {str(e)}')

@app.post('/post-facebook')
def post_to_facebook(request: FBPostRequest):
    if not FB_PAGE_ID or not FB_PAGE_ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail='Facebook credentials are not set in environment variables.')
    
    try:
        agent = AIAgent(skip_memory=True)
        post_content = agent.run(f'Write an engaging Facebook post about: {request.prompt}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'LLM Error: {str(e)}')
    
    fb_url = f'https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed'
    payload = {
        'message': post_content,
        'access_token': FB_PAGE_ACCESS_TOKEN
    }
    
    fb_response = requests.post(fb_url, data=payload)
    data = fb_response.json()
    
    if 'id' in data:
        return {'status': 'success', 'facebook_post_id': data['id'], 'content': post_content}
    else:
        return {'status': 'error', 'details': data}

@app.post('/webhook')
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if 'message' in data and 'text' in data['message']:
            chat_id = data['message']['chat']['id']
            user_text = data['message']['text']
            
            try:
                agent = AIAgent(skip_memory=True)
                response_text = str(agent.run(HERMES_CONTEXT + user_text))
            except Exception as err:
                response_text = f'Sorry, an error occurred with the AI model: {str(err)}'
            
            if TELEGRAM_TOKEN:
                telegram_url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
                requests.post(telegram_url, json={'chat_id': chat_id, 'text': response_text})
    except Exception as e:
        print(f'Webhook error: {e}')
    return {'status': 'ok'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run('main:app', host='0.0.0.0', port=port, reload=False)
