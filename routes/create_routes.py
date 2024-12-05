from flask import request, jsonify
from models import lekcija, oblast, predmet, db
from routes.auth import proveriToken, checkIfAdmin

def init_create_routes(app):
    @app.route('/createLekcija', methods=['POST'])
    def createLekcija():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401

        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401
        id_oblasti = request.form.get('id_oblasti')
        naziv = request.form.get('naziv')
        opis = request.form.get('opis')
        sadrzaj = request.form.get('sadrzaj')
       
        korisnicko_ime = korisnik

        if not id_oblasti or not naziv or not opis or not sadrzaj or not korisnicko_ime:
            return jsonify({"success": False, "message": "Niste uneli sve podatke"}), 400

        try:
            id_oblasti = int(id_oblasti)
        except ValueError:
            return jsonify({"success": False, "message": "ID oblasti moraju biti celi brojevi"}), 400

        nova_lekcija = lekcija(id_oblasti=id_oblasti, naziv=naziv, opis=opis, sadrzaj=sadrzaj, korisnicko_ime=korisnicko_ime)
        db.session.add(nova_lekcija)
        db.session.commit()
        return jsonify({"success": True, "message": "Uspešno dodata lekcija"}), 201
    @app.route('/createOblast', methods=['POST'])
    def createOblast():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401

        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401
        if checkIfAdmin(korisnik):
            id_predmeta = request.form.get('id_predmeta')
            naziv = request.form.get('naziv')
            opis = request.form.get('opis')
            if not id_predmeta or not naziv or not opis:
                return jsonify({"success": False, "message": "Niste uneli sve podatke"}), 400

            try:
                id_predmeta = int(id_predmeta)
            except ValueError:
                return jsonify({"success": False, "message": "ID predmeta moraju biti celi brojevi"}), 400

            nova_oblast = oblast(id_predmeta=id_predmeta, naziv=naziv, opis=opis)
            db.session.add(nova_oblast)
            db.session.commit()
            return jsonify({"success": True, "message": "Uspešno dodata oblast"}), 201
        else:
            return jsonify({"success": False, "message": "Nemate dozvolu za ovu akciju"}), 403
    @app.route('/createPredmet', methods=['POST'])
    def createPredmet():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401

        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401
        if checkIfAdmin(korisnik):
            naziv = request.form.get('naziv')
            if not naziv:
                return jsonify({"success": False, "message": "Niste uneli sve podatke"}), 400

            novi_predmet = predmet(naziv=naziv)
            db.session.add(novi_predmet)
            db.session.commit()
            return jsonify({"success": True, "message": "Uspešno dodat predmet"}), 201
        else:
            return jsonify({"success": False, "message": "Nemate dozvolu za ovu akciju"}), 403

        