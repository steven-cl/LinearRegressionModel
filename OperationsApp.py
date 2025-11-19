"""
Módulo de operaciones matemáticas para regresión lineal y exponencial.
Contiene todas las funciones de cálculo de modelos y métricas.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


def parse_numbers(text):
    """
    Parsea una cadena de texto que contiene números separados por comas, espacios o saltos de línea.
    
    Args:
        text: Cadena de texto con números
        
    Returns:
        Lista de valores flotantes
        
    Raises:
        ValueError: Si algún valor no puede ser convertido a número
    """
    raw = text.replace("\n", " ").replace(";", " ").split(",")
    parts = []
    for chunk in raw:
        for token in chunk.strip().split():
            if token:
                parts.append(token)
    vals = []
    for p in parts:
        try:
            vals.append(float(p))
        except ValueError:
            raise ValueError(f"Valor inválido: {p}")
    return vals


def calcular_regresion_lineal(X, y):
    """
    Calcula la regresión lineal usando scikit-learn.
    
    Args:
        X: Array numpy de valores X (shape: n x 1)
        y: Array numpy de valores y (shape: n)
        
    Returns:
        Diccionario con:
            - intercept: Término independiente (b)
            - coef: Coeficiente de X (m)
            - y_pred: Valores predichos
            - r2: Coeficiente de determinación R²
            - mse: Error cuadrático medio
            - rmse: Raíz del error cuadrático medio
    """
    lr = LinearRegression()
    lr.fit(X, y)
    y_pred = lr.predict(X)
    
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y, y_pred)
    
    return {
        "intercept": lr.intercept_,
        "coef": lr.coef_[0],
        "y_pred": y_pred,
        "mse": mse,
        "rmse": rmse,
        "r2": r2
    }


def calcular_regresion_exponencial(X, y):
    """
    Calcula la regresión exponencial y = a * e^(bx) usando linealización.
    
    Args:
        X: Array numpy de valores X (shape: n x 1)
        y: Array numpy de valores y (shape: n)
        
    Returns:
        Diccionario con:
            - a: Coeficiente a
            - b: Coeficiente b
            - y_pred: Valores predichos
            - r2: Coeficiente de determinación R²
            - mse: Error cuadrático medio
            - rmse: Raíz del error cuadrático medio
        None si algún valor de y es <= 0
    """
    if np.any(y <= 0):
        return None
    
    Y_log = np.log(y)
    lr_exp = LinearRegression()
    lr_exp.fit(X, Y_log)
    
    b = lr_exp.coef_[0]
    a = np.exp(lr_exp.intercept_)
    y_pred = a * np.exp(b * X.flatten())
    
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y, y_pred)
    
    return {
        "a": a,
        "b": b,
        "y_pred": y_pred,
        "mse": mse,
        "rmse": rmse,
        "r2": r2
    }


def calcular_todos_modelos(xs, ys):
    """
    Calcula todos los modelos de regresión disponibles.
    
    Args:
        xs: Lista de valores X
        ys: Lista de valores y
        
    Returns:
        Diccionario con los resultados de cada modelo:
            - "linear_sklearn": Resultados de regresión lineal
            - "exponential": Resultados de regresión exponencial (o None si no es aplicable)
    """
    X = np.array(xs).reshape(-1, 1)
    y = np.array(ys)
    
    resultados = {}
    
    # Calcular regresión lineal
    resultados["Lineal"] = calcular_regresion_lineal(X, y)
    
    # Calcular regresión exponencial
    resultados["Exponencial"] = calcular_regresion_exponencial(X, y)
    
    return resultados
