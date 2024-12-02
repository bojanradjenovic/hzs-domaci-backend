from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json

# Otvori config.json fajl i ucitaj config
with open("config.json") as config_file:
    config = json.load(config_file)

app = Flask(__name__)

# Database konekcija
app.config['SQLALCHEMY_DATABASE_URI'] = f"mariadb+mariadbconnector://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model za korisnike
class korisnici(db.Model):
    id_korisnika = db.Column(db.Integer, primary_key=True)
    korisnicko_ime = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

@app.route('/getKorisnici')
def getKorisnici():
    #dodati proveru autha, ovo je samo test
    svi_korisnici = korisnici.query.all()
    return f"Korisnici: {[korisnik.korisnicko_ime for korisnik in svi_korisnici]}, Admins: {[korisnik.korisnicko_ime for korisnik in svi_korisnici if korisnik.is_admin]}"

if __name__ == "__main__":
    app.run(debug=True)
