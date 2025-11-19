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
import Queries

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


def search_models(container, txt_x, txt_y, id_session_var, btn_editar):
    """
    Crea la UI de búsqueda de modelos en la base de datos.

    Args:
        container: Contenedor donde se colocará la búsqueda
        txt_x: Widget de texto para valores X
        txt_y: Widget de texto para valores Y
        id_session_var: Variable IntVar para guardar el ID del modelo seleccionado
        btn_editar: Botón de editar que se habilitará al seleccionar un modelo

    Returns:
        Tupla (frame_search, entry_search) con el frame y el entry de búsqueda
    """
    frame_search = tk.LabelFrame(container, text="Buscar Modelo en Base de Datos")
    frame_search.pack(fill="x", padx=10, pady=5)

    # Entry para búsqueda
    entry_search = tk.Entry(frame_search, font=("Arial", 12))
    entry_search.pack(fill="x", padx=5, pady=5)

    # Frame scrollable para resultados
    results_frame = tk.Frame(frame_search, height=150)
    results_frame.pack(fill="both", expand=True, padx=5, pady=5)
    results_frame.pack_propagate(False)

    canvas_results = tk.Canvas(results_frame, height=150)
    scrollbar_results = tk.Scrollbar(
        results_frame, orient="vertical", command=canvas_results.yview
    )
    scrollable_results = tk.Frame(canvas_results)

    scrollable_results.bind(
        "<Configure>",
        lambda e: canvas_results.configure(scrollregion=canvas_results.bbox("all")),
    )

    canvas_results.create_window((0, 0), window=scrollable_results, anchor="nw")
    canvas_results.configure(yscrollcommand=scrollbar_results.set)

    canvas_results.pack(side="left", fill="both", expand=True)
    scrollbar_results.pack(side="right", fill="y")

    def update_search_results(*args):
        """Actualiza los resultados de búsqueda mientras el usuario escribe."""
        # Limpiar resultados previos
        for widget in scrollable_results.winfo_children():
            widget.destroy()

        search_text = entry_search.get()
        if not search_text.strip():
            return

        # Buscar modelos que coincidan
        results = Queries.search_models(search_text)

        if not results:
            lbl_no_results = tk.Label(
                scrollable_results,
                text="No se encontraron modelos",
                fg="gray",
                font=("Arial", 10, "italic"),
            )
            lbl_no_results.pack(pady=10)
            return

        # Mostrar cada resultado con botón "Utilizar"
        for model_id, model_name in results:
            frame_result = tk.Frame(scrollable_results)
            frame_result.pack(fill="x", padx=5, pady=2)

            lbl_name = tk.Label(
                frame_result, text=model_name, anchor="w", font=("Arial", 10)
            )
            lbl_name.pack(side="left", fill="x", expand=True)

            def use_model(mid=model_id, mname=model_name):
                """Carga el modelo seleccionado en los campos X e Y."""
                xy_data = Queries.get_model_xy_by_id(mid)
                if xy_data:
                    x_str, y_str = xy_data
                    txt_x.delete("1.0", tk.END)
                    txt_x.insert("1.0", x_str)
                    txt_y.delete("1.0", tk.END)
                    txt_y.insert("1.0", y_str)

                    # Guardar ID en variable de sesión
                    id_session_var.set(mid)

                    # Habilitar botón editar
                    btn_editar.config(state=tk.NORMAL)

                    messagebox.showinfo(
                        "Modelo Cargado",
                        f"Modelo '{mname}' (ID: {mid}) cargado exitosamente.",
                    )
                else:
                    messagebox.showerror("Error", "No se pudo cargar el modelo.")

            def delete_model(mid=model_id, mname=model_name):
                """Elimina el modelo de la base de datos con confirmación."""
                # Mostrar diálogo de confirmación
                result = messagebox.askyesno(
                    "Confirmar Eliminación",
                    f"¿Está seguro que desea eliminar el modelo '{mname}' (ID: {mid})?\n\n"
                    "Esta acción no se puede deshacer.",
                )

                if result:
                    try:
                        success = Queries.delete_model(mid)
                        if success:
                            # Si el modelo eliminado era el que estaba cargado, resetear
                            if id_session_var.get() == mid:
                                id_session_var.set(0)
                                btn_editar.config(state=tk.DISABLED)
                                txt_x.delete("1.0", tk.END)
                                txt_y.delete("1.0", tk.END)

                            messagebox.showinfo(
                                "Éxito",
                                f"Modelo '{mname}' (ID: {mid}) eliminado correctamente.",
                            )

                            # Actualizar resultados de búsqueda
                            update_search_results()
                        else:
                            messagebox.showerror(
                                "Error", f"No se pudo eliminar el modelo ID {mid}."
                            )
                    except Exception as e:
                        messagebox.showerror("Error", f"Error al eliminar: {e}")

            btn_delete = tk.Button(
                frame_result,
                text="Eliminar",
                command=delete_model,
                bg="#e74c3c",
                fg="white",
                width=10,
            )
            btn_delete.pack(side="right", padx=2)

            btn_use = tk.Button(
                frame_result,
                text="Utilizar",
                command=use_model,
                bg="#3498db",
                fg="white",
                width=10,
            )
            btn_use.pack(side="right", padx=2)

    # Vincular evento de escritura al entry
    entry_search.bind("<KeyRelease>", update_search_results)

    return frame_search, entry_search


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
        Tupla (txt_x, txt_y, frame_inputs) con los widgets de texto y su contenedor
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

    return txt_x, txt_y, frame_inputs


