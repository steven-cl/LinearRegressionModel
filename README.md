# LinearRegressionModel
Linear Regression Model with Python

## 📋 Descripción

Aplicación GUI para comparar dos enfoques de regresión sobre pares de datos (x, y):
- **Regresión Lineal** usando scikit-learn
- **Regresión Exponencial** (y = a * e^(bx)) usando linealización

## 🚀 Cómo Ejecutar

```bash
python3 App.py
```

## 📁 Estructura Modular

El proyecto ha sido refactorizado en módulos independientes:

- **`OperationsApp.py`** - Operaciones matemáticas y cálculos
- **`AppGUI.py`** - Componentes de interfaz gráfica
- **`App.py`** - Punto de entrada principal

Ver [ESTRUCTURA_MODULAR.md](ESTRUCTURA_MODULAR.md) para más detalles.

## 📦 Dependencias

```bash
pip install numpy scikit-learn matplotlib
```

## ✅ Tests

```bash
python3 test_operations.py      # Tests unitarios
python3 test_integration.py     # Tests de integración
python3 test_comparison.py      # Verificación vs versión original
```

## 🎯 Funcionalidades

- ✓ Ingresar valores X e Y (múltiples formatos soportados)
- ✓ Calcular ambos modelos de regresión
- ✓ Mostrar métricas: R², MSE, RMSE y fórmula
- ✓ Resaltar modelo con mejor RMSE
- ✓ Visualizar gráficas interactivas
- ✓ Limpiar datos
