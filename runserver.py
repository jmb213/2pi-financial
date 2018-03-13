from os import environ
from app import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', '0.0.0.0')
    PORT = environ.get('SERVER_PORT', 80)
    if PORT == '':
        PORT = 80
    PORT = int(PORT)
    app.run(HOST, PORT, debug=True)