def crear_botones(
    container,
    calcular_callback,
    graficar_callback,
    limpiar_callback,
    guardar_callback,
    editar_callback,
):
    """
    Crea los botones de la aplicación.

    Args:
        container: Contenedor donde se colocarán los botones
        calcular_callback: Función a llamar al presionar "Calcular Modelos"
        graficar_callback: Función a llamar al presionar "Mostrar Gráfica"
        limpiar_callback: Función a llamar al presionar "Limpiar"
        guardar_callback: Función a llamar al presionar "Guardar"
        editar_callback: Función a llamar al presionar "Editar"

    Returns:
        Tupla (btn_guardar, btn_editar) con los botones de base de datos
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
        frame_btns, text="Limpiar", command=limpiar_callback, bg="#c0392b", fg="white"
    ).pack(side="left", padx=5)

    # Botones de base de datos a la derecha
    btn_editar = tk.Button(
        frame_btns,
        text="Editar",
        command=editar_callback,
        bg="#f39c12",
        fg="white",
        state=tk.DISABLED,
    )
    btn_editar.pack(side="right", padx=5)

    btn_guardar = tk.Button(
        frame_btns, text="Guardar", command=guardar_callback, bg="#16a085", fg="white"
    )
    btn_guardar.pack(side="right", padx=5)

    return btn_guardar, btn_editar


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
        ("Potencial", "Regresión Potencial"),
        ("Logaritmica", "Regresión Logarítmica"),
        ("Polinomial_2", "Regresión Polinomial Grado 2"),
    ]

    for i, (key, name) in enumerate(nombres, start=1):
        rb = tk.Radiobutton(frame_metodos, variable=metodo_seleccionado, value=key)
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
            elif key == "Exponencial":
                comps["formula"].config(text=f"y = {r['a']:.4f} * e^{r['b']:.4f}x")
            elif key == "Potencial":
                comps["formula"].config(text=f"y = {r['a']:.4f} * x^{r['b']:.4f}")
            elif key == "Logaritmica":
                comps["formula"].config(text=f"y = {r['a']:.4f} + {r['b']:.4f}*ln(x)")
            elif key == "Polinomial_2":
                comps["formula"].config(
                    text=f"y = {r['a']:.4f} + {r['b']:.4f}x + {r['c']:.4f}x²"
                )

            comps["name"].config(fg="green" if key == mejor_key else "black")
        else:
            comps["r2"].config(text="-")
            comps["rmse"].config(text="-")
            comps["mse"].config(text="-")
            comps["formula"].config(text="-")
            comps["name"].config(fg="black")


def mostrar_grafico(ax, canvas, lbl_info, metodo, resultados, xs, ys):
    """
    Muestra el gráfico del modelo seleccionado junto con su información.

    Args:
        ax: Ejes del gráfico matplotlib
        canvas: Canvas de matplotlib
        lbl_info: Label donde se mostrará la información
        metodo: Nombre del método seleccionado
        resultados: Diccionario con los resultados de los métodos
        xs: Lista de valores X
        ys: Lista de valores y
    """
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
    elif metodo == "Exponencial":
        y_line = r["a"] * np.exp(r["b"] * X_grid)
        formula = f"y = {r['a']:.6f} * e^{r['b']:.6f}x"
    elif metodo == "Potencial":
        y_line = r["a"] * np.power(X_grid, r["b"])
        formula = f"y = {r['a']:.6f} * x^{r['b']:.6f}"
    elif metodo == "Logaritmica":
        y_line = r["a"] + r["b"] * np.log(X_grid)
        formula = f"y = {r['a']:.6f} + {r['b']:.6f}*ln(x)"
    elif metodo == "Polinomial_2":
        y_line = r["a"] + r["b"] * X_grid + r["c"] * X_grid**2
        formula = f"y = {r['a']:.6f} + {r['b']:.6f}x + {r['c']:.6f}x²"

    ax.plot(X_grid, y_line, color="#e74c3c", label="Modelo")  # type: ignore

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
        f"Fórmula: {formula}\n"  # type: ignore
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
    master.title("Modelos de Regresión")
    master.geometry("900x750")

    # Variables de estado
    resultados = {}
    metodo_seleccionado = tk.StringVar(value="Lineal")
    id_session = tk.IntVar(value=0)  # 0 significa que no hay modelo seleccionado

    # Crear scroll frame
    scroll = ScrollableFrame(master)
    scroll.pack(fill="both", expand=True)
    container = scroll.interior

    # Crear componentes en el orden correcto
    lbl_titulo = crear_titulo(container)

    # Crear inputs primero (necesarios para search_models)
    txt_x, txt_y, frame_inputs = crear_inputs(container)

    # Crear placeholder para btn_editar
    btn_editar = None

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

        # Mostrar advertencias para los modelos que no son aplicables
        advertencias = []
        if resultados_calc["Exponencial"] is None:
            advertencias.append("Exponencial (todos los y deben ser > 0)")
        if resultados_calc["Potencial"] is None:
            advertencias.append("Potencial (todos los x e y deben ser > 0)")
        if resultados_calc["Logaritmica"] is None:
            advertencias.append("Logarítmica (todos los x deben ser > 0)")

        if advertencias:
            mensaje = "Métodos omitidos:\n- " + "\n- ".join(advertencias)
            messagebox.showwarning("Advertencia", mensaje)

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
        limpiar_interfaz(
            txt_x, txt_y, rows, ax, canvas, lbl_info, lbl_titulo, resultados
        )
        # Limpiar id_session y deshabilitar botón editar
        id_session.set(0)
        if btn_editar:
            btn_editar.config(state=tk.DISABLED)

    def guardar_callback():
        """Guarda un nuevo modelo en la base de datos."""
        # Obtener valores actuales de X e Y
        try:
            xs = OperationsApp.parse_numbers(txt_x.get("1.0", tk.END))
            ys = OperationsApp.parse_numbers(txt_y.get("1.0", tk.END))
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")
            return

        if len(xs) != len(ys) or len(xs) < 2:
            messagebox.showerror("Error", "Debe proporcionar datos válidos para X e Y.")
            return

        # Mostrar ventana emergente para pedir el nombre del modelo
        popup = tk.Toplevel(master)
        popup.title("Guardar Modelo")
        popup.geometry("350x150")
        popup.grab_set()  # Hacer modal

        tk.Label(popup, text="Ingrese el nombre del modelo:", font=("Arial", 11)).pack(
            pady=10
        )

        entry_name = tk.Entry(popup, font=("Arial", 11), width=30)
        entry_name.pack(pady=5)
        entry_name.focus()

        frame_btns_popup = tk.Frame(popup)
        frame_btns_popup.pack(pady=15)

        def save_model():
            model_name = entry_name.get().strip()
            if not model_name:
                messagebox.showerror(
                    "Error", "El nombre del modelo no puede estar vacío.", parent=popup
                )
                return

            try:
                # Convertir listas a strings separados por comas
                x_str = ",".join(str(x) for x in xs)
                y_str = ",".join(str(y) for y in ys)

                # Insertar nuevo modelo
                new_id = Queries.insert_model(model_name, x_str, y_str)

                # Actualizar id_session con el nuevo ID
                id_session.set(new_id)

                # Habilitar botón editar
                if btn_editar:
                    btn_editar.config(state=tk.NORMAL)

                popup.destroy()
                messagebox.showinfo(
                    "Éxito", f"Modelo '{model_name}' guardado con ID {new_id}."
                )
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo guardar el modelo: {e}", parent=popup
                )

        def cancel_save():
            popup.destroy()

        tk.Button(
            frame_btns_popup,
            text="Guardar",
            command=save_model,
            bg="#16a085",
            fg="white",
            width=10,
        ).pack(side="left", padx=5)
        tk.Button(
            frame_btns_popup,
            text="Cancelar",
            command=cancel_save,
            bg="#95a5a6",
            fg="white",
            width=10,
        ).pack(side="left", padx=5)

        # Permitir guardar con Enter
        entry_name.bind("<Return>", lambda e: save_model())

    def editar_callback():
        """Edita el modelo actualmente seleccionado (id_session)."""
        current_id = id_session.get()
        if current_id == 0:
            messagebox.showwarning(
                "Advertencia", "No hay ningún modelo seleccionado para editar."
            )
            return

        # Obtener valores actuales de X e Y
        try:
            xs = OperationsApp.parse_numbers(txt_x.get("1.0", tk.END))
            ys = OperationsApp.parse_numbers(txt_y.get("1.0", tk.END))
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")
            return

        if len(xs) != len(ys) or len(xs) < 2:
            messagebox.showerror("Error", "Debe proporcionar datos válidos para X e Y.")
            return

        # Confirmar edición
        result = messagebox.askyesno(
            "Confirmar Edición", f"¿Desea actualizar el modelo con ID {current_id}?"
        )
        if not result:
            return

        try:
            # Convertir listas a strings separados por comas
            x_str = ",".join(str(x) for x in xs)
            y_str = ",".join(str(y) for y in ys)

            # Actualizar modelo existente
            success = Queries.update_model_xy(current_id, x_str, y_str)

            if success:
                messagebox.showinfo(
                    "Éxito", f"Modelo ID {current_id} actualizado correctamente."
                )
            else:
                messagebox.showerror(
                    "Error", f"No se pudo actualizar el modelo ID {current_id}."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {e}")

    # Crear botones (retorna los botones de DB)
    btn_guardar, btn_editar = crear_botones(
        container,
        calcular_modelos_callback,
        mostrar_grafica_callback,
        limpiar_callback,
        guardar_callback,
        editar_callback,
    )

    # Ahora crear la búsqueda (necesita btn_editar y los txt_x, txt_y)
    frame_search, entry_search = search_models(
        container, txt_x, txt_y, id_session, btn_editar
    )

    # Reordenar: búsqueda debe estar después del título y antes de los inputs
    frame_search.pack_forget()
    frame_search.pack(after=lbl_titulo, fill="x", padx=10, pady=5)

    # Los inputs deben estar después de la búsqueda
    frame_inputs.pack_forget()  # frame_inputs que contiene txt_x y txt_y
    frame_inputs.pack(after=frame_search, fill="x", padx=10)

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
        "id_session": id_session,
        "btn_editar": btn_editar,
        "btn_guardar": btn_guardar,
    }
