from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
import bcrypt
import time
import secrets
from datetime import datetime
from flask_cors import CORS

# Otvori config.json fajl i ucitaj config
with open("config.json") as config_file:
    config = json.load(config_file)

app = Flask(__name__)
# Cross origin resource sharing
CORS(app)
# Database konekcija
app.config['SQLALCHEMY_DATABASE_URI'] = f"mariadb+mariadbconnector://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model za korisnike
class korisnici(db.Model):
    korisnicko_ime = db.Column(db.String(255), nullable=False, primary_key=True)
    sifra = db.Column(db.LargeBinary, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

# Model za lekcije
class lekcija(db.Model):
    id_lekcije = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(255), nullable=False)
    opis = db.Column(db.String(255), nullable=False)
    sadrzaj = db.Column(db.Text, nullable=False)
    glasovi = db.Column(db.Integer, nullable=False)
    prihvacena = db.Column(db.Boolean)
    korisnicko_ime = db.Column(db.String(255), db.ForeignKey('korisnici.korisnicko_ime'), nullable=False)
    id_oblasti = db.Column(db.BigInteger, db.ForeignKey('oblast.id_oblasti'), nullable=False)

# Model za oblasti
class oblast(db.Model):
    id_oblasti = db.Column(db.BigInteger, primary_key=True)
    naziv = db.Column(db.String, nullable=False)
    opis = db.Column(db.String)
    id_predmeta = db.Column(db.Integer, db.ForeignKey('predmet.id_predmeta'), nullable=False)
    lekcije = db.relationship('lekcija', backref='oblast', lazy=True)

# Model za predmete
class predmet(db.Model):
    id_predmeta = db.Column(db.BigInteger, primary_key=True)
    naziv = db.Column(db.String, nullable=False)
    oblasti = db.relationship('oblast', backref='predmet', lazy=True)

# Model za korisnici_tokens
class korisnici_tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    korisnicko_ime = db.Column(db.String(255), db.ForeignKey('korisnici.korisnicko_ime'), nullable=False)
    token = db.Column(db.String(255), nullable=False)

def proveriToken(token):
    token = korisnici_tokens.query.filter_by(token=token).first()
    if token:
        return token.korisnicko_ime
    return False

@app.route('/napraviLekciju', methods=['POST'])
def napraviLekciju():
    id_lekcije = request.form['id_lekcije']
    naziv = request.form['naziv']
    opis = request.form['opis']
    sadrzaj = request.form['sadrzaj']
    glasovi = request.form['glasovi']
    id_oblasti = request.form['id_oblasti']
    korisnicko_ime = request.form['korisnicko_ime']
    postojeca_lekcija = lekcija.query.filter_by(id_lekcije=id_lekcije).first()
    if postojeca_lekcija:
         return jsonify({"success": False, "message": "Lekcija sa tim id-em imenom vec postoji"}), 400
    nova_lekcija = lekcija(
        id_lekcije=id_lekcije,
        naziv = naziv,
        opis = opis,
        sadrzaj = sadrzaj,
        glasovi = glasovi,
        id_oblasti = id_oblasti,
        korisnicko_ime =korisnicko_ime
    )
    db.session.add(nova_lekcija)
    db.session.commit()
    return jsonify({"success": True, "message": "Lekcija uspesno kreirana"}), 201

@app.route('/kreirajOblast', methods=['POST'])
def kreirajOblast():
    id_oblasti = request.form['id_oblasti']
    naziv = request.form['naziv']
    opis = request.form['opis']
    id_predmeta = request.form['id_predmeta']
    postojeca_oblast = oblast.query.filter_by(id_oblasti=id_oblasti).first()
    if postojeca_oblast:
        return jsonify({"success": False, "message": "Oblast sa tim id-em imenom vec postoji"}), 400
    nova_oblast = oblast(
        id_oblasti = id_oblasti,
        naziv = naziv,
        opis = opis,
        id_predmeta = id_predmeta
    )
    db.session.add(nova_oblast)
    db.session.commit()
    return jsonify({"success": True, "message": "Oblast uspesno kreirana"}), 201


@app.route('/registerKorisnik', methods=['POST'])
def registerKorisnik():
    korisnicko_ime = request.form['korisnicko_ime']
    sifra = request.form['sifra']
    postojeci_korisnik = korisnici.query.filter_by(korisnicko_ime=korisnicko_ime).first()
    if postojeci_korisnik:
        return jsonify({"success": False, "message": "Korisnik sa tim korisnickim imenom vec postoji"}), 400
    hashed_password = bcrypt.hashpw(sifra.encode('utf-8'), bcrypt.gensalt())
    novi_korisnik = korisnici(korisnicko_ime=korisnicko_ime, is_admin=False, sifra=hashed_password)
    db.session.add(novi_korisnik)
    db.session.commit()
    return jsonify({"success": True, "message": "Korisnik uspesno registrovan"}), 201

@app.route('/loginKorisnik', methods=['POST'])
def loginKorisnik():
    try:
        korisnicko_ime = request.form.get('korisnicko_ime')
        sifra = request.form.get('sifra')
        
        if not korisnicko_ime or not sifra:
            return jsonify({"success": False, "message": "Nedostaju podaci"}), 400
        
        korisnik = korisnici.query.filter_by(korisnicko_ime=korisnicko_ime).first()
        
        if korisnik and bcrypt.checkpw(sifra.encode('utf-8'), korisnik.sifra):
            token = secrets.token_hex(32)
            novi_token = korisnici_tokens(korisnicko_ime=korisnicko_ime, token=token)
            db.session.add(novi_token)
            db.session.commit()
            return jsonify({"success": True, "token": novi_token.token}), 200
        else:
            time.sleep(2) 
            return jsonify({"success": False, "message": "Pogrešno korisničko ime ili šifra"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/logoutKorisnik')
def logoutKorisnik():
    token = request.args.get('token')
    token = korisnici_tokens.query.filter_by(token=token).first()
    if token:
        db.session.delete(token)
        db.session.commit()
        return jsonify({"success": True, "message": "Uspesno izlogovan"}), 200
    return jsonify({"success": False, "message": "Neuspesno izlogovan"}), 400

@app.route('/getLekcije')
def getLekcije():
    id_oblasti = request.args.get('id_oblasti')
    if not id_oblasti:
        return jsonify({"success": False, "message": "ID oblasti nije prosleđen"}), 400
    try:
        id_oblasti = int(id_oblasti)
    except ValueError:
        return jsonify({"success": False, "message": "ID oblasti mora biti ceo broj"}), 400
    
    sve_lekcije = lekcija.query.filter_by(id_oblasti=id_oblasti).all()
    
    if not sve_lekcije:
        return jsonify({"success": False, "message": "Nema lekcija za ovu oblast"}), 404
    
    json_data = [{
        "id_lekcije": lekcija.id_lekcije,
        "naziv": lekcija.naziv,
        "opis": lekcija.opis,
        "sadrzaj": lekcija.sadrzaj,
        "glasovi": lekcija.glasovi,
        "id_oblasti": lekcija.id_oblasti,
        "korisnicko_ime": lekcija.korisnicko_ime
    } for lekcija in sve_lekcije]
    
    return jsonify(json_data), 200

@app.route('/getOblasti')
def getOblasti():
    id_predmeta = request.args.get('id_predmeta')
    
    if not id_predmeta:
        return jsonify({"success": False, "message": "ID predmeta nije prosleđen"}), 400

    try:
        id_predmeta = int(id_predmeta)
    except ValueError:
        return jsonify({"success": False, "message": "ID predmeta mora biti ceo broj"}), 400
    
    predmet_record = predmet.query.get(id_predmeta)
    
    if not predmet_record:
        return jsonify({"success": False, "message": "Predmet nije pronađen"}), 404
    
    sve_oblasti = oblast.query.filter_by(id_predmeta=id_predmeta).all()
    
    json_data = [{
        "id_oblasti": o.id_oblasti,
        "naziv": o.naziv,
        "opis": o.opis,
    } for o in sve_oblasti]
    
    return jsonify(json_data), 200

@app.route('/getPredmeti')
def getPredmeti():
    svi_predmeti = predmet.query.all()
    json_data = [{
        "id_predmeta": predmet.id_predmeta,
        "naziv": predmet.naziv
    } for predmet in svi_predmeti]
    return jsonify(json_data), 200

@app.route('/getKorisnici')
def getKorisnici():
    svi_korisnici = korisnici.query.all()
    return jsonify({
        "korisnici": [korisnik.korisnicko_ime for korisnik in svi_korisnici],
        "admini": [korisnik.korisnicko_ime for korisnik in svi_korisnici if korisnik.is_admin]
    }), 200

@app.route('/tokenProvera')
def tokenProvera():
    token = request.args.get('token')
    korisnik = proveriToken(token)
    if korisnik:
        return jsonify({"success": True, "korisnik": korisnik}), 200
    return jsonify({"success": False, "message": "Nevalidan token"}), 401

if __name__ == "__main__":
    app.run(debug=True)