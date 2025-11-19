"""
Script de prueba para verificar que los módulos refactorizados funcionan correctamente.
"""

import numpy as np
import OperationsApp


def test_parse_numbers():
    """Prueba la función de parseo de números."""
    print("Testing parse_numbers...")
    
    # Test con comas
    result = OperationsApp.parse_numbers("1, 2, 3, 4")
    assert result == [1.0, 2.0, 3.0, 4.0], f"Expected [1.0, 2.0, 3.0, 4.0], got {result}"
    
    # Test con espacios
    result = OperationsApp.parse_numbers("1 2 3 4")
    assert result == [1.0, 2.0, 3.0, 4.0], f"Expected [1.0, 2.0, 3.0, 4.0], got {result}"
    
    # Test con saltos de línea
    result = OperationsApp.parse_numbers("1\n2\n3\n4")
    assert result == [1.0, 2.0, 3.0, 4.0], f"Expected [1.0, 2.0, 3.0, 4.0], got {result}"
    
    # Test con mezcla
    result = OperationsApp.parse_numbers("1, 2\n3 4")
    assert result == [1.0, 2.0, 3.0, 4.0], f"Expected [1.0, 2.0, 3.0, 4.0], got {result}"
    
    print("✓ parse_numbers tests passed")


def test_regresion_lineal():
    """Prueba la función de regresión lineal."""
    print("\nTesting calcular_regresion_lineal...")
    
    # Datos de prueba: y = 2 + 3x
    X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
    y = np.array([5, 8, 11, 14, 17])
    
    result = OperationsApp.calcular_regresion_lineal(X, y)
    
    # Verificar que el resultado contiene las claves esperadas
    expected_keys = ["intercept", "coef", "y_pred", "mse", "rmse", "r2"]
    for key in expected_keys:
        assert key in result, f"Key '{key}' not found in result"
    
    # Verificar que los coeficientes son aproximadamente correctos
    assert abs(result["intercept"] - 2.0) < 0.01, f"Expected intercept ~2.0, got {result['intercept']}"
    assert abs(result["coef"] - 3.0) < 0.01, f"Expected coef ~3.0, got {result['coef']}"
    
    # Verificar que R² es cercano a 1 (ajuste perfecto)
    assert result["r2"] > 0.99, f"Expected R² > 0.99, got {result['r2']}"
    
    print(f"  Intercept: {result['intercept']:.4f}")
    print(f"  Coef: {result['coef']:.4f}")
    print(f"  R²: {result['r2']:.6f}")
    print(f"  RMSE: {result['rmse']:.6f}")
    print("✓ calcular_regresion_lineal tests passed")


def test_regresion_exponencial():
    """Prueba la función de regresión exponencial."""
    print("\nTesting calcular_regresion_exponencial...")
    
    # Datos de prueba exponenciales
    X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
    y = np.array([2.7, 7.4, 20.1, 54.6, 148.4])  # Aproximadamente y = e^x
    
    result = OperationsApp.calcular_regresion_exponencial(X, y)
    
    # Verificar que el resultado contiene las claves esperadas
    expected_keys = ["a", "b", "y_pred", "mse", "rmse", "r2"]
    for key in expected_keys:
        assert key in result, f"Key '{key}' not found in result"
    
    print(f"  a: {result['a']:.4f}")
    print(f"  b: {result['b']:.4f}")
    print(f"  R²: {result['r2']:.6f}")
    print(f"  RMSE: {result['rmse']:.6f}")
    print("✓ calcular_regresion_exponencial tests passed")
    
    # Prueba con valores negativos (debe retornar None)
    print("\nTesting calcular_regresion_exponencial with negative values...")
    y_neg = np.array([1, -2, 3, 4, 5])
    result_neg = OperationsApp.calcular_regresion_exponencial(X, y_neg)
    assert result_neg is None, "Expected None for negative y values"
    print("✓ Correctly returns None for negative values")


def test_regresion_potencial():
    """Prueba la función de regresión potencial."""
    print("\nTesting calcular_regresion_potencial...")
    
    # Datos de prueba: y = 2 * x^3
    X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
    y = np.array([2, 16, 54, 128, 250])
    
    result = OperationsApp.calcular_regresion_potencial(X, y)
    
    # Verificar que el resultado contiene las claves esperadas
    expected_keys = ["a", "b", "y_pred", "mse", "rmse", "r2"]
    for key in expected_keys:
        assert key in result, f"Key '{key}' not found in result"
    
    print(f"  a: {result['a']:.4f}")
    print(f"  b: {result['b']:.4f}")
    print(f"  R²: {result['r2']:.6f}")
    print(f"  RMSE: {result['rmse']:.6f}")
    print("✓ calcular_regresion_potencial tests passed")
    
    # Prueba con valores negativos o cero (debe retornar None)
    print("\nTesting calcular_regresion_potencial with non-positive values...")
    X_zero = np.array([0, 1, 2, 3, 4]).reshape(-1, 1)
    result_zero = OperationsApp.calcular_regresion_potencial(X_zero, y)
    assert result_zero is None, "Expected None for x values with zero"
    
    y_neg = np.array([1, -2, 3, 4, 5])
    result_neg = OperationsApp.calcular_regresion_potencial(X, y_neg)
    assert result_neg is None, "Expected None for negative y values"
    print("✓ Correctly returns None for non-positive values")


def test_regresion_logaritmica():
    """Prueba la función de regresión logarítmica."""
    print("\nTesting calcular_regresion_logaritmica...")
    
    # Datos de prueba logarítmicos: y = 1 + 2*ln(x)
    X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
    y = np.array([1.0, 2.386, 3.197, 3.773, 4.219])
    
    result = OperationsApp.calcular_regresion_logaritmica(X, y)
    
    # Verificar que el resultado contiene las claves esperadas
    expected_keys = ["a", "b", "y_pred", "mse", "rmse", "r2"]
    for key in expected_keys:
        assert key in result, f"Key '{key}' not found in result"
    
    print(f"  a: {result['a']:.4f}")
    print(f"  b: {result['b']:.4f}")
    print(f"  R²: {result['r2']:.6f}")
    print(f"  RMSE: {result['rmse']:.6f}")
    print("✓ calcular_regresion_logaritmica tests passed")
    
    # Prueba con valores negativos o cero (debe retornar None)
    print("\nTesting calcular_regresion_logaritmica with non-positive x values...")
    X_zero = np.array([0, 1, 2, 3, 4]).reshape(-1, 1)
    result_zero = OperationsApp.calcular_regresion_logaritmica(X_zero, y)
    assert result_zero is None, "Expected None for x values with zero"
    print("✓ Correctly returns None for non-positive x values")


def test_regresion_polinomial_grado2():
    """Prueba la función de regresión polinomial de grado 2."""
    print("\nTesting calcular_regresion_polinomial_grado2...")
    
    # Datos de prueba: y = 1 + 2x + 3x²
    X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
    y = np.array([6, 17, 34, 57, 86])
    
    result = OperationsApp.calcular_regresion_polinomial_grado2(X, y)
    
    # Verificar que el resultado contiene las claves esperadas
    expected_keys = ["a", "b", "c", "y_pred", "mse", "rmse", "r2"]
    for key in expected_keys:
        assert key in result, f"Key '{key}' not found in result"
    
    # Verificar que los coeficientes son aproximadamente correctos
    assert abs(result["a"] - 1.0) < 0.01, f"Expected a ~1.0, got {result['a']}"
    assert abs(result["b"] - 2.0) < 0.01, f"Expected b ~2.0, got {result['b']}"
    assert abs(result["c"] - 3.0) < 0.01, f"Expected c ~3.0, got {result['c']}"
    
    # Verificar que R² es cercano a 1 (ajuste perfecto)
    assert result["r2"] > 0.99, f"Expected R² > 0.99, got {result['r2']}"
    
    print(f"  a: {result['a']:.4f}")
    print(f"  b: {result['b']:.4f}")
    print(f"  c: {result['c']:.4f}")
    print(f"  R²: {result['r2']:.6f}")
    print(f"  RMSE: {result['rmse']:.6f}")
    print("✓ calcular_regresion_polinomial_grado2 tests passed")


def test_calcular_todos_modelos():
    """Prueba la función que calcula todos los modelos."""
    print("\nTesting calcular_todos_modelos...")
    
    xs = [1, 2, 3, 4, 5]
    ys = [5, 8, 11, 14, 17]
    
    resultados = OperationsApp.calcular_todos_modelos(xs, ys)
    
    # Verificar que todos los modelos están en el resultado
    expected_models = ["linear_sklearn", "exponential", "power", "logarithmic", "polynomial_2"]
    for model in expected_models:
        assert model in resultados, f"{model} not in resultados"
    
    # Verificar que los resultados no son None
    assert resultados["linear_sklearn"] is not None, "linear_sklearn result is None"
    assert resultados["exponential"] is not None, "exponential result is None"
    assert resultados["power"] is not None, "power result is None"
    assert resultados["logarithmic"] is not None, "logarithmic result is None"
    assert resultados["polynomial_2"] is not None, "polynomial_2 result is None"
    
    print("  Linear regression calculated")
    print("  Exponential regression calculated")
    print("  Power regression calculated")
    print("  Logarithmic regression calculated")
    print("  Polynomial regression (degree 2) calculated")
    print("✓ calcular_todos_modelos tests passed")


def run_all_tests():
    """Ejecuta todas las pruebas."""
    print("=" * 60)
    print("Running OperationsApp tests...")
    print("=" * 60)
    
    test_parse_numbers()
    test_regresion_lineal()
    test_regresion_exponencial()
    test_regresion_potencial()
    test_regresion_logaritmica()
    test_regresion_polinomial_grado2()
    test_calcular_todos_modelos()
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
