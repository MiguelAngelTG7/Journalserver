from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources=['*'], allow_headers=['*'], methods=['GET','POST','PUT','DELETE'])

posteos = [
   
]

@app.route('/')
def inicio():
    print('hola')
    return 'Bienvenido a mi aplicacion amigos'

@app.route('/posteos', methods=['GET', 'POST'])
def gestion_posteos():
    print(request.method)

    if request.method == 'GET':
        return{
            'content': posteos
        }
    elif request.method == 'POST':
        print(request.get_json())
        data = request.get_json()
        
        posteos.append(data)

        return {
            'message': 'Producto creado exitosamente'
       }

    return {
        'content': posteos
    }

@app.route('/posteos/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def gestion_posteo(id):
    
    if request.method=='GET':
        limite = len(posteos)
        if limite < id:
            return {
                'message': 'El producto no existe'
            }
        else: 
            return {
                'content': posteos[id]
            } 
    
    elif request.method=='PUT':
        limite = len(posteos)
        if limite < id:
            return {
                'message': 'El producto no existe'
            }
        else:
            data = request.get_json()
            posteos[id] = data
            return {
                'message': 'Producto actualizado exitosamente'
        } 
    
    elif request.method=='DELETE':
        limite = len(posteos)
        if limite < id:
            return {
                'message': 'El producto no existe'
            }
        else:
            del posteos[id]
            return {
                'message': 'Prodcuto eliminado exitosamente'
        } 



if __name__ == '__main__':
    app.run(debug=True)