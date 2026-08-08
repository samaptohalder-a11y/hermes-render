import os
import uvicorn
import requests
import subprocess
import smtplib
from email.message import EmailMessage
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from hermes import AIAgent

app = FastAPI(title='Hermes Agent API')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
FB_PAGE_ID = os.getenv('FB_PAGE_ID')
FB_PAGE_ACCESS_TOKEN = os.getenv('FB_PAGE_ACCESS_TOKEN')

HERMES_CONTEXT = 'You are Hermes, an autonomous AI agent equipped with tools to execute terminal commands, search the web, and send emails on behalf of the user.'

# --- TOOL 1: Web Search ---
def web_search(query: str) -> str:
    '''Searches the web for real-time information and returns key text content.'''
    try:
        url = f'https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        return res.text[:2000]
    except Exception as e:
        return f'Web search error: {str(e)}'

# --- TOOL 2: Terminal / Shell Execution ---
def execute_terminal_command(command: str) -> str:
    '''Executes a terminal or shell command on the host container and returns the output.'''
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout if result.returncode == 0 else result.stderr
        return output or 'Command executed with no output.'
    except Exception as e:
        return f'Terminal error: {str(e)}'

# --- TOOL 3: Send Email ---
def send_email(to_email: str, subject: str, body: str) -> str:
    '''Sends an email to a recipient using configured SMTP environment variables.'''
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')

    if not sender_email or not sender_password:
        return 'Email failed: SENDER_EMAIL or SENDER_PASSWORD environment variables are not set on Render.'

    try:
        msg = EmailMessage()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.set_content(body)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return f'Successfully sent email to {to_email}'
    except Exception as e:
        return f'Email error: {str(e)}'

AVAILABLE_TOOLS = [web_search, execute_terminal_command, send_email]

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
        agent = AIAgent(tools=AVAILABLE_TOOLS, skip_memory=True)
        agent_response = agent.run(HERMES_CONTEXT + '\nUser request: ' + request.message)
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
                agent = AIAgent(tools=AVAILABLE_TOOLS, skip_memory=True)
                response_text = str(agent.run(HERMES_CONTEXT + '\nUser request: ' + user_text))
            except Exception as err:
                response_text = f'Error during tool execution: {str(err)}'
            
            if TELEGRAM_TOKEN:
                telegram_url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
                requests.post(telegram_url, json={'chat_id': chat_id, 'text': response_text})
    except Exception as e:
        print(f'Webhook error: {e}')
    return {'status': 'ok'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run('main:app', host='0.0.0.0', port=port, reload=False)
