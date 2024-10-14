from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import Column, types, func
from flask_restful import Resource, Api
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources=['*'], allow_headers=['*'], methods=['GET','POST','PUT','DELETE'])

# dialect://nombre:password@host/db
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:root@localhost/journal'

api = Api(app=app)

conexion = SQLAlchemy(app=app)

class Posteo(conexion.Model):
    id = Column(types.Integer, autoincrement=True, primary_key=True)
    title = Column(types.String(length=100), nullable=False)
    body = Column(types.String(length=500), nullable=False)
    created_at = Column(types.DateTime, server_default=func.now())  # Fecha de creación
    updated_at = Column(types.DateTime, server_default=func.now(), onupdate=func.now())  # Fecha de modificación

    __tablename__ = 'posteos'

first_request = True                
@app.before_request
def inicializador():
    global first_request
    if first_request:
        print('yo me ejecuto solo una vez')
        conexion.create_all()
        first_request = False

# Nueva ruta para mostrar el mensaje de bienvenida
@app.route('/')
def welcome():
    return "Bienvenido a tu Diario Virtual!"

class PosteoDTO(SQLAlchemyAutoSchema):
    class Meta:
        model = Posteo
        fields = ("id", "title", "body", "created_at", "updated_at")

    
class PosteoController(Resource):
    # Método para obtener un posteo por ID
    def get(self):
        posteos = conexion.session.query(Posteo).all()
        dto = PosteoDTO()
        resultado = dto.dump(posteos, many=True)
        return {
            'message': 'Entradas recuperadas exitosamente',
            'content': resultado
        }
    
    # Método para crear un posteo por ID
    def post(self):
        data = request.get_json()
        dto = PosteoDTO()
        try:
            dataValidada = dto.load(data)
            nuevoPosteo = Posteo(**dataValidada)
            conexion.session.add(nuevoPosteo)
            conexion.session.commit()
            return {
                'message': 'Posteo creado correctamente',
                'content': dto.dump(nuevoPosteo)
            }
        except Exception as e:
            return {
                'message': 'Error al crear el nuevo Posteo',
                'content': e.args
            }

class PosteoUnitarioController(Resource):
    dto = PosteoDTO()

    # Método para obtener un posteo por ID
    def get(self, id):
        posteo = conexion.session.query(Posteo).filter_by(id=id).first()
        if posteo:
            resultado = self.dto.dump(posteo)
            return {
                'message': 'Posteo recuperado exitosamente',
                'content': resultado
            }
        return {
            'message': 'Posteo no encontrado',
            'content': None
        }, 404

    # Método para actualizar un posteo por ID
    def put(self, id):
        posteo = conexion.session.query(Posteo).filter_by(id=id).first()
        if not posteo:
            return {
                'message': 'Posteo no existe'
            }, 404

        try:
            data = request.get_json()  # Obtiene los datos del cuerpo de la solicitud
            data_validada = self.dto.load(data)  # Valida y carga los datos en el DTO

            # Actualizamos los campos del posteo existente
            posteo.title = data_validada.get('title')
            posteo.body = data_validada.get('body')

            # Guardamos los cambios en la base de datos
            conexion.session.commit()

            return {
                'message': 'Posteo actualizado exitosamente',
                'content': self.dto.dump(posteo)  # Devolvemos el posteo actualizado
            }
        except Exception as e:
            return {
                'message': 'Error al actualizar el Posteo',
                'content': e.args
            }, 400


    # Método para eliminar un posteo por ID
    def delete(self, id):
        posteo = conexion.session.query(Posteo).filter_by(id=id).first()
        if not posteo:
            return {
                'message': 'Posteo no existe'
            }, 404

        try:
            # Eliminamos el posteo de la base de datos
            conexion.session.delete(posteo)
            conexion.session.commit()

            return {
                'message': 'Posteo eliminado exitosamente'
            }
        except Exception as e:
            return {
                'message': 'Error al eliminar el Posteo',
                'content': e.args
            }, 400


api.add_resource(PosteoController, '/posteos')
api.add_resource(PosteoUnitarioController, '/posteos/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)
