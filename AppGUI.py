"""
Módulo de interfaz gráfica para la aplicación de regresión.
Contiene todas las funciones relacionadas con la interfaz de usuario.
"""

import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import OperationsApp

matplotlib.use("TkAgg")


class ScrollableFrame(tk.Frame):
    """
    Frame con scroll vertical para la interfaz.
    """
    def __init__(self, master):
        super().__init__(master)
        self.canvas = tk.Canvas(self, borderwidth=0)
        vscroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.interior = tk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(
            (0, 0), window=self.interior, anchor="nw"
        )
        self.interior.bind("<Configure>", self._configure_interior)
        self.canvas.bind("<Configure>", self._configure_canvas)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all(
            "<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units")
        )
        self.canvas.bind_all(
            "<Button-5>", lambda e: self.canvas.yview_scroll(1, "units")
        )

    def _configure_interior(self, _):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _configure_canvas(self, event):
        self.canvas.itemconfig(self.interior_id, width=event.width)

    def _on_mousewheel(self, event):
        delta = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(delta, "units")


def crear_titulo(container):
    """
    Crea el label de título de la aplicación.
    
    Args:
        container: Contenedor donde se colocará el título
        
    Returns:
        Label del título
    """
    lbl_titulo = tk.Label(
        container,
        text="Modelos (n pares de datos)",
        font=("Arial", 16, "bold"),
    )
    lbl_titulo.pack(pady=8)
    return lbl_titulo


def crear_inputs(container):
    """
    Crea los campos de entrada para X e Y.
    
    Args:
        container: Contenedor donde se colocarán los inputs
        
    Returns:
        Tupla (txt_x, txt_y) con los widgets de texto
    """
    frame_inputs = tk.Frame(container)
    frame_inputs.pack(fill="x", padx=10)

    frame_x = tk.LabelFrame(frame_inputs, text="Valores X")
    frame_x.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    txt_x = tk.Text(frame_x, height=10)
    txt_x.pack(fill="both", expand=True, padx=5, pady=5)

    frame_y = tk.LabelFrame(frame_inputs, text="Valores y")
    frame_y.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    txt_y = tk.Text(frame_y, height=10)
    txt_y.pack(fill="both", expand=True, padx=5, pady=5)
    
    return txt_x, txt_y


def crear_botones(container, calcular_callback, graficar_callback, limpiar_callback):
    """
    Crea los botones de la aplicación.
    
    Args:
        container: Contenedor donde se colocarán los botones
        calcular_callback: Función a llamar al presionar "Calcular Modelos"
        graficar_callback: Función a llamar al presionar "Mostrar Gráfica"
        limpiar_callback: Función a llamar al presionar "Limpiar"
    """
    frame_btns = tk.Frame(container)
    frame_btns.pack(fill="x", padx=10, pady=5)

    tk.Button(
        frame_btns,
        text="Calcular Modelos",
        command=calcular_callback,
        bg="#2e86de",
        fg="white",
    ).pack(side="left", padx=5)
    
    tk.Button(
        frame_btns,
        text="Mostrar Gráfica",
        command=graficar_callback,
        bg="#27ae60",
        fg="white",
    ).pack(side="left", padx=5)
    
    tk.Button(
        frame_btns, 
        text="Limpiar", 
        command=limpiar_callback, 
        bg="#c0392b", 
        fg="white"
    ).pack(side="left", padx=5)


def crear_tabla_metodos(container, metodo_seleccionado):
    """
    Crea la tabla de métodos y métricas.
    
    Args:
        container: Contenedor donde se colocará la tabla
        metodo_seleccionado: Variable StringVar para el radiobutton
        
    Returns:
        Diccionario con los labels de cada método
    """
    frame_metodos = tk.LabelFrame(container, text="Métodos y Métricas")
    frame_metodos.pack(fill="x", padx=10, pady=5)

    headers = ["Seleccionar", "Método", "R2", "RMSE", "MSE", "Fórmula"]
    for c, h in enumerate(headers):
        tk.Label(frame_metodos, text=h, font=("Arial", 10, "bold")).grid(
            row=0, column=c, padx=5, pady=3
        )

    rows = {}
    nombres = [
        ("Lineal", "Regresión Lineal"),
        ("Exponencial", "Regresión Exponencial"),
    ]
    
    for i, (key, name) in enumerate(nombres, start=1):
        rb = tk.Radiobutton(
            frame_metodos, variable=metodo_seleccionado, value=key
        )
        rb.grid(row=i, column=0)
        lbl_name = tk.Label(frame_metodos, text=name, anchor="w")
        lbl_name.grid(row=i, column=1, sticky="w")
        lbl_r2 = tk.Label(frame_metodos, text="-")
        lbl_r2.grid(row=i, column=2)
        lbl_rmse = tk.Label(frame_metodos, text="-")
        lbl_rmse.grid(row=i, column=3)
        lbl_mse = tk.Label(frame_metodos, text="-")
        lbl_mse.grid(row=i, column=4)
        lbl_formula = tk.Label(frame_metodos, text="-", anchor="w")
        lbl_formula.grid(row=i, column=5, sticky="w")
        rows[key] = {
            "r2": lbl_r2,
            "rmse": lbl_rmse,
            "mse": lbl_mse,
            "formula": lbl_formula,
            "name": lbl_name,
        }
    
    return rows


def crear_grafico(container):
    """
    Crea el canvas para el gráfico.
    
    Args:
        container: Contenedor donde se colocará el gráfico
        
    Returns:
        Tupla (fig, ax, canvas) con la figura, ejes y canvas de matplotlib
    """
    frame_graf = tk.LabelFrame(container, text="Gráfica")
    frame_graf.pack(fill="both", expand=True, padx=10, pady=5)

    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_xlabel("X")
    ax.set_ylabel("y")
    ax.set_title("Gráfico")
    canvas = FigureCanvasTkAgg(fig, master=frame_graf)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    return fig, ax, canvas


def crear_label_info(container):
    """
    Crea el label de información del modelo seleccionado.
    
    Args:
        container: Contenedor donde se colocará el label
        
    Returns:
        Label de información
    """
    lbl_info = tk.Label(
        container,
        text="Información del modelo seleccionado.",
        font=("Arial", 11),
    )
    lbl_info.pack(fill="x", padx=10, pady=5)
    return lbl_info


def actualizar_tabla(rows, resultados):
    """
    Actualiza la tabla de métricas con los resultados calculados.
    Resalta en verde el método con menor RMSE.
    
    Args:
        rows: Diccionario con los labels de cada método
        resultados: Diccionario con los resultados de cada método
    """
    if not resultados:
        return
    
    # Encontrar el mejor método (menor RMSE)
    metodos_validos = {k: v for k, v in resultados.items() if v is not None}
    if not metodos_validos:
        return
        
    mejor_key = min(metodos_validos.keys(), key=lambda k: metodos_validos[k]["rmse"])
    
    for key, comps in rows.items():
        if key in resultados and resultados[key] is not None:
            r = resultados[key]
            comps["r2"].config(text=f"{r['r2']:.4f}")
            comps["rmse"].config(text=f"{r['rmse']:.4f}")
            comps["mse"].config(text=f"{r['mse']:.4f}")
            
            if key == "Lineal":
                comps["formula"].config(
                    text=f"y = {r['intercept']:.4f} + {r['coef']:.4f}x"
                )
            else:
                comps["formula"].config(text=f"y = {r['a']:.4f} * e^{r['b']:.4f}x")
            
            comps["name"].config(fg="green" if key == mejor_key else "black")
        else:
            comps["r2"].config(text="-")
            comps["rmse"].config(text="-")
            comps["mse"].config(text="-")
            comps["formula"].config(text="-")
            comps["name"].config(fg="black")


def mostrar_grafico(ax, canvas, lbl_info, metodo, resultados, xs, ys):
    if metodo not in resultados or resultados[metodo] is None:
        messagebox.showerror("Error", "Primero calcule los modelos.")
        return False

    X = np.array(xs)
    y = np.array(ys)
    r = resultados[metodo]

    ax.clear()
    ax.scatter(X, y, color="#2980b9", label="Datos")

    # Grid fino para suavizar la curva
    x_min, x_max = X.min(), X.max()
    X_grid = np.linspace(x_min, x_max, 200)

    if metodo == "Lineal":
        y_line = r["intercept"] + r["coef"] * X_grid
        formula = f"y = {r['intercept']:.6f} + {r['coef']:.6f}x"
    else:  # Exponencial
        y_line = r["a"] * np.exp(r["b"] * X_grid)
        formula = f"y = {r['a']:.6f} * e^{r['b']:.6f}x"

    ax.plot(X_grid, y_line, color="#e74c3c", label="Modelo")

    ax.set_title("Modelo Seleccionado")
    ax.set_xlabel("X")
    ax.set_ylabel("y")
    ax.legend()

    # Si la diferencia de magnitudes es muy grande, puedes activar escala log en y (opcional):
    if y.max() / max(y.min(), 1e-9) > 100:  # heurística
        ax.set_yscale("log")

    canvas.draw()

    info = (
        f"Método: {metodo}\n"
        f"Fórmula: {formula}\n"
        f"R2: {r['r2']:.6f} | MSE: {r['mse']:.6f} | RMSE: {r['rmse']:.6f}"
    )
    lbl_info.config(text=info)
    return True


