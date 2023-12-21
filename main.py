from threading import Thread
from flask import Flask, render_template
import time, serial, json, os

app = Flask(__name__)

global datosProceso

datosProceso = {
    'fase': 'Inicializacion',
    'isComplete': False,
    'phMedidoInicial': 0,
    'phMedidoMedio': 0,
    'phMedidoFinal': 0,
    'voltajeTurbidezMedidaInicial': 0,
    'voltajeTurbidezMedidaFinal': 0,
    'turbidezDeterminadaEnNTUInicial': 0,
    'turbidezDeterminadaEnNTUFinal': 0
} 

## ***** Parte de la comunicación *****

def controlarPIC():
    global datosProceso

    ## Se hace la lectura del fichero con el JSON, validando la existencia de este
    if not os.path.exists('data.json'):
        with open('data.json', 'w') as fichero:
            json.dump(datosProceso,fichero)
    else:
        with open('data.json', 'r') as fichero:
            datosProceso = json.load(fichero)

    ## Se abre paso a realizar la secuencia de limpieza, configurando los parámetros de comunicación
       #arduino = serial.Serial('COM3', 9600)
        pic = serial.Serial('/dev/ttyS0', 9600, timeout=1);


## ***** ENDPOINTS DEL SERVIDOR *****
@app.route('/ping')
def ping():
    global valor
    return datosProceso

@app.route("/")
def index():
    return render_template("index.html" )


## ***** MAIN *****
if __name__ == '__main__':
    ## Se inicializa el servidor, y se crea el hilo que llevará el flujo del PIC
    #hilo1 = Thread(target=controlarPIC)
    #hilo1.start()
    app.run(host="localhost" ,debug=True, port=4000)
    #hilo1.join()