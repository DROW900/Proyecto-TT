import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score


# **** Algoritmo predictivo correspondiente a la turbidez de agua ****
#Los datos son almacenados para 1 Litro de agua
turbidezMedidaEnVoltaje = [4.26, 4.22, 4.17]
concentradoAgregado = [50,51,54]

fig, ax = plt.subplots(figsize=(6, 3.84))
datos = pd.DataFrame({'Turbidez': turbidezMedidaEnVoltaje, 'Concentrado Agregado': concentradoAgregado})
datos.head()

datos.plot(x='Turbidez', y='Concentrado Agregado')
ax.set_title('Distribución de bateos y runs')