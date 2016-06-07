from flask import render_template, flash, url_for, request, session, \
    redirect, abort
from urllib.parse import quote
from flask_app import app
from src.qa import ask


@app.route('/')
@app.route('/index')
def home():
    print(app.template_folder)
    print(app.jinja_loader.list_templates())
    return render_template("index.html")
# """
# <head>
#   <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.2.2/jquery.min.js"></script>
# </head>
# <body>
# <h1>Hello world!</h1>
# </body>
# """

@app.route('/get_answer', methods=['GET'])
def get_answer():
    question = request.args['question']
    language = request.args['language']
    return ask(question, language=language)