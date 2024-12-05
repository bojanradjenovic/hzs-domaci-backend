from flask import request, jsonify
from models import lekcija, oblast, predmet, db
from routes.auth import proveriToken, checkIfAdmin
from sqlalchemy.exc import IntegrityError
def init_delete_routes(app):
    @app.route('/deleteLekcija', methods=['POST'])
    def deleteLekcija():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401
        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401

        id_lekcije = request.form.get('id_lekcije')
        if not id_lekcije:
            return jsonify({"success": False, "message": "ID lekcije nije prosleđen"}), 400

        lekcija_obj = lekcija.query.filter_by(id_lekcije=id_lekcije).first()
        if not lekcija_obj:
            return jsonify({"success": False, "message": "Lekcija ne postoji"}), 404

        if lekcija_obj.korisnicko_ime != korisnik and not checkIfAdmin(korisnik):
            return jsonify({"success": False, "message": "Nemate dozvolu za brisanje ove lekcije"}), 403

        try:
            db.session.delete(lekcija_obj)
            db.session.commit()
            return jsonify({"success": True, "message": "Lekcija uspešno obrisana"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": e}), 500
    @app.route('/deleteOblast', methods=['POST'])
    def deleteOblast():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401
        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401

        id_oblasti = request.form.get('id_oblasti')
        if not id_oblasti:
            return jsonify({"success": False, "message": "ID oblasti nije prosleđen"}), 400

        oblast_obj = oblast.query.filter_by(id_oblasti=id_oblasti).first()
        if not oblast_obj:
            return jsonify({"success": False, "message": "Oblast ne postoji"}), 404

        if not checkIfAdmin(korisnik):
            return jsonify({"success": False, "message": "Nemate dozvolu za brisanje ove oblasti"}), 403
        try:
            db.session.delete(oblast_obj)
            db.session.commit()
            return jsonify({"success": True, "message": "Oblast uspešno obrisana"}), 200
        except IntegrityError:
            return jsonify({"success": False, "message": "Oblast je povezana sa lekcijama"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": e}), 500
    @app.route('/deletePredmet', methods=['POST'])
    def deletePredmet():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token nije prosleđen"}), 401
        korisnik = proveriToken(token)
        if not korisnik:
            return jsonify({"success": False, "message": "Nevalidan token"}), 401

        id_predmeta = request.form.get('id_predmeta')
        if not id_predmeta:
            return jsonify({"success": False, "message": "ID predmeta nije prosleđen"}), 400

        predmet_obj = predmet.query.filter_by(id_predmeta=id_predmeta).first()
        if not predmet_obj:
            return jsonify({"success": False, "message": "Predmet ne postoji"}), 404

        if not checkIfAdmin(korisnik):
            return jsonify({"success": False, "message": "Nemate dozvolu za brisanje ovog predmeta"}), 403

        try:
            db.session.delete(predmet_obj)
            db.session.commit()
            return jsonify({"success": True, "message": "Predmet uspešno obrisan"}), 200
        except IntegrityError:
            return jsonify({"success": False, "message": "Predmet je povezan sa oblastima"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": e}), 500