# Estructura Modular de la Aplicación

## Descripción

Esta aplicación ha sido refactorizada en una estructura modular para mejorar la escalabilidad, legibilidad y mantenibilidad del código. La aplicación permite comparar dos enfoques de regresión sobre pares de datos (x, y):

1. **Regresión Lineal** usando scikit-learn
2. **Regresión Exponencial** y = a * e^(bx) usando linealización con ln(y)

## Estructura de Módulos

### 1. OperationsApp.py
**Propósito:** Contiene todas las operaciones matemáticas y de cálculo.

**Funciones principales:**
- `parse_numbers(text)`: Parsea texto con números separados por comas, espacios o saltos de línea
- `calcular_regresion_lineal(X, y)`: Calcula la regresión lineal y retorna métricas (R², MSE, RMSE)
- `calcular_regresion_exponencial(X, y)`: Calcula la regresión exponencial y retorna métricas
- `calcular_todos_modelos(xs, ys)`: Calcula ambos modelos y retorna un diccionario con todos los resultados

**Ventajas:**
- Separación clara de la lógica de negocio
- Funciones reutilizables y testables
- No depende de la interfaz gráfica

### 2. AppGUI.py
**Propósito:** Contiene todos los componentes de la interfaz gráfica.

**Clases:**
- `ScrollableFrame`: Frame con scroll vertical para la interfaz

**Funciones principales:**
- `crear_titulo(container)`: Crea el label de título
- `crear_inputs(container)`: Crea los campos de entrada para X e Y
- `crear_botones(container, ...)`: Crea los botones de la aplicación
- `crear_tabla_metodos(container, metodo_seleccionado)`: Crea la tabla de métodos y métricas
- `crear_grafico(container)`: Crea el canvas para el gráfico matplotlib
- `crear_label_info(container)`: Crea el label de información del modelo
- `inicializar_interfaz(master)`: Función principal que inicializa toda la interfaz
- `actualizar_tabla(rows, resultados)`: Actualiza la tabla con los resultados calculados
- `mostrar_grafico(ax, canvas, lbl_info, ...)`: Muestra el gráfico del modelo seleccionado
- `limpiar_interfaz(...)`: Limpia todos los datos de la interfaz

**Ventajas:**
- Separación de componentes de UI en funciones específicas
- Fácil de mantener y modificar
- Integración con OperationsApp para cálculos

### 3. App.py
**Propósito:** Punto de entrada principal de la aplicación.

**Funciones:**
- `main()`: Inicializa la ventana principal y la interfaz

**Ventajas:**
- Código minimalista y claro
- Fácil de ejecutar
- Punto único de entrada

## Cómo Ejecutar

```bash
python3 App.py
```

## Flujo de Trabajo

1. El usuario ejecuta `App.py`
2. `App.py` importa `AppGUI` e inicializa la interfaz
3. Cuando el usuario ingresa datos y presiona "Calcular Modelos":
   - `AppGUI` llama a `OperationsApp.parse_numbers()` para parsear los datos
   - `AppGUI` llama a `OperationsApp.calcular_todos_modelos()` para calcular las regresiones
   - `AppGUI.actualizar_tabla()` actualiza la UI con los resultados
4. Cuando el usuario presiona "Mostrar Gráfica":
   - `AppGUI.mostrar_grafico()` genera el gráfico usando los resultados almacenados
5. Cuando el usuario presiona "Limpiar":
   - `AppGUI.limpiar_interfaz()` resetea todos los componentes

## Funcionalidades

- ✓ Ingresar valores X e Y (soporta múltiples formatos: comas, espacios, saltos de línea)
- ✓ Calcular ambos modelos de regresión
- ✓ Mostrar métricas: R², MSE, RMSE y fórmula de cada modelo
- ✓ Resaltar en verde el modelo con menor RMSE
- ✓ Seleccionar un modelo y visualizar su gráfica
- ✓ Mostrar información detallada del modelo seleccionado debajo de la gráfica
- ✓ Limpiar todos los datos

## Tests

La aplicación incluye tests para verificar el funcionamiento:

```bash
# Test de operaciones matemáticas
python3 test_operations.py

# Test de integración
python3 test_integration.py
```

## Dependencias

- numpy
- scikit-learn
- matplotlib
- tkinter (incluido en Python)

## Notas Importantes

- La interfaz y lógica permanecen **sin cambios** respecto a la versión original
- Solo se ha refactorizado el código para hacerlo más modular y legible
- Todos los componentes mantienen la misma funcionalidad
- El archivo `app.py` original se mantiene para referencia
