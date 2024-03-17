from flask import Flask,request,jsonify
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import binascii
import datetime
from colorama import Fore
import os


def print_ascii_art():
    logo = f"""{Fore.MAGENTA}
 █████    ██████    █████   ██     ██      ██████    █████          ██          ██       █████
██       ██    ██  ██      ██ ██  ██ ██   ██    ██  ██              ██        ██  ██    ██
██       ██    ██   ████   ██   ██   ██   ██    ██   ████   ██████  ██       ██    ██    ████
██       ██    ██      ██  ██        ██   ██    ██      ██          ██       ██ ██ ██       ██
 █████    ██████   █████   ██        ██    ██████   █████            ██████  ██    ██   █████
"""
    by = f"""{Fore.CYAN}                                     Por Nicolás Rodríguez Torres"""
    print(logo)   
    print(by)
    

app = Flask(__name__)

def clear():
  if os.name == "nt":
    os.system("cls")
  else:
    os.system("clear")
#crea el cliente de azure 
def create_client(host,master_key):
        client = cosmos_client.CosmosClient(host, {'masterKey': master_key}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
        return client
   
#crea el cliente o lo trae si ya existe
def get_container(db,name):
    try: 
        container = db.create_container(id=name, partition_key=PartitionKey(path='/partitionKey'))
    except exceptions.CosmosResourceExistsError as e:
        container = db.get_container_client(name)
    return container
#ferifica si no existe el item ya y lo añade
def add_item(container,name,data,partition):
    try:
        dataS = {
            'id' : name,
            'partitionKey' : partition,
            'date' : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data' : data
        }
        container.create_item(body=dataS)
        return True
    except exceptions.CosmosResourceExistsError as e:
        return False
    
@app.route('/create_database',methods=['POST'])
def create_database():
    data = request.get_json()
    HOST = data.get('host')
    MASTER_KEY = data.get('A-key')
    DATABASE_ID = data.get('name_Db')
    try:
    # 
    # aqui se creal el cliente que es la puerta de entrada a la base de datos 
      client = create_client(HOST,MASTER_KEY)
    # con esa misma puerta de entrada se hace un llamado a la base de datos y se guarad en esa variable db
      #print("si pasa")
      try:
         # print("netra")
          db = client.create_database(DATABASE_ID) 
          #print("LA crea")
      except exceptions.CosmosResourceExistsError as e:
           return jsonify({'error': 'Ya esta creada esa base de datos'
                      })
         # print("La trae")
      return jsonify({'response': 'Ya tienes la base de datos crack! ;) solo falta agregar los datos'
                      ,'database_ID': db.id,
                      'client_ID' : id(client)
                      })
    except exceptions.CosmosHttpResponseError as e:
      return jsonify({'error': 'Ocurrio un error :(, datos erroneos o problemas del servidor',
                      'details': str(e)})
    except binascii.Error as e:
        return jsonify({
            'error' : str(e) 
        })
    
  #se obtiene las lista de las bases de datos con el cliente y un metodo incorporado de azure cosmos que se
    # llama list databases y se almacena el resultado en una lista de python pra luego recorrerla y procesar los datos  
@app.route('/list_databases',methods=['GET'])
def list_databases():

    cont = 0
    list = {}
    data = request.get_json()
    HOST = data.get('host')
    MASTER_KEY = data.get('A-key')
    try:
       client =  create_client(HOST,MASTER_KEY)
       list_db = client.list_databases()
       #se valida que la lista no venga vacia
       if list_db:             
            for item in list_db:
                  cont += 1
                  print(item)
                  list[f'database_{cont}'] = {'data':item}            
            return jsonify({
                'response' : list,
                'status' : 200
            })
       else:
            return jsonify({'error':'No tienes bases de datos creadas'})
       #se tratan dos errores, los errores de servidor, y los errores de binascci que son errores,
       #en los datos introducidos para la uetnticacion como falta de datos en la A-key
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({
           'error':str(e),
           'status':500
        })
    except binascii.Error as e:
        return jsonify({
            'error' : str(e) 
            ,'status': 500
        })
    
@app.route('/list_containers',methods=['GET'])
def list_containers():
     listC = {}
     cont = 0
     data = request.get_json()
     HOST = data.get('host')
     MASTER_KEY = data.get('A-key')
     DATABASE_ID = data.get('name_Db')
     try:
         client = create_client(HOST,MASTER_KEY)
         db = client.get_database_client(DATABASE_ID)
         list_cont = list(db.list_containers())
         print(list_cont)
         if list_cont:
             for item in list_cont:
                 cont += 1
                 listC[f'container_{cont}'] = {'data':item}
             return jsonify({'response': listC,
                             'status': 200})
         else:
             return jsonify({'error': f'No hay contenedores en la base de datos {DATABASE_ID}',
                             'status':404})
          # se tratan dos tipos de errores, para ser más específicos en la respuesta, los errores de servidor,
        #y los errores 404 de notFound
     except exceptions.CosmosResourceNotFoundError as e:
         return jsonify({'error':str(e),
                         'status':404})
     except exceptions.CosmosHttpResponseError as e:
         return jsonify({'error':str(e),
                         'status':500})

#con este servicio se puede obtener los items de un contenedor en específico, y datos sobre los items
@app.route('/list_items',methods=['GET'])
def list_items():
     listI = {}
     cont = 0
     data = request.get_json()
     HOST = data.get('host')
     MASTER_KEY = data.get('A-key')
     DATABASE_ID = data.get('name_Db')
     name_container = data.get('container')
     try:
         client = create_client(HOST,MASTER_KEY)
         db = client.get_database_client(DATABASE_ID)
         container = db.get_container_client(name_container)
         list_item = container.read_all_items()       
         for item in list_item:
                 cont += 1
                 listI[f'item_{cont}'] ={'data': item}
         return jsonify({
                 'response': listI,
                  'status':200
             })
          # se tratan dos tipos de errores, para ser más específicos en la respuesta, los errores de servidor,
        #y los errores 404 de notFound
     except exceptions.CosmosResourceNotFoundError as e:
         return jsonify({
                 'erro':str(e),
                  'status':404
             })
     except exceptions.CosmosHttpResponseError as e:
         return jsonify({
                 'error': str(e),
                  'status':500
             })
             
#en este metodo se trae un item en específico simlplemente se lee
@app.route('/get_item',methods=['GET'])
def get_item():
    data = request.get_json()
    HOST = data.get('host')
    MASTER_KEY = data.get('A-key')
    DATABASE_ID = data.get('name_Db')
    name = data.get('container')
    name_item = data.get('name_item')
    partition = data.get('partition')
    try:
        client = create_client(HOST,MASTER_KEY)
        db = client.get_database_client(DATABASE_ID)
        container = db.get_container_client(name)
        item = container.read_item(name_item,partition)
        return jsonify(
            {
                'response':item,
                'status':200
            }
        )
    #como en los demás servicios de lectura, se tratan dos tipos de errores para asi tener más,
    #control sobre estos, el error notfound y el erro de servidor
    except exceptions.CosmosResourceNotFoundError as e:
        return jsonify(
            {
                'error':str(e),
                'status':404
            }
        )
    except exceptions.CosmosHttpResponseError as e:
        return jsonify(
            {
                'error':str(e),
                'status':500
            }
        )
#crear item, primero se crea o se llama al cliente, luego se crea o se llama el contenedor, y por ultimo,
#se crea el item, cabe mencionar que antes de crear el item se verifica que este no exista
@app.route('/create_item',methods=['POST'])
def create_item():
    data = request.get_json()
    HOST = data.get('host')
    MASTER_KEY = data.get('A-key')
    DATABASE_ID = data.get('name_Db')
    name = data.get('container')
    name_item = data.get('name_item')
    objectI = data.get('item')
    partition = data.get('partition')
    try:
        client = create_client(HOST,MASTER_KEY)
        db = client.get_database_client(DATABASE_ID)
        container = get_container(db,name)
        item = add_item(container,name_item,objectI,partition)
        if item :
            return jsonify({
           'status' : 200,
           'response' : 'El item '+name_item +" fue creado con exito",
           'item' : objectI
           })
        else:
            return jsonify({
                'error':'El item ya existe'
            })
       
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({'error':str(e),
                        'status':500})
    
    except binascii.Error as e:
        return jsonify({
            'error' : str(e),
            'status':500 
        })

#delete 
    #con este servicio se puede eliminar el contenedor especificado
@app.route('/delete_container',methods=['DELETE'])
def delete_container():
    data = request.get_json()
    HOST = data.get('host')
    MASTER_KEY = data.get('A-key')
    DATABASE_ID = data.get('name_Db')
    name = data.get('container')
    try:
        client = create_client(HOST,MASTER_KEY)
        db = client.get_database_client(DATABASE_ID)
        db.delete_container(name)
        return jsonify({
        'status' : 200,
        'response' : f'El contenedor {name} fue eliminado'
         })
#se tratan tambien dos tipos de errores para tener más control de estos
    except exceptions.CosmosResourceNotFoundError as e:
        return jsonify({
            'error':str(e),
            'status' :404
        })
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({
            'error':str(e),
            'status' :500
        })
@app.route('/delete_item',methods = ['DELETE'])
def delete_it():
    data = request.get_json()
    HOST = data.get('host')
    MASTER_KEY = data.get('A-key')
    DATABASE_ID = data.get('name_Db')
    name = data.get('container')
    name_item = data.get('name_item')
    partition = data.get('partition')
    try:
        client = create_client(HOST,MASTER_KEY)
        db = client.get_database_client(DATABASE_ID)
        container = db.get_container_client(name)
        container.delete_item(name_item,partition)
        return jsonify({
            'status' : 200,
            'response' :f'El item {name_item} fue eliminado'
        })
     #se tratan tambien dos tipos de errores para tener más control de estos
    except exceptions.CosmosResourceNotFoundError as e:
        return jsonify({
            'error':str(e),
            'status' :404
        })
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({
            'error':str(e),
            'status' :500
        })


    #con este servicio se pueden eliminar las bases de datos, con solo el nombre y las credenciales de cliente azure
@app.route('/delete_database',methods=['DELETE'])
def delete_database():
    data = request.get_json()
    HOST = data.get('host')
    MASTER_KEY = data.get('A-key')
    DATABASE_ID = data.get('name_Db')
    try:
        client = create_client(HOST,MASTER_KEY)
        client.delete_database(DATABASE_ID)
        return jsonify({
            'status':200,
            'response':f'La base de datos {DATABASE_ID} ha sido eliminada'
        })
    #se tratan tambien dos tipos de errores para tener más control de estos
    except exceptions.CosmosResourceNotFoundError as e:
        return jsonify({
            'error':f'La base de datos {DATABASE_ID} no existe',
            'status' :404
        })
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({
            'error':str(e),
            'status' :500
        })
    #con este servico se borra el contenedor especificado en le header, solo se borra uno a la vez
if __name__ == '__main__':
    clear()
    print_ascii_art()  
    url=f"""{Fore.GREEN} UrlApi: http://127.0.0.1:5000"""
    print(url)
    app.run(debug=True)
    
