import os
import sys
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import uvicorn

# Initialize FastAPI app
app = FastAPI(title='Hermes Agent API')

class ChatRequest(BaseModel):
    message: str

# Health check endpoint for Render
@app.get('/')
def health_check():
    return {'status': 'healthy', 'service': 'Hermes Agent'}

# Chat endpoint to interact with your Hermes Agent
@app.post('/chat')
def chat_endpoint(request: ChatRequest, authorization: str = Header(None)):
    # Optional API Key security check
    expected_key = os.getenv('AGENT_API_KEY')
    if expected_key and authorization != f'Bearer {expected_key}':
        raise HTTPException(status_code=401, detail='Unauthorized')

    user_prompt = request.message
    
    # TODO: Connect your Hermes Agent logic here
    # response = agent.run(user_prompt)
    agent_response = f'Hermes Agent received: {user_prompt}'

    return {
        'status': 'success',
        'prompt': user_prompt,
        'response': agent_response
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run('main:app', host='0.0.0.0', port=port, reload=False)