def limpiar_interfaz(txt_x, txt_y, rows, ax, canvas, lbl_info, lbl_titulo, resultados):
    """
    Limpia todos los datos de la interfaz.
    
    Args:
        txt_x: Widget de texto para valores X
        txt_y: Widget de texto para valores y
        rows: Diccionario con los labels de cada método
        ax: Ejes del gráfico matplotlib
        canvas: Canvas de matplotlib
        lbl_info: Label de información
        lbl_titulo: Label del título
        resultados: Diccionario de resultados (se limpiará)
    """
    txt_x.delete("1.0", tk.END)
    txt_y.delete("1.0", tk.END)
    
    for comps in rows.values():
        comps["r2"].config(text="-")
        comps["rmse"].config(text="-")
        comps["mse"].config(text="-")
        comps["formula"].config(text="-")
        comps["name"].config(fg="black")
    
    resultados.clear()
    
    ax.clear()
    ax.set_xlabel("X")
    ax.set_ylabel("y")
    ax.set_title("Gráfico")
    canvas.draw()
    
    lbl_info.config(text="Información del modelo seleccionado.")
    lbl_titulo.config(text="Modelos (n pares de datos)")


def inicializar_interfaz(master):
    """
    Inicializa toda la interfaz de la aplicación.
    
    Args:
        master: Ventana principal de Tkinter
        
    Returns:
        Diccionario con todos los componentes de la interfaz
    """
    master.title("Regresión Lineal y Exponencial")
    master.geometry("900x650")

    # Variables de estado
    resultados = {}
    metodo_seleccionado = tk.StringVar(value="Lineal")

    # Crear scroll frame
    scroll = ScrollableFrame(master)
    scroll.pack(fill="both", expand=True)
    container = scroll.interior

    # Crear componentes
    lbl_titulo = crear_titulo(container)
    txt_x, txt_y = crear_inputs(container)
    
    # Definir callbacks que usan OperationsApp
    def calcular_modelos_callback():
        try:
            xs = OperationsApp.parse_numbers(txt_x.get("1.0", tk.END))
            ys = OperationsApp.parse_numbers(txt_y.get("1.0", tk.END))
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        if len(xs) != len(ys):
            messagebox.showerror("Error", "Cantidad de X y y no coincide.")
            return
        if len(xs) < 2:
            messagebox.showerror("Error", "Se requieren al menos 2 pares.")
            return

        n = len(xs)
        lbl_titulo.config(text=f"Modelos ({n} pares de datos)")

        # Calcular todos los modelos usando OperationsApp
        resultados_calc = OperationsApp.calcular_todos_modelos(xs, ys)
        
        # Mostrar advertencia si exponencial no es aplicable
        if resultados_calc["Exponencial"] is None:
            messagebox.showwarning(
                "Advertencia", "Exponencial omitida: todos los y deben ser > 0."
            )
        
        resultados.clear()
        resultados.update(resultados_calc)
        actualizar_tabla(rows, resultados)
        messagebox.showinfo("Éxito", "Modelos calculados.")

    def mostrar_grafica_callback():
        metodo = metodo_seleccionado.get()
        try:
            xs = OperationsApp.parse_numbers(txt_x.get("1.0", tk.END))
            ys = OperationsApp.parse_numbers(txt_y.get("1.0", tk.END))
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        if len(xs) != len(ys) or len(xs) < 2:
            messagebox.showerror("Error", "Datos inválidos.")
            return
        
        mostrar_grafico(ax, canvas, lbl_info, metodo, resultados, xs, ys)

    def limpiar_callback():
        limpiar_interfaz(txt_x, txt_y, rows, ax, canvas, lbl_info, lbl_titulo, resultados)

    crear_botones(container, calcular_modelos_callback, mostrar_grafica_callback, limpiar_callback)
    rows = crear_tabla_metodos(container, metodo_seleccionado)
    fig, ax, canvas = crear_grafico(container)
    lbl_info = crear_label_info(container)

    return {
        "resultados": resultados,
        "metodo_seleccionado": metodo_seleccionado,
        "txt_x": txt_x,
        "txt_y": txt_y,
        "rows": rows,
        "fig": fig,
        "ax": ax,
        "canvas": canvas,
        "lbl_info": lbl_info,
        "lbl_titulo": lbl_titulo,
    }
