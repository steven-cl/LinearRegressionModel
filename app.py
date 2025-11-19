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
from tkinter import messagebox
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use("TkAgg")


class ScrollableFrame(tk.Frame):
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


class RegressionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Regresión Lineal y Exponencial")
        self.master.geometry("900x650")

        self.resultados = {}
        self.metodo_seleccionado = tk.StringVar(value="linear_sklearn")

        self.scroll = ScrollableFrame(master)
        self.scroll.pack(fill="both", expand=True)
        self.container = self.scroll.interior

        self._crear_widgets()

    def _crear_widgets(self):
        self.lbl_titulo = tk.Label(
            self.container,
            text="Modelos (n pares de datos)",
            font=("Arial", 16, "bold"),
        )
        self.lbl_titulo.pack(pady=8)

        frame_inputs = tk.Frame(self.container)
        frame_inputs.pack(fill="x", padx=10)

        frame_x = tk.LabelFrame(frame_inputs, text="Valores X")
        frame_x.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.txt_x = tk.Text(frame_x, height=10)
        self.txt_x.pack(fill="both", expand=True, padx=5, pady=5)

        frame_y = tk.LabelFrame(frame_inputs, text="Valores y")
        frame_y.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.txt_y = tk.Text(frame_y, height=10)
        self.txt_y.pack(fill="both", expand=True, padx=5, pady=5)

        frame_btns = tk.Frame(self.container)
        frame_btns.pack(fill="x", padx=10, pady=5)

        tk.Button(
            frame_btns,
            text="Calcular Modelos",
            command=self.calcular_modelos,
            bg="#2e86de",
            fg="white",
        ).pack(side="left", padx=5)
        tk.Button(
            frame_btns,
            text="Mostrar Gráfica",
            command=self.mostrar_grafica,
            bg="#27ae60",
            fg="white",
        ).pack(side="left", padx=5)
        tk.Button(
            frame_btns, text="Limpiar", command=self.limpiar, bg="#c0392b", fg="white"
        ).pack(side="left", padx=5)

        frame_metodos = tk.LabelFrame(self.container, text="Métodos y Métricas")
        frame_metodos.pack(fill="x", padx=10, pady=5)

        headers = ["Seleccionar", "Método", "R2", "RMSE", "MSE", "Fórmula"]
        for c, h in enumerate(headers):
            tk.Label(frame_metodos, text=h, font=("Arial", 10, "bold")).grid(
                row=0, column=c, padx=5, pady=3
            )

        self.rows = {}
        nombres = [
            ("linear_sklearn", "Regresión Lineal (Sklearn)"),
            ("exponential", "Regresión Exponencial"),
        ]
        for i, (key, name) in enumerate(nombres, start=1):
            rb = tk.Radiobutton(
                frame_metodos, variable=self.metodo_seleccionado, value=key
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
            self.rows[key] = {
                "r2": lbl_r2,
                "rmse": lbl_rmse,
                "mse": lbl_mse,
                "formula": lbl_formula,
                "name": lbl_name,
            }

        frame_graf = tk.LabelFrame(self.container, text="Gráfica")
        frame_graf.pack(fill="both", expand=True, padx=10, pady=5)

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("y")
        self.ax.set_title("Gráfico")
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_graf)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.lbl_info = tk.Label(
            self.container,
            text="Información del modelo seleccionado.",
            font=("Arial", 11),
        )
        self.lbl_info.pack(fill="x", padx=10, pady=5)

    def limpiar(self):
        self.txt_x.delete("1.0", tk.END)
        self.txt_y.delete("1.0", tk.END)
        for comps in self.rows.values():
            comps["r2"].config(text="-")
            comps["rmse"].config(text="-")
            comps["mse"].config(text="-")
            comps["formula"].config(text="-")
            comps["name"].config(fg="black")
        self.resultados.clear()
        self.ax.clear()
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("y")
        self.ax.set_title("Gráfico")
        self.canvas.draw()
        self.lbl_info.config(text="Información del modelo seleccionado.")
        self.lbl_titulo.config(text="Modelos (n pares de datos)")

    def parse_numbers(self, text):
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

    def calcular_modelos(self):
        try:
            xs = self.parse_numbers(self.txt_x.get("1.0", tk.END))
            ys = self.parse_numbers(self.txt_y.get("1.0", tk.END))
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
        self.lbl_titulo.config(text=f"Modelos ({n} pares de datos)")

        X = np.array(xs).reshape(-1, 1)
        y = np.array(ys)

        resultados = {}

        def pack_pred(y_true, y_pred, extra):
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_true, y_pred)
            extra.update({"mse": mse, "rmse": rmse, "r2": r2, "y_pred": y_pred})
            return extra

        # 1. Lineal (sklearn)
        lr = LinearRegression()
        lr.fit(X, y)
        y_pred_lin = lr.predict(X)
        resultados["linear_sklearn"] = pack_pred(
            y, y_pred_lin, {"intercept": lr.intercept_, "coef": lr.coef_[0]}
        )

        # 2. Exponencial y = a * e^{b x}  => ln(y) = ln(a) + b x
        if np.any(y <= 0):
            messagebox.showwarning(
                "Advertencia", "Exponencial omitida: todos los y deben ser > 0."
            )
        else:
            Y_log = np.log(y)
            lr_exp = LinearRegression()
            lr_exp.fit(X, Y_log)
            b = lr_exp.coef_[0]
            a = np.exp(lr_exp.intercept_)
            y_pred_exp = a * np.exp(b * X.flatten())
            resultados["exponential"] = pack_pred(y, y_pred_exp, {"a": a, "b": b})

        self.resultados = resultados
        self._actualizar_tabla()
        messagebox.showinfo("Éxito", "Modelos calculados.")

    def _actualizar_tabla(self):
        if not self.resultados:
            return
        mejor_key = min(
            self.resultados.keys(), key=lambda k: self.resultados[k]["rmse"]
        )
        for key, comps in self.rows.items():
            if key in self.resultados:
                r = self.resultados[key]
                comps["r2"].config(text=f"{r['r2']:.4f}")
                comps["rmse"].config(text=f"{r['rmse']:.4f}")
                comps["mse"].config(text=f"{r['mse']:.4f}")
                if key == "linear_sklearn":
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

    def mostrar_grafica(self):
        metodo = self.metodo_seleccionado.get()
        if metodo not in self.resultados:
            messagebox.showerror("Error", "Primero calcule los modelos.")
            return
        try:
            xs = self.parse_numbers(self.txt_x.get("1.0", tk.END))
            ys = self.parse_numbers(self.txt_y.get("1.0", tk.END))
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        if len(xs) != len(ys) or len(xs) < 2:
            messagebox.showerror("Error", "Datos inválidos.")
            return

        X = np.array(xs)
        y = np.array(ys)
        r = self.resultados[metodo]

        self.ax.clear()
        self.ax.scatter(X, y, color="#2980b9", label="Datos")

        orden = np.argsort(X)
        X_sorted = X[orden]

        if metodo == "linear_sklearn":
            y_line = r["intercept"] + r["coef"] * X_sorted
            formula = f"y = {r['intercept']:.6f} + {r['coef']:.6f}x"
        else:
            y_line = r["a"] * np.exp(r["b"] * X_sorted)
            formula = f"y = {r['a']:.6f} * e^{r['b']:.6f}x"

        self.ax.plot(X_sorted, y_line, color="#e74c3c", label="Modelo")
        self.ax.set_title("Modelo Seleccionado")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("y")
        self.ax.legend()
        self.canvas.draw()

        info = (
            f"Método: {metodo}\n"
            f"Fórmula: {formula}\n"
            f"R2: {r['r2']:.6f} | MSE: {r['mse']:.6f} | RMSE: {r['rmse']:.6f}"
        )
        self.lbl_info.config(text=info)


def main():
    root = tk.Tk()
    app = RegressionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
