"""
Test de integración para verificar que el flujo completo funciona.
"""

import numpy as np
import OperationsApp


def test_integration():
    """Prueba de integración completa del flujo de cálculo."""
    print("=" * 60)
    print("Integration Test: Complete Workflow")
    print("=" * 60)
    
    # Simular datos de entrada como strings (como vienen de la GUI)
    x_input = "1, 2, 3, 4, 5"
    y_input = "2.1, 4.2, 6.1, 8.2, 10.0"
    
    print("\n1. Parsing input data...")
    xs = OperationsApp.parse_numbers(x_input)
    ys = OperationsApp.parse_numbers(y_input)
    print(f"   X values: {xs}")
    print(f"   Y values: {ys}")
    
    # Validaciones
    print("\n2. Validating input...")
    assert len(xs) == len(ys), "X and Y must have same length"
    assert len(xs) >= 2, "Need at least 2 pairs"
    print(f"   ✓ Valid: {len(xs)} pairs of data")
    
    # Calcular todos los modelos
    print("\n3. Calculating all models...")
    resultados = OperationsApp.calcular_todos_modelos(xs, ys)
    
    # Verificar resultados de regresión lineal
    print("\n4. Linear Regression Results:")
    lr_result = resultados["Lineal"]
    print(f"   Formula: y = {lr_result['intercept']:.4f} + {lr_result['coef']:.4f}x")
    print(f"   R²: {lr_result['r2']:.6f}")
    print(f"   MSE: {lr_result['mse']:.6f}")
    print(f"   RMSE: {lr_result['rmse']:.6f}")
    
    # Verificar resultados de regresión exponencial
    print("\n5. Exponential Regression Results:")
    exp_result = resultados["Exponencial"]
    if exp_result is not None:
        print(f"   Formula: y = {exp_result['a']:.4f} * e^({exp_result['b']:.4f}x)")
        print(f"   R²: {exp_result['r2']:.6f}")
        print(f"   MSE: {exp_result['mse']:.6f}")
        print(f"   RMSE: {exp_result['rmse']:.6f}")
    else:
        print("   Not applicable (negative y values)")
    
    # Encontrar el mejor modelo
    print("\n6. Finding best model (lowest RMSE)...")
    modelos_validos = {k: v for k, v in resultados.items() if v is not None}
    mejor_modelo = min(modelos_validos.keys(), key=lambda k: modelos_validos[k]["rmse"])
    print(f"   Best model: {mejor_modelo}")
    print(f"   RMSE: {modelos_validos[mejor_modelo]['rmse']:.6f}")
    
    # Simular graficar el modelo seleccionado
    print("\n7. Simulating plot data generation...")
    metodo = "Lineal"
    r = resultados[metodo]
    X = np.array(xs)
    y = np.array(ys)
    
    # Ordenar para el gráfico
    orden = np.argsort(X)
    X_sorted = X[orden]
    
    if metodo == "Lineal":
        y_line = r["intercept"] + r["coef"] * X_sorted
        formula = f"y = {r['intercept']:.6f} + {r['coef']:.6f}x"
    else:
        y_line = r["a"] * np.exp(r["b"] * X_sorted)
        formula = f"y = {r['a']:.6f} * e^{r['b']:.6f}x"
    
    print(f"   Formula: {formula}")
    print(f"   Plot points: {len(y_line)}")
    
    print("\n" + "=" * 60)
    print("Integration test passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    test_integration()
