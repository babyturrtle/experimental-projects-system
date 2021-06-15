from flask import Flask
from flaskext.mysql import MySQL


app = Flask(__name__, template_folder='templates')
app.add_url_rule("/", endpoint="index")


""" MySQL Database Configuration """

db = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'experimental-projects'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

db.init_app(app)

if __name__ == "__main__":
    app.run()