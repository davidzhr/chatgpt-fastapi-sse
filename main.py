from flask import Flask, render_template, request, session
import flask
import openai

import os
from dotenv import load_dotenv

# load_dotnev will parse the .env file and set the variables in environment automatically.
load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


# set the env variables for openai
openai.api_key = os.getenv("AZURE_API_KEY")
openai.api_version = os.getenv("OPENAI_API_VERSION")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_type = "azure"

@app.route("/chatgpt",methods=["POST","GET"])
def chatgpt():
    question = request.args.get("question","")
    question = str(question).strip()
    data = ''
    if question:
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
                print(data)
                yield "data: %s\n\n" % data.replace("\n","<br>")

        return flask.Response(stream(), mimetype="text/event-stream")

    return render_template('chatpgt.html')


app.run(host="0.0.0.0", port=5000, debug=True)
