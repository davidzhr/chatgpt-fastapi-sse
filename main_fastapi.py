
# The idea is from https://amittallapragada.github.io/docker/fastapi/python/2020/12/23/server-side-events.html


from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from sse_starlette.sse import EventSourceResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import openai

import os
from dotenv import load_dotenv


app = FastAPI()

#add CORS so our web page can connect to our api
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load_dotnev will parse the .env file and set the variables in environment automatically.
load_dotenv()

# set the env variables for openai
openai.api_key = os.getenv("AZURE_API_KEY")
openai.api_version = os.getenv("OPENAI_API_VERSION")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_type = "azure"

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse('chatpgt.html', context={"request": request})


@app.get("/chatgpt")
def chatgpt(request: Request, question: str):
    question = str(question).strip()
    data = ''

    def stream():
        response = openai.ChatCompletion.create(
            engine=os.getenv("CHATGPT_MODEL"),
            messages=[
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            #max_tokens=1000,
            stream=True,
            n=1,
            #top_p=1,
            #frequency_penalty=0,
            #presence_penalty=0,
        )
        for trunk in response:
            if trunk['choices'][0]['finish_reason'] is not None:
                data = '[DONE]'
            else:
                data = trunk['choices'][0]['delta'].get('content','')
            #yield "data: %s\n\n" % data.replace("\n","<br>")
            yield "%s\n\n" % data.replace("\n","<br>")

    return EventSourceResponse(stream())


uvicorn.run(app, host="0.0.0.0", port=5000)
