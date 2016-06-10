import json

from flask import render_template, request

from flask_app import app
from src.db import DB
from src.qa import ask


@app.route('/')
@app.route('/index')
def home():
    return render_template("index.html")


@app.route('/get_answer', methods=['GET'])
def get_answer():
    question = request.args['question']
    language = request.args['language']
    return json.dumps(ask(question, language=language))


@app.route('/set_feedback', methods=['POST'])
def set_feedback():
    question = request.form['question']
    language = request.form['language']
    is_correct = request.form['isCorrect']
    DB().put_qa(question, language, is_correct)
    return json.dumps({'success': True})
