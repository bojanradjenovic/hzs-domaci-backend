from flask import request, jsonify
from models import lekcija, oblast, predmet, db
from routes.auth import proveriToken, checkIfAdmin

def init_modify_routes(app):
    @app.route('/modifyLekcija', methods=['POST'])
    def modifyLekcija():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401
        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401

        id_lekcije = request.form.get('id_lekcije')
        id_oblasti = request.form.get('id_oblasti')
        naziv = request.form.get('naziv')
        opis = request.form.get('opis')
        sadrzaj = request.form.get('sadrzaj')

        if not id_lekcije or not id_oblasti or not naziv or not opis or not sadrzaj:
            return jsonify({"success": False, "message": "Niste uneli sve podatke"}), 400

        lekcija_obj = lekcija.query.filter_by(id_lekcije=id_lekcije).first()
        if not lekcija_obj:
            return jsonify({"success": False, "message": "Lekcija ne postoji"}), 404

        if lekcija_obj.korisnicko_ime != korisnik and not checkIfAdmin(korisnik):
            return jsonify({"success": False, "message": "Nemate dozvolu za izmenu ove lekcije"}), 403

        try:
            lekcija_obj.id_oblasti = id_oblasti
            lekcija_obj.naziv = naziv
            lekcija_obj.opis = opis
            lekcija_obj.sadrzaj = sadrzaj
            db.session.commit()
            return jsonify({"success": True, "message": "Lekcija uspešno izmenjena"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": e}), 500
        
    @app.route('/modifyOblast', methods=['POST'])
    def modifyOblast():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401
        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401

        id_oblasti = request.form.get('id_oblasti')
        naziv = request.form.get('naziv')
        opis = request.form.get('opis')

        if not id_oblasti or not naziv or not opis:
            return jsonify({"success": False, "message": "Niste uneli sve podatke"}), 400

        oblast_obj = oblast.query.filter_by(id_oblasti=id_oblasti).first()
        if not oblast_obj:
            return jsonify({"success": False, "message": "Oblast ne postoji"}), 404

        if not checkIfAdmin(korisnik):
            return jsonify({"success": False, "message": "Nemate dozvolu za izmenu ove oblasti"}), 403

        try:
            oblast_obj.naziv = naziv
            oblast_obj.opis = opis
            db.session.commit()
            return jsonify({"success": True, "message": "Oblast uspešno izmenjena"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": e}), 500
    @app.route('/modifyPredmet', methods=['POST'])
    def modifyPredmet():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401
        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401

        id_predmeta = request.form.get('id_predmeta')
        naziv = request.form.get('naziv')

        if not id_predmeta or not naziv:
            return jsonify({"success": False, "message": "Niste uneli sve podatke"}), 400

        predmet_obj = predmet.query.filter_by(id_predmeta=id_predmeta).first()
        if not predmet_obj:
            return jsonify({"success": False, "message": "Predmet ne postoji"}), 404

        if not checkIfAdmin(korisnik):
            return jsonify({"success": False, "message": "Nemate dozvolu za izmenu predmeta"}), 403

        try:
            predmet_obj.naziv = naziv
            db.session.commit()
            return jsonify({"success": True, "message": "Predmet uspešno izmenjen"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": e}), 500