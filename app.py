# from crypt import methods
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy   

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

app.app_context().push()

####################### BASE DE DATOS #################


class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_lugar = db.Column(db.Integer)
    nombre = db.Column(db.String(200))
    descripcion = db.Column(db.String(500))
    accesibilidad = db.Column(db.String(100))
    comentario = db.Column(db.String(500))
    fecha_inicio = db.Column(db.Integer)
    fecha_fin = db.Column(db.Integer)
    link = db.Column(db.String(3000))
    precio = db.Column(db.String(20))
    latitud = db.Column(db.Integer)
    longitud = db.Column(db.Integer)

    def __init__(self, id_lugar, nombre, descripcion, accesibilidad, comentario, fecha_inicio, fecha_fin, link, precio, latitud, longitud):
        self.id_lugar = id_lugar
        self.nombre = nombre
        self.descripcion = descripcion
        self.accesibilidad = accesibilidad
        self.comentario = comentario
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.link = link
        self.precio = precio
        self.latitud = latitud
        self.longitud = longitud
 


class Lugar(db.Model):
    id_lugar = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200))
    fecha_inicio = db.Column(db.String)
    fecha_fin = db.Column(db.String)
    link = db.Column(db.String(3000))
    precio = db.Column(db.String(20))
    latitud = db.Column(db.String)
    longitud = db.Column(db.String)

    def __init__(self, id_lugar, fecha_inicio, fecha_fin, link, precio, latitud, longitud):
        self.id_lugar = id_lugar
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.link = link
        self.precio = precio
        self.latitud = latitud
        self.longitud = longitud


####################### URL- ENDPOINTS #######################

@app.route('/')
def index():
    return render_template('RecorriendoPy.html')


@app.route('/showcity', methods = ['GET'])
def showcity():
    lugares = Lugar.query.all() #se crea el objeto lugares que pertenece a la clase Lugar (base de datos) y se utilliza el metodo query (para hacer un pedido a la base de datos) y se utiliza all para llamar a todos los campos de la base de datos.   
    return render_template('vista2.html', lugares=lugares)  #se utiliza return para retornar el template renderizado con render template, se indica el archivo html que va a renderizar y se declara la variable que será utilizada en el html, se le da el valor de la variable declarada en la función de la ruta. 


@app.route('/showfilters', methods = ['GET'] )
def showfilters():
    return render_template('vista3.html')

@app.route('/video', methods= ['GET'])
def video():
    return render_template('video.html')












#@app.route 

# from flask import Flask, render_template


# app = Flask(__name__)

# @app.route('/')
# def index ():
#     return render_template("index.html")

# @app.route('/showcity')
# def showcity():
#     return render_template('showcity.html')


# @app.route('/showfilters')
# def showfilters():
#     return render_template('showfilters.html')


# @app.route('/recommendme')
# def recommendme():
#     return render_template('recommendme.html')

# @app.route('/hotel')
# def hotel():
#     return render_template('hotel.html')


# if __name__ == '__main__':
















if __name__== '__main__':
    db.create_all()






