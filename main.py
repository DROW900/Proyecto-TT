import serial, time

arduino = serial.Serial('COM3', 9600)
time.sleep(2)

mensaje = arduino.readline()
print(mensaje)
arduino.write(b"Recibido\n")
mensaje = arduino.readline().decode('ascii')
print(mensaje)
arduino.close()