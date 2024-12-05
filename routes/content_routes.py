from flask import request, jsonify
from models import lekcija, oblast, predmet
from routes.auth import proveriToken

def init_content_routes(app):
    @app.route('/getLekcije')
    def getLekcije():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401

        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401

        id_oblasti = request.args.get('id_oblasti')
        if not id_oblasti:
            return jsonify({"success": False, "message": "ID oblasti nije prosleđen"}), 400
        try:
            id_oblasti = int(id_oblasti)
        except ValueError:
            return jsonify({"success": False, "message": "ID oblasti mora biti ceo broj"}), 400
        
        sve_lekcije = lekcija.query.filter_by(id_oblasti=id_oblasti).all()
        
        
        json_data = [{
            "id_lekcije": lekcija.id_lekcije,
            "naziv": lekcija.naziv,
            "opis": lekcija.opis,
            "sadrzaj": lekcija.sadrzaj,
            "id_oblasti": lekcija.id_oblasti,
            "korisnicko_ime": lekcija.korisnicko_ime
        } for lekcija in sve_lekcije]
        
        return jsonify({"success": True, "korisnicko_ime": korisnik, "lekcije": json_data}), 200

    @app.route('/getOblasti')
    def getOblasti():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401

        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401

        id_predmeta = request.args.get('id_predmeta')
        
        if not id_predmeta:
            return jsonify({"success": False, "message": "ID predmeta nije prosleđen"}), 400

        try:
            id_predmeta = int(id_predmeta)
        except ValueError:
            return jsonify({"success": False, "message": "ID predmeta mora biti ceo broj"}), 400
        predmet_record = predmet.query.get(id_predmeta)
        if not predmet_record:
            return jsonify({"error": "Predmet nije pronađen"}), 404
        
        sve_oblasti = oblast.query.filter_by(id_predmeta=id_predmeta).all()
        
        json_data = [{
            "id_oblasti": o.id_oblasti,
            "naziv": o.naziv,
            "opis": o.opis,
        } for o in sve_oblasti]
        
        return jsonify({"success": True, "korisnicko_ime": korisnik, "oblasti": json_data}), 200

    @app.route('/getPredmeti')
    def getPredmeti():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401

        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401

        svi_predmeti = predmet.query.all()
        json_data = [{
            "id_predmeta": predmet.id_predmeta,
            "naziv": predmet.naziv
        } for predmet in svi_predmeti]
        return jsonify({"success": True, "korisnicko_ime": korisnik, "predmeti": json_data}), 200
    @app.route('/getLekcija')
    def getLekcija():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401

        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401

        id_lekcije = request.args.get('id_lekcije')
        if not id_lekcije:
            return jsonify({"success": False, "message": "ID lekcije nije prosleđen"}), 400
        try:
            id_lekcije = int(id_lekcije)
        except ValueError:
            return jsonify({"success": False, "message": f"ID lekcije mora biti ceo broj, {id_lekcije}"}), 400
        
        sve_lekcije = lekcija.query.filter_by(id_lekcije=id_lekcije).all()
        
        if not sve_lekcije:
            return jsonify({"success": False, "message": "Ne postoji lekcija sa tim ID-em!"}), 404
        
        json_data = [{
            "id_lekcije": lekcija.id_lekcije,
            "naziv": lekcija.naziv,
            "opis": lekcija.opis,
            "sadrzaj": lekcija.sadrzaj,
            "id_oblasti": lekcija.id_oblasti,
            "korisnicko_ime": lekcija.korisnicko_ime
        } for lekcija in sve_lekcije]
        
        return jsonify({"success": True, "korisnicko_ime": korisnik, "lekcija": json_data[0]}), 200
