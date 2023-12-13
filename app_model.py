from flask import Flask, request, jsonify
import os
import pickle
import sqlite3
import pandas as pd

dir_path = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

path_sql = os.path.join(dir_path,"data","api_database.db")
path_model = os.path.join(dir_path,"data","advertising_model")
path_csv = os.path.join(dir_path, "data", "Advertising.csv")

df = pd.read_csv(path_csv, index_col=0)
df["newpaper"] = df["newpaper"].apply(lambda x: x.replace("s",""))
df.newpaper = df["newpaper"].astype("float")

conn = sqlite3.connect(path_sql)
df.to_sql('datos', conn, index=False, if_exists='replace')
conn.close()

# Función para conectar a la base de datos y obtener los datos necesarios
def get_data_from_database():
    conn = sqlite3.connect(path_sql)
    query = conn.execute('''SELECT tv, radio, newpaper, sales from datos''')
    data = query.fetchall()
    conn.close()
    return data

def ingest_data(tv, radio, newpaper, sales):
    conn = sqlite3.connect(path_sql)
    conn.execute("""
                        INSERT INTO datos (tv, radio, newpaper, sales)
                        VALUES (?,?,?,?)
                         """, (tv, radio, newpaper, sales))
    conn.commit()
    # Cerrar la conexión
    conn.close()

@app.route("/", methods=['GET'])
def hello():
    return f"Bienvenido a mi API del modelo advertising" 

# 1. Endpoint que devuelva la predicción de los nuevos datos enviados mediante argumentos en la llamada
@app.route('/predict', methods=['GET'])
def predict():
    data = request.json
    if data is None or 'data' not in data:
        return jsonify({'error': 'Datos no proporcionados o formato incorrecto'}), 400
    
    df = pd.DataFrame(data['data'])
    df.columns = ['TV', 'radio', 'newspaper']
    model = pickle.load(open(path_model, 'rb'))
    prediction = model.predict(df)
    return jsonify({'prediction': str(round(prediction[0], 2)) + 'k €'})


# Función para almacenar nuevos datos
@app.route('/ingest', methods=['POST'])
def ingest_data_endpoint():
    data = request.json
    if data is None or 'data' not in data:
        return jsonify({'error': 'Datos no proporcionados o formato incorrecto'}), 400

    values = data['data']
    for value_list in data['data']:
        if not isinstance(value_list, list) or len(value_list) != 4:
            return jsonify({'error': 'Formato de datos incorrecto'}), 400
        ingest_data(*value_list)
    return jsonify({'message': 'Datos ingresados correctamente'})




@app.route('/retrain', methods=['POST'])
def retrain_data():
    
    datos = get_data_from_database()

    df = pd.DataFrame(datos)

    df.columns = ['TV', 'radio', 'newpaper', 'sales']

    X = df[['TV', 'radio', 'newpaper']]
    y = df[['sales']]

    # Cargar modelo existente
    with open(path_model, 'rb') as f:
        old_model = pickle.load(f)

    # Reentrenar el modelo
    new_model = old_model.fit(X, y)


    with open(os.path.join(dir_path,"data", "new_model"), 'wb') as f:
        pickle.dump(new_model, f)

    return jsonify({'message': 'Modelo reentrenado correctamente.'})

app.run(host="0.0.0.0", port=5000)