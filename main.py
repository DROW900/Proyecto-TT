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
    pic = serial.Serial('/dev/ttyS0', 9600, timeout=1);
    
    respuestaComunicacion = "";
    #Inicializacion

    
    # ****** Pruebas ******

    # ******* ********
    
    #Medir turbidez - Comando A1\n
        ## Recibe - Voltaje
    time.sleep(1)
    guardarDataEnArchivo("instruccion", "Midiendo turbidez inicial")
    respuestaComunicacion = gestionarMensaje(pic, "A1\n".encode())
    print("Voltaje Turbidez: " + respuestaComunicacion)
    guardarDataEnArchivo("voltajeTurbidezMedidaInicial", respuestaComunicacion)
    
    # Medir pH medio - Comando A2\n
        ## Recibe - Voltaje
    time.sleep(1)
    guardarDataEnArchivo("instruccion", "Midiendo ph inicial")
    respuestaComunicacion = gestionarMensaje(pic, "A2\n".encode())
    guardarDataEnArchivo("phMedidoInicial", respuestaComunicacion)
    
    #Dispensar sulfato y gomaguar - Comando PI300FI200F\n Todo es en mililitros, primero sulfato y luego gomaguar en el comando
        ## Recibe - "OK"
    guardarDataEnArchivo("instruccion", "Dispensando quimicos")
    respuestaComunicacion = gestionarMensaje(pic, "PI250FI500F\n".encode())
    print("Estado dispensado sulfato y gomaguar: " + respuestaComunicacion)
    # TODO: OBTENER EL VALOR CON BASE EN EL ALGORITMO PREDICTIVO
    
    #Mezcla rapido 60 segundos - Comando T2I(0-4)FI(Segundos)F donde el primer numero representa la velocidad, siendo 0 10%, 1 30%, 2 60%, 3 80%, 4 90%
        ## Recibe - "OK"
    guardarDataEnArchivo("instruccion", "Regulando pH")
    respuestaComunicacion = gestionarMensaje(pic, "T2I4FI10F\n".encode())
    print("Estado mezclado: " + respuestaComunicacion)
    
    # Medir pH medio - Comando A2\n
        ## Recibe - Voltaje
    respuestaComunicacion = gestionarMensaje(pic, "A2\n".encode())
    print("Voltaje pH: " + respuestaComunicacion)
    
    # Determinar y agregar bicarbonato - Comando T1I(Gramos)F
        ## Recibe - OK"
        #respuestaComunicacion = gestionarMensaje(pic, "A2\n".encode()) - Pendiente
        
    # Mezclar rapido 120 segundos
        ## Recibe - OK"
    guardarDataEnArchivo("instruccion", "Mezclando quimicos")
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
    guardarDataEnArchivo("instruccion", "Reposando")
    respuestaComunicacion = gestionarMensaje(pic, "T3\n".encode())
    print("Reposo completado")
    # Bombeo al filtro - B\n
        ## Recibe - OK"
        #respuestaComunicacion = gestionarMensaje(pic, "T2I0FI360F\n".encode())
        
    # Mandar E y resetear\n

#Funcion guardar informacion
def guardarDataEnArchivo(dato, valor):
    datosProceso[dato] = valor
    f = open("data.json", 'w')
    json.dump(datosProceso, f)
    f.close()

    
#Funcion para administrar la comunicacion
def gestionarMensaje(comunicador, comando):
    contador = 1
    comunicador.write(comando);
    while contador > 0:
        cadenaLeida = leerPorUart(comunicador)
        contador -= 1
        return cadenaLeida

#Funcion para leer por el UART
def leerPorUart(comunicador):
    respuestaString = "";
    while True:
        if comunicador.in_waiting > 0:
            letra = comunicador.read().decode("utf-8")
            if letra == '\n':
                return respuestaString
            respuestaString += letra
            


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
    hilo1 = Thread(target=controlarPIC)
    hilo1.start()
    app.run(host="localhost" ,debug=False, port=4000)
    hilo1.join()
