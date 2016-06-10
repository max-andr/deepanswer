from flask import Flask

app = Flask('DeepAnswer')
app.root_path += '/flask_app'

from flask_app import routes