# #!flask/bin/python
#
# from src.__init__ import app
#
# app.run(port=5009, debug=True)
#
#

#!flask/bin/python
from flask_app import app


app.config.update(dict(
    # DATABASE_STRING = 'dbname=animal_db user=postgres password=root',
    # DEBUG = True,
    # SECRET_KEY = 'development key',
    # USERNAME = 'max',
    # PASSWORD = 'root'
))

app.config.from_object(__name__)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')