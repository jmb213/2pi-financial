from os import environ
from app import app

if __name__ == '__main__':    
    app.run(host='0.0.0.0', debug=True, port=80)
    
    HOST = environ.get('SERVER_HOST', '0.0.0.0')
    PORT = 80        
    app.run(HOST, PORT)
