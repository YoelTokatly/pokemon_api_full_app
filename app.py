from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://admin:pokemon123@pokemon-mongodb:27017/')
db = client.pokemon_db

@app.route('/pokemon', methods=['GET'])
def get_pokemon():
    # Your API logic here
    passcdoe 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

