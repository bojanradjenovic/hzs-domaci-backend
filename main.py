from flask import Flask
from flask_cors import CORS
from models import db
import json
from routes.content_routes import init_content_routes
from routes.auth import init_auth

# Otvori config.json fajl i ucitaj config
with open("config.json") as config_file:
    config = json.load(config_file)

app = Flask(__name__)
# Cross origin resource sharing
CORS(app)
# Database konekcija
app.config['SQLALCHEMY_DATABASE_URI'] = f"mariadb+mariadbconnector://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

init_auth(app)
init_content_routes(app)

if __name__ == "__main__":
    app.run(debug=True)