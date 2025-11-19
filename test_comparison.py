"""
Prueba de comparación para verificar que la versión refactorizada
produce exactamente los mismos resultados que la versión original.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import OperationsApp


def test_comparison_with_original():
    """
    Compara los resultados del módulo refactorizado con cálculos directos
    que replican la lógica original de app.py
    """
    print("=" * 70)
    print("COMPARISON TEST: Refactored vs Original Logic")
    print("=" * 70)
    
    # Datos de prueba
    xs_list = [1.0, 2.0, 3.0, 4.0, 5.0]
    ys_list = [2.1, 4.2, 6.1, 8.2, 10.0]
    
    X = np.array(xs_list).reshape(-1, 1)
    y = np.array(ys_list)
    
    print("\n--- TEST 1: Linear Regression ---")
    
    # Versión original (app.py)
    lr_original = LinearRegression()
    lr_original.fit(X, y)
    y_pred_original = lr_original.predict(X)
    mse_original = mean_squared_error(y, y_pred_original)
    rmse_original = np.sqrt(mse_original)
    r2_original = r2_score(y, y_pred_original)
    
    print("\nOriginal logic results:")
    print(f"  Intercept: {lr_original.intercept_:.6f}")
    print(f"  Coefficient: {lr_original.coef_[0]:.6f}")
    print(f"  R²: {r2_original:.6f}")
    print(f"  MSE: {mse_original:.6f}")
    print(f"  RMSE: {rmse_original:.6f}")
    
    # Versión refactorizada (OperationsApp)
    result_refactored = OperationsApp.calcular_regresion_lineal(X, y)
    
    print("\nRefactored module results:")
    print(f"  Intercept: {result_refactored['intercept']:.6f}")
    print(f"  Coefficient: {result_refactored['coef']:.6f}")
    print(f"  R²: {result_refactored['r2']:.6f}")
    print(f"  MSE: {result_refactored['mse']:.6f}")
    print(f"  RMSE: {result_refactored['rmse']:.6f}")
    
    # Verificar que son iguales
    assert abs(result_refactored['intercept'] - lr_original.intercept_) < 1e-10
    assert abs(result_refactored['coef'] - lr_original.coef_[0]) < 1e-10
    assert abs(result_refactored['r2'] - r2_original) < 1e-10
    assert abs(result_refactored['mse'] - mse_original) < 1e-10
    assert abs(result_refactored['rmse'] - rmse_original) < 1e-10
    
    print("\n✓ Linear Regression: Results match perfectly!")
    
    print("\n--- TEST 2: Exponential Regression ---")
    
    # Versión original (app.py)
    Y_log_original = np.log(y)
    lr_exp_original = LinearRegression()
    lr_exp_original.fit(X, Y_log_original)
    b_original = lr_exp_original.coef_[0]
    a_original = np.exp(lr_exp_original.intercept_)
    y_pred_exp_original = a_original * np.exp(b_original * X.flatten())
    mse_exp_original = mean_squared_error(y, y_pred_exp_original)
    rmse_exp_original = np.sqrt(mse_exp_original)
    r2_exp_original = r2_score(y, y_pred_exp_original)
    
    print("\nOriginal logic results:")
    print(f"  a: {a_original:.6f}")
    print(f"  b: {b_original:.6f}")
    print(f"  R²: {r2_exp_original:.6f}")
    print(f"  MSE: {mse_exp_original:.6f}")
    print(f"  RMSE: {rmse_exp_original:.6f}")
    
    # Versión refactorizada (OperationsApp)
    result_exp_refactored = OperationsApp.calcular_regresion_exponencial(X, y)
    
    print("\nRefactored module results:")
    print(f"  a: {result_exp_refactored['a']:.6f}")
    print(f"  b: {result_exp_refactored['b']:.6f}")
    print(f"  R²: {result_exp_refactored['r2']:.6f}")
    print(f"  MSE: {result_exp_refactored['mse']:.6f}")
    print(f"  RMSE: {result_exp_refactored['rmse']:.6f}")
    
    # Verificar que son iguales
    assert abs(result_exp_refactored['a'] - a_original) < 1e-10
    assert abs(result_exp_refactored['b'] - b_original) < 1e-10
    assert abs(result_exp_refactored['r2'] - r2_exp_original) < 1e-10
    assert abs(result_exp_refactored['mse'] - mse_exp_original) < 1e-10
    assert abs(result_exp_refactored['rmse'] - rmse_exp_original) < 1e-10
    
    print("\n✓ Exponential Regression: Results match perfectly!")
    
    print("\n--- TEST 3: Parse Numbers ---")
    
    test_strings = [
        "1, 2, 3, 4",
        "1 2 3 4",
        "1\n2\n3\n4",
        "1, 2\n3 4",
    ]
    
    for test_str in test_strings:
        # Lógica original
        raw = test_str.replace("\n", " ").replace(";", " ").split(",")
        parts = []
        for chunk in raw:
            for token in chunk.strip().split():
                if token:
                    parts.append(token)
        vals_original = []
        for p in parts:
            vals_original.append(float(p))
        
        # Lógica refactorizada
        vals_refactored = OperationsApp.parse_numbers(test_str)
        
        # Verificar
        assert vals_original == vals_refactored
        print(f"  '{repr(test_str)}' -> {vals_refactored} ✓")
    
    print("\n✓ Parse Numbers: Results match perfectly!")
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED! ✓")
    print("The refactored code produces EXACTLY the same results as original!")
    print("=" * 70)


if __name__ == "__main__":
    test_comparison_with_original()
