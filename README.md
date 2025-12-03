# LinearRegressionModel

Aplicación GUI en Python para calcular, comparar y visualizar modelos de regresión sobre pares de datos (x, y). Soporta múltiples métodos, muestra métricas clave y resalta automáticamente el mejor modelo según RMSE.

## Tabla de Contenidos
- Descripción
- Uso de la Aplicación
- Capturas de Pantalla
- Modelos Implementados
- Características
- Requisitos
- Instalación
- Ejecución
- Formatos de Entrada
- Métricas y Selección del Mejor Modelo
- Estructura del Proyecto
- Troubleshooting
- Pruebas
- Descargas (Releases)
- Contribuir
- Licencia
- Autor

## Descripción
Permite:
- Ingresar datos X e Y en diversos formatos.
- Calcular y comparar múltiples modelos de regresión.
- Visualizar la curva/recta del modelo y los datos con matplotlib.
- Revisar métricas (R², MSE, RMSE, fórmula).
- Resaltar el modelo con menor RMSE.
- Guardar y buscar modelos en una base de datos local.

## Uso de la Aplicación
1. Ingresa “Valores X” y “Valores y”.
2. Presiona “Calcular Modelos”.
3. Revisa la tabla de métricas y fórmulas.
4. Selecciona el método y presiona “Mostrar Gráfica”.
5. Usa “Guardar” para almacenar el modelo en la base de datos.
6. Usa “Buscar Modelo” para localizar y cargar modelos guardados.
7. “Editar” se habilita al seleccionar un modelo desde la búsqueda y sirve para modificar modelos guardados.

## Capturas de Pantalla
- Vista principal:
<img width="1920" height="1048" alt="image" src="https://github.com/user-attachments/assets/41bde1c3-b004-4303-a9fd-40fc8d495973" />

---

- Cargando Modelos guardados:
<img width="1920" height="1049" alt="image" src="https://github.com/user-attachments/assets/5ea8599f-5383-43c9-aa5e-856cd8d57ce7" />

---

- Graficando mejor modelo:
<img width="1920" height="1049" alt="image" src="https://github.com/user-attachments/assets/bf762c0c-de41-496c-84ae-eb5416b0ee0d" />

---

- Graficando mejor modelo:
<img width="1920" height="1049" alt="image" src="https://github.com/user-attachments/assets/342cdb6c-9335-4368-ade1-b5a2a1fed48d" />

---

- Guardando un nuevo modelo:
<img width="1920" height="1049" alt="image" src="https://github.com/user-attachments/assets/c49c0175-c489-475a-8244-060c0d88954f" />

## Modelos Implementados
Claves retornadas por OperationsApp.py alineadas con la GUI:
- Lineal: y = a + b·x
- Exponencial: y = a · e^(b·x) (requiere y > 0)
- Potencial: y = a · x^b (requiere x > 0 y y > 0)
- Logarítmica: y = a + b·ln(x) (requiere x > 0)
- Polinomial grado 2: y = a + b·x + c·x^2

Las métricas se calculan en el espacio original de y.

## Características
- Ingreso flexible de datos (comas, espacios, punto y coma, saltos de línea).
- Cálculo y visualización inmediata de modelos.
- Tabla de métricas y fórmula por método.
- Resalta automáticamente el mejor modelo (menor RMSE).
- Curva/recta suavizada en la gráfica.
- Integración con base de datos para guardar, buscar y editar modelos.

## Requisitos
- Python 3.9+
- Dependencias:
  - numpy
  - scikit-learn
  - matplotlib
  - tkinter
  - sqlite3 (incluido en Python)

Instalación de dependencias:
```bash
pip install -r requirements.txt
```

## Instalación
```bash
git clone https://github.com/steven-cl/LinearRegressionModel.git
cd LinearRegressionModel
pip install -r requirements.txt
```

## Ejecución
```bash
python3 App.py
```

En Linux con entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 App.py
```

## Formatos de Entrada
Acepta mezclas de:
- Comas: 1, 2, 3, 4
- Espacios: 1 2 3 4
- Punto y coma: 1; 2; 3; 4
- Saltos de línea: </br>
  1</br>
  2</br>
  3

El parser ignora espacios extra.

## Métricas y Selección del Mejor Modelo
- R²: coeficiente de determinación.
- MSE: error cuadrático medio.
- RMSE: raíz del error cuadrático medio.
El mejor modelo se elige por RMSE mínimo entre los métodos válidos.

## Estructura del Proyecto
- App.py: punto de entrada de la aplicación GUI.
- AppGUI.py: componentes y lógica de interfaz (Tkinter, plotting, búsqueda/edición).
- OperationsApp.py: cálculo de modelos y métricas.
- Queries.py: funciones para interacción con la base de datos (CRUD de modelos).
- regressionModel.db: base de datos SQLite con los modelos guardados.
- requirements.txt: dependencias del proyecto.
- tests/: scripts de pruebas unitarias e integración.
- README.md: este documento.

## Troubleshooting
- “Primero calcule los modelos” al graficar:
  - Causa: resultados no están en el estado compartido o la clave del método no coincide.
  - Solución: asegúrate de que calcular_modelos_callback guarde estado["resultados"], estado["xs"], estado["ys"], y que metodo_seleccionado sea una de las claves: "Lineal", "Exponencial", "Potencial", "Logaritmica", "Polinomial_2".

- La curva exponencial se ve como una línea segmentada:
  - Causa: pocos puntos X o datos que no siguen patrón exponencial (R² negativo).
  - Solución: genera un grid fino al graficar y verifica que y > 0. Considera usar escala log en y para inspección.

- Error de dominio (None en resultados de un método):
  - Exponencial: requiere y > 0.
  - Potencial: requiere x > 0 y y > 0.
  - Logarítmica: requiere x > 0.
  - Solución: corrige los datos de entrada o usa otro método.

- “Cantidad de X y y no coincide”:
  - Causa: distinto número de elementos parseados.
  - Solución: revisa separadores y vacíos en los campos.

- Backend TkAgg no carga:
  - Causa: entorno sin servidor gráfico.
  - Solución: usa entorno con GUI o ajusta el backend de matplotlib.

- Búsqueda/Edición en DB no funciona:
  - Causa: ruta/permiso a regressionModel.db o esquema distinto.
  - Solución: valida que regressionModel.db esté junto al ejecutable/App.py y que Queries.py use la ruta correcta.

## Pruebas
```bash
python3 test_operations.py      # Tests unitarios
python3 test_integration.py     # Tests de integración
```

## Descargas (Releases)
Descarga paquetes para Windows/Linux desde:
[Releases](https://github.com/steven-cl/LinearRegressionModel/releases/latest)

Para ejecutables:
1. Descarga el ZIP apropiado.
2. Descomprime.
3. Ejecuta `RegressionModel.exe` (Windows) o `RegressionModel` (Linux).
**No separes el ejecutable de `regressionModel.db`.**

## Contribuir
- Abre un Issue con descripción clara.
- Envía Pull Requests con tests y documentación.

## Licencia
GNU GENERAL PUBLIC LICENSE Version 3. Ver [LICENSE](LICENSE) para más detalles.

## Autor
Steven Castillo - [GitHub](https://github.com/steven-cl)
