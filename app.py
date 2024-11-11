from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app= Flask (__name__)

#Configuracion de la base de datos SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db= SQLAlchemy(app)

#Modelo de la tabla LOG

class Log(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    fecha_y_hora= db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

#Crear la tabla si no existe 
with app.app_context():
    db.create_all()


#Funcion para ordenar los registros por fecha y hora 
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda X: X.fecha_y_hora, reverse=True)

@app.route('/')
def index():
    #Obtener todos los registros de la BD
    registros = Log.query.all()
    registros_odrdenados=ordenar_por_fecha_y_hora(registros)
    return render_template('index.html', registros=registros_odrdenados)

mensajes_log=[]
#Funcion para agregar mensjaes y guardar en la BD

def agregar_mensajes_log(texto):
    mensajes_log.append(texto)

    #Guardar el mesaje en la BD

    nuevo_registro= Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

#Token de verificación para la configurción

TOKEN_MANUEL= "Manuel23"

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method== 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method== 'POST':
        response = recibir_mensajes(request)
        return response

def verificar_token(req):
    token=req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_MANUEL:
        return challenge
    else:
        return jsonify({'error': 'Token invalido'}),401


def recibir_mensajes(req):

    try:
        req = request.get_json()
        entry = request.get_json() 
        changes = entry ['changes'] [0]
        value = changes['value']
        objeto_mensaje = value ['message']
        
        agregar_mensajes_log(objeto_mensaje)



        return jsonify({'message':'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED'})


if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
