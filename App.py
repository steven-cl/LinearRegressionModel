"""
Aplicación GUI para comparar dos enfoques de regresión sobre pares (x, y):
1. Regresión Lineal (scikit-learn)
2. Regresión Exponencial y = a * e^{b x}  (linealizando con ln(y))

Funciones:
- Ingresar X e y
- Calcular ambos modelos y mostrar métricas (R2, MSE, RMSE)
- Seleccionar modelo y graficar
- Resaltar el de menor RMSE
"""

import tkinter as tk
import AppGUI


def main():
    """
    Función principal que inicia la aplicación.
    """
    root = tk.Tk()
    AppGUI.inicializar_interfaz(root)
    root.mainloop()


if __name__ == "__main__":
    main()
