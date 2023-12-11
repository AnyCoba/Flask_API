from flask import Flask, request, jsonify
import os
import pickle
import sqlite3


os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

# Función para conectar a la base de datos y obtener los datos necesarios
def get_data_from_database():

    conn = sqlite3.connect(r"C:/Users/Ana/Desktop/4. BOOTCAMP/Ana Fdz/4-Data_Engineering/1-APIs/Model/ejercicio/api_database.db")
    query = conn.execute("""
            SELECT tv, radio, newpaper from datos LIMIT 1
             """)

    data = query.fetchone()
    conn.close()
    return data

@app.route("/", methods=['GET'])
def hello():
    return "Bienvenido a mi API del modelo advertising"

# 1. Endpoint que devuelva la predicción de los nuevos datos enviados mediante argumentos en la llamada
@app.route('/v1/predict', methods=['GET'])
def predict():
    model = pickle.load(open('data/advertising_model','rb'))

    # Obtener datos de la base de datos
    database_data = get_data_from_database()

    # Verificar si se obtuvieron datos de la base de datos
    if database_data is None:
        return "No se pudieron obtener datos de la base de datos"

    # Desempacar los datos

    tv, radio, newspaper = database_data


    if tv is None or radio is None or newspaper is None:
        return "Missing args, the input values are needed to predict"
    else:
        prediction = model.predict([[int(tv),int(radio),int(newspaper)]])
        return "The prediction of sales investing that amount of money in TV, radio and newspaper is: " + str(round(prediction[0],2)) + 'k €'

app.run()