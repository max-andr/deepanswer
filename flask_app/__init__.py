import os

import jinja2
from flask import Flask

app = Flask('DeepAnswer') #, template_folder=template_dir) #, static_url_path=static_dir)
app.root_path += '/flask_app'

from flask_app import views