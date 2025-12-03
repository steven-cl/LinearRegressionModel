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
from tkinter import messagebox

# Guardar referencia a la función original
_original_inicializar_interfaz = AppGUI.inicializar_interfaz

def _safe_inicializar_interfaz(root):
    try:
        _original_inicializar_interfaz(root)
    except Exception as e:
        root.withdraw()
        messagebox.showerror("Error", str(e))

# Reemplazar la función por la versión segura
AppGUI.inicializar_interfaz = _safe_inicializar_interfaz

def main():
    root = tk.Tk()
    AppGUI.inicializar_interfaz(root)
    root.mainloop()

if __name__ == "__main__":
    main()
