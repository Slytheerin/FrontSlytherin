from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

app.app_context().push()

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_lugar = db.Column(db.String(200))
    descripcion = db.Column(db.String(500))
    accesibilidad = db.Column(db.String(100))
    costo = db.Column(db.Integer)
    comentario = db.column(db.String(500))
        
@app.route('/')
def index():
    return render_template('index.html')

if __name__== '__main__':
    db.create_all()
