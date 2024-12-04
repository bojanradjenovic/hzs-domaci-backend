from flask import request, jsonify
from models import db, korisnici, korisnici_tokens
import bcrypt
import time
import secrets
from sqlalchemy.exc import IntegrityError
def init_auth(app):
    @app.route('/registerKorisnik', methods=['POST'])
    def registerKorisnik():
        korisnicko_ime = request.form['korisnicko_ime']
        sifra = request.form['sifra']
        try:
            hashed_sifra = bcrypt.hashpw(sifra.encode('utf-8'), bcrypt.gensalt())
            novi_korisnik = korisnici(korisnicko_ime=korisnicko_ime, is_admin=False, sifra=hashed_sifra)
            db.session.add(novi_korisnik)
            db.session.commit()
            return jsonify({"success": True, "message": "Korisnik uspešno registrovan"}), 201
        except IntegrityError:
            return jsonify({"success": False, "message": "Korisničko ime već postoji"}), 400
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
        

    @app.route('/loginKorisnik', methods=['POST'])
    def loginKorisnik():
        try:
            korisnicko_ime = request.form.get('korisnicko_ime')
            sifra = request.form.get('sifra')
            
            if not korisnicko_ime or not sifra:
                return jsonify({"success": False, "message": "Nedostaju podaci."}), 400
            
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
        token = request.headers.get('Authorization')
        token = korisnici_tokens.query.filter_by(token=token).first()
        if token:
            db.session.delete(token)
            db.session.commit()
            return jsonify({"success": True, "message": "Uspešno izlogovan"}), 200
        return jsonify({"success": False, "message": "Neuspešno izlogovan"}), 400

    @app.route('/tokenProvera')
    def tokenProvera():
        token = request.args.get('token')
        korisnik = proveriToken(token)
        if korisnik:
            return jsonify({"success": True, "korisnik": korisnik}), 200
        return jsonify({"success": False, "message": "Nevalidan token"}), 401
def proveriToken(token):
    token = korisnici_tokens.query.filter_by(token=token).first()
    if token:
        return token.korisnicko_ime
    return False
