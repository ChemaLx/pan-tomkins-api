from flask import Flask, jsonify
from flask import request
from fakeapi import datos_ECG
from flask_cors import CORS, cross_origin
import pan_tomkins_f

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
time_stamp = []
for i in range(0,3600):
    time_stamp.append(i)
#print(time_stamp)


@app.route('/procesar', methods=['POST'])
def procesar_datos():
    request_data = request.get_json()
    #print(request_data)
    ecg = request_data['electrocardiograma']
    edad = request_data['edad']
    sexo = request_data['sexo']
    ecg.pop()
    print(len(ecg))
    print(len(time_stamp))
    ecg_int = []
    for muestra in ecg:
        ecg_int.append(float(muestra))
    heart_beat = pan_tomkins_f.iniciar(ecg_int)
    
    print("Heart Rate: "+ str(60/heart_beat) + " BPM")
    
    heart_beat = 60/heart_beat
    
    return jsonify({
        "heart_beat": heart_beat,
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