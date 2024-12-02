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
    korisnicko_ime = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

class lekcija(db.Model):
    id_lekcije = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(255), nullable=False)
    opis = db.Column(db.String(255), nullable=False)
    sadrzaj = db.Column(db.Text, nullable=False)
    glasovi = db.Column(db.Integer, nullable=False)
    prihvacena = db.Column(db.Boolean)
    id_korisnika = db.Column(db.BigInteger, db.ForeignKey('korisnik.id_korisnika'), nullable=False)
    id_oblasti = db.Column(db.BigInteger, db.ForeignKey('oblast.id_oblasti'), nullable=False)

class oblast(db.Model):
    id_oblasti = db.Column(db.BigInteger, primary_key=True)
    naziv = db.Column(db.String, nullable=False)
    opis = db.Column(db.String)
    id_predmeta = db.Column(db.Integer, db.ForeignKey('predmet.id_predmeta'), nullable=False)
    lekcije = db.relationship('lekcija', backref='oblast', lazy=True)

class predmet(db.Model):
    id_predmeta = db.Column(db.BigInteger, primary_key=True)
    naziv = db.Column(db.String, nullable=False)
    oblasti = db.relationship('oblast', backref='predmet', lazy=True)

@app.route('/getLekcije')
def getLekcije():
    sve_lekcije = lekcija.query.all()
    return f"lekcije: {[lekcija.id_korisnika for lekcija in sve_lekcije]}"

@app.route('/getKorisnici')
def getKorisnici():
    #dodati proveru autha, ovo je samo test
    svi_korisnici = korisnici.query.all()
    return f"Korisnici: {[korisnik.korisnicko_ime for korisnik in svi_korisnici]}, Admins: {[korisnik.korisnicko_ime for korisnik in svi_korisnici if korisnik.is_admin]}"

if __name__ == "__main__":
    app.run(debug=True)
