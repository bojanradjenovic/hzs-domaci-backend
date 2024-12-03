from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import json
import bcrypt
import time
import secrets
from datetime import datetime
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
    korisnicko_ime = db.Column(db.String(255), nullable=False, primary_key=True)
    sifra = db.Column(db.LargeBinary, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

#Model za lekcije
class lekcija(db.Model):
    id_lekcije = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(255), nullable=False)
    opis = db.Column(db.String(255), nullable=False)
    sadrzaj = db.Column(db.Text, nullable=False)
    glasovi = db.Column(db.Integer, nullable=False)
    prihvacena = db.Column(db.Boolean)
    korisnicko_ime = db.Column(db.String(255), db.ForeignKey('korisnik.korisnicko_ime'), nullable=False)
    id_oblasti = db.Column(db.BigInteger, db.ForeignKey('oblast.id_oblasti'), nullable=False)

#Model za oblasti
class oblast(db.Model):
    id_oblasti = db.Column(db.BigInteger, primary_key=True)
    naziv = db.Column(db.String, nullable=False)
    opis = db.Column(db.String)
    id_predmeta = db.Column(db.Integer, db.ForeignKey('predmet.id_predmeta'), nullable=False)
    lekcije = db.relationship('lekcija', backref='oblast', lazy=True)

#Model za predmete
class predmet(db.Model):
    id_predmeta = db.Column(db.BigInteger, primary_key=True)
    naziv = db.Column(db.String, nullable=False)
    oblasti = db.relationship('oblast', backref='predmet', lazy=True)
#Model za korisnici_tokens
class korisnici_tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    korisnicko_ime = db.Column(db.String(255), db.ForeignKey('korisnici.korisnicko_ime'), nullable=False)
    token = db.Column(db.String(255), nullable=False)

def proveriToken(token):
    token = korisnici_tokens.query.filter_by(token=token).first()
    if token:
        return token.korisnicko_ime
    return False

@app.route('/registerKorisnik', methods=['POST'])
def registerKorisnik():
    #dodati proveru za sifru, tj. password requirements
    korisnicko_ime = request.form['korisnicko_ime']
    sifra = request.form['sifra']
    postojeci_korisnik = korisnici.query.filter_by(korisnicko_ime=korisnicko_ime).first()
    if postojeci_korisnik:
        return json.dumps({"success": False, "message": "Korisnik sa tim korisnickim imenom vec postoji"})
    hashed_password = bcrypt.hashpw(sifra.encode('utf-8'), bcrypt.gensalt())
    novi_korisnik = korisnici(korisnicko_ime=korisnicko_ime, is_admin=False, sifra=hashed_password)
    db.session.add(novi_korisnik)
    db.session.commit()
    return json.dumps({"success": True, "message": "Korisnik uspesno registrovan"})
@app.route('/loginKorisnik', methods=['POST'])
def loginKorisnik():
    korisnicko_ime = request.form['korisnicko_ime']
    sifra = request.form['sifra']
    korisnik = korisnici.query.filter_by(korisnicko_ime=korisnicko_ime).first()
    if korisnik and bcrypt.checkpw(sifra.encode('utf-8'), korisnik.sifra):
        token = secrets.token_hex(32)
        novi_token = korisnici_tokens(korisnicko_ime=korisnicko_ime, token=token)
        db.session.add(novi_token)
        db.session.commit()
        return json.dumps({"success": True, "token": novi_token.token})
    else:
        time.sleep(2)
        return json.dumps({"success": False, "message": "Pogresno korisnicko ime ili lozinka"})

@app.route('/logoutKorisnik')
def logoutKorisnik():
    token = request.args.get('token')
    token = korisnici_tokens.query.filter_by(token=token).first()
    if token:
        db.session.delete(token)
        db.session.commit()
        return json.dumps({"success": True, "message": "Uspesno izlogovan"})
    return json.dumps({"success": False, "message": "Neuspesno izlogovan"})

@app.route('/getLekcije')
def getLekcije():
    #dodati da zapravo radi nesto
    sve_lekcije = lekcija.query.all()
    return f"lekcije: {[lekcija.id_korisnika for lekcija in sve_lekcije]}"

@app.route('/getKorisnici')
def getKorisnici():
    #dodati auth da mogu samo admini da vide sve korisnike	
    svi_korisnici = korisnici.query.all()
    return json.dumps({
        "korisnici": [korisnik.korisnicko_ime for korisnik in svi_korisnici],
        "admini": [korisnik.korisnicko_ime for korisnik in svi_korisnici if korisnik.is_admin]
    })
@app.route('/tokenProvera')
def tokenProvera():
    token = request.args.get('token')
    korisnik = proveriToken(token)
    if korisnik:
        return json.dumps({"success": True, "korisnik": korisnik})
    return json.dumps({"success": False, "message": "Nevalidan token"})

if __name__ == "__main__":
    app.run(debug=True)
