from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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