from threading import Thread
from flask import Flask, render_template
import time, serial, json, os
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd

app = Flask(__name__)

global datosProceso

datosProceso = {
    'fase': 0,
    'instruccion': 'Inicializacion',
    'isComplete': False,
    'cantidadFloculante': 'Por definir',
    'cantidadBicarbonato': 'Por definir',
    'phMedidoInicial': 'Por medir',
    'phMedidoMedio': 'Por medir',
    'phMedidoFinal': 'Por medir',
    'voltajeTurbidezMedidaInicial': 0,
    'voltajeTurbidezMedidaFinal': 0,
    'turbidezDeterminadaEnNTUInicial': 'Por medir',
    'turbidezDeterminadaEnNTUFinal': 'Por medir'
}

## ***** Preparación modelos predictivos *****
def generarModeloFloculante():
    # Datos de entrenamiento Floculante
    turbidezMedidaEnVoltaje = [4.26, 4.22, 4.17, 3.63, 3.39]
    concentradoAgregado = [50, 51, 54, 100, 110]

    dataFrameRegulador = pd.DataFrame({'Turbidez': turbidezMedidaEnVoltaje, 'Concentrado Agregado': concentradoAgregado})

    XTurbidez = dataFrameRegulador[["Turbidez"]]
    yTurbidez = dataFrameRegulador["Concentrado Agregado"]

    XT_train, XT_test, yT_train, yT_test = train_test_split(
        XTurbidez.values.reshape(-1, 1),
        yTurbidez.values.reshape(-1, 1),
        train_size=0.6,
        random_state=1234,
        shuffle=True
    )

    modeloTurbidez = LinearRegression()
    modeloTurbidez.fit(X=XT_train.reshape(-1, 1), y=yT_train)

    return modeloTurbidez

def generarModeloPh():
    # Datos de entrenamiento regulador pH
    pHMedido = [7.25, 7.15, 6.3, 7.0, 6.1]
    bicarbonatoAgregado = [1.6, 1.7, 2.2, 1.8, 2.3]

    dataFramepH = pd.DataFrame({'Nivel de pH': pHMedido, 'Bicarbonato Agregado': bicarbonatoAgregado})

    # Generación de variables para el entrenamiento y la definición del modelo para regulación de pH
    XPh = dataFramepH[["Nivel de pH"]]
    yPh = dataFramepH["Bicarbonato Agregado"]

    XP_train, XP_test, yP_train, yP_test = train_test_split(
        XPh.values.reshape(-1, 1),
        yPh.values.reshape(-1, 1),
        train_size=0.6,
        random_state=1234,
        shuffle=True
    )
    modeloPh = LinearRegression()
    modeloPh.fit(X=XP_train.reshape(-1, 1), y=yP_train)

    return modeloPh

## ***** Lectura del archivo de datos *****
def leerJson():
    global datosProceso
    ## Se hace la lectura del fichero con el JSON, validando la existencia de este
    if not os.path.exists('data.json'):
        with open('data.json', 'w') as fichero:
            json.dump(datosProceso,fichero)
    else:
        with open('data.json', 'r') as fichero:
            datosProceso = json.load(fichero)


## ***** Parte de la comunicación *****
def controlarPIC():
    #Se crean los modelos
    modelopH = generarModeloPh()
    modeloRegulador = generarModeloFloculante()

    #Se lee el archivo JSON
    leerJson()

    # Pruebas del modelo Turbidez
    numeroSensado = np.array([4.34])
    print(numeroSensado)
    prediccion = modeloRegulador.predict(numeroSensado.reshape(1,-1))
    print(prediccion)

    #Prueba del modelo pH
    numeroSensado = np.array([7])
    print(numeroSensado)
    prediccion = modelopH.predict(numeroSensado.reshape(1,-1))
    print("Prediccion pH: ", round(float(prediccion[0][0])))

    ## Se abre paso a realizar la secuencia de limpieza, configurando los parámetros de comunicación
    pic = serial.Serial('/dev/ttyS0', 9600, timeout=1)

    #Se inicializa un proceso de limpieza
    actualizarData("fase", 0);
    actualizarData("instruccion", "Esperando el llenado del contenedor")
    respuestaComunicacion = gestionarMensaje(pic, "INIT\n".encode())
    print("Empieza una nueva limpieza")

    #Medir turbidez - Comando A1\n
        ## Recibe - Voltaje
    actualizarData("fase", 1)
    actualizarData("instruccion", "Midiendo turbidez inicial")
    respuestaComunicacion = gestionarMensaje(pic, "A1\n".encode())
    voltajeSensado = float(respuestaComunicacion) # Se obtiene un voltaje en cadena, por lo que se pasa a un flotante
    actualizarData('voltajeTurbidezMedidaInicial', voltajeSensado)
    floculanteADispensar = round(modeloRegulador.predict(np.array(voltajeSensado).reshape(1,-1)))
    actualizarData('cantidadFloculante', floculanteADispensar)
    actualizarData('turbidezDeterminadaEnNTUInicial', -1120.4 * (voltajeSensado**2) + 5742.3 * voltajeSensado - 3778.236)

    # Medir pH medio - Comando A2\n
        ## Recibe - Voltaje
    actualizarData("fase", 2)
    actualizarData("instruccion", "Midiendo ph inicial")
    respuestaComunicacion = gestionarMensaje(pic, "A2\n".encode());
    actualizarData("phMedidoInicial", respuestaComunicacion)
    
    #Dispensar sulfato y gomaguar - Comando PI300FI200F\n todo es en mililitros, primero sulfato y luego gomaguar en el comando
        ## Recibe - "OK"
    actualizarData("fase", 3)
    actualizarData("instruccion", "Dispensando quimicos")
    respuestaComunicacion = gestionarMensaje(pic, "PI250FI500F\n".encode())
    print("Estado dispensado sulfato y gomaguar: " + respuestaComunicacion)
    # TODO: OBTENER EL VALOR CON BASE EN EL ALGORITMO PREDICTIVO
    
    #Mezcla rapido 60 segundos - Comando T2I(0-4)FI(Segundos)F donde el primer numero representa la velocidad, siendo 0 10%, 1 30%, 2 60%, 3 80%, 4 90%
        ## Recibe - "OK"
    actualizarData("fase", 4)
    actualizarData("instruccion", "Regulando pH")
    respuestaComunicacion = gestionarMensaje(pic, "T2I4FI10F\n".encode())
    print("Estado mezclado: " + respuestaComunicacion)
    
    # Medir pH medio - Comando A2\n
        ## Recibe - Voltaje
    respuestaComunicacion = gestionarMensaje(pic, "A2\n".encode())
    print("Voltaje pH: " + respuestaComunicacion)
    
    # Determinar y agregar bicarbonato - Comando T1I(Gramos)F
        ## Recibe - OK"
        #respuestaComunicacion = gestionarMensaje(pic, "A2\n".encode()) - Pendiente
        # TODO: OBTENER EL VALOR CON BASE EN EL ALGORITMO PREDICTIVO
        
    # Mezclar rapido 120 segundos
        ## Recibe - OK"
    actualizarData("fase", 5)
    actualizarData("instruccion", "Mezclando quimicos")
    respuestaComunicacion = gestionarMensaje(pic, "T2I4FI7F\n".encode())
    print("Estado mezclado: " + respuestaComunicacion)

    # Meclar medio 420 segundos
        ## Recibe - OK"
    respuestaComunicacion = gestionarMensaje(pic, "T2I1FI30F\n".encode())
    print("Estado mezclado: " + respuestaComunicacion)

    # Mezclar lento 360 segundos
        ## Recibe - OK"
    respuestaComunicacion = gestionarMensaje(pic, "T2I0FI15F\n".encode())
    print("Estado mezclado: " + respuestaComunicacion)
    
    # Reposo - Comando T3
        ## Recibe - "OK"
    actualizarData("fase", 6)
    actualizarData("instruccion", "Reposando")
    respuestaComunicacion = gestionarMensaje(pic, "T3\n".encode())
    print("Reposo completado")

    # Bombeo al filtro - B\n
        ## Recibe - OK"
        #respuestaComunicacion = gestionarMensaje(pic, "T2I0FI360F\n".encode())
        
    # Mandar E y resetear\n


#Funcion guardar informacion
def actualizarData(dato, valor):
    datosProceso[dato] = valor
    f = open("data.json", 'w')
    json.dump(datosProceso, f)
    f.close()

#Funcion para administrar la comunicacion
def gestionarMensaje(comunicador, comando):
    comunicador.write(comando)
    cadenaLeida = leerPorUart(comunicador)
    return cadenaLeida

#Funcion para leer por el UART
def leerPorUart(comunicador):
    respuestaString = ""
    while True:
        if comunicador.in_waiting > 0:
            letra = comunicador.read().decode("utf-8")
            if letra == '\n':
                return respuestaString
            respuestaString += letra
def definirTiempoDispensador(modelo):
    print("Funciona")

## ***** ENDPOINTS DEL SERVIDOR *****
@app.route('/getInfo')
def getInfo():
    global valor
    leerJson()
    return datosProceso

@app.route("/")
def index():
    return render_template("index.html" )


## ***** MAIN *****
if __name__ == '__main__':
    # Se inicializa el hilo con el flujo de limpieza
    hilo1 = Thread(target=controlarPIC)
    hilo1.start()

    ## Se inicializa el servidor
    app.run(host="localhost" ,debug=False, port=4000)

    hilo1.join()
