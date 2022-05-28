from flask import Flask, jsonify
from flask import request
import requests
from fakeapi import datos_ECG
from flask_cors import CORS, cross_origin
import pan_tomkins_f

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/procesar-ecg', methods=['POST'])
def procesar_datos():
    request_data = request.get_json()
    #print(request_data)
    ecg = request_data['electrocardiograma']
    print (ecg)
    ecg.pop()
    print(len(ecg))
    ecg_int = []
    for muestra in ecg:
        ecg_int.append(float(muestra))
    
    heart_beat = pan_tomkins_f.iniciar(ecg_int, len(ecg_int))
    
    print("Heart Rate: "+ str(60/heart_beat) + " BPM")
    
    heart_beat = 60/heart_beat
    
    return jsonify({
        "ritmo_cardiaco": heart_beat,
        #"ecg": datos_ECG
    })

@app.route('/recuperar/datos/usuario/', methods=['GET'])
def informacion_usuario():
    print(request.headers)
    app.logger.debug("Request Headers %s", request.headers)
    id_usuario = request.args.get('idUsuario')
    print(id_usuario)
    return jsonify({
        "body": {
            "sexo": 0,
            "edad": 22
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=4000)
