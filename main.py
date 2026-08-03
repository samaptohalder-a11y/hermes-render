import os
import sys
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import uvicorn

from hermes import AIAgent

app = FastAPI(title='Hermes Agent API')

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

    user_prompt = request.message

    try:
        agent = AIAgent(skip_memory=True)
        agent_response = agent.run(user_prompt)
        return {
            'status': 'success',
            'prompt': user_prompt,
            'response': str(agent_response)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Agent Execution Error: {str(e)}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run('main:app', host='0.0.0.0', port=port, reload=False)
