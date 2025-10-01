"""
GUI application to compare several approaches to simple linear regression on a set
of (x, y) numeric pairs. Implementations included:
- scikit-learn LinearRegression
- Closed-form Normal Equation
- Batch Gradient Descent (implemented manually)
- Stochastic Gradient Descent (scikit-learn SGDRegressor, adapted back to original scale)

The interface lets the user:
1. Paste/enter X and y values (comma, whitespace, or newline separated).
2. Compute all models and show evaluation metrics (R2, MSE, RMSE).
3. Select a model and visualize the regression line against the raw data.
4. Identify (highlight) the model with the lowest RMSE.
"""

import tkinter as tk
from tkinter import messagebox
import numpy as np
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, Lasso, ElasticNet

# Use TkAgg backend for embedding matplotlib in Tkinter
matplotlib.use("TkAgg")


class ScrollableFrame(tk.Frame):
    """
    A vertically scrollable container for embedding arbitrary widgets.
    Creates a Canvas + interior Frame pattern and handles mouse wheel events.
    """

    def __init__(self, master):
        super().__init__(master)
        self.canvas = tk.Canvas(self, borderwidth=0)
        vscroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vscroll.set)

        # Layout scroll + canvas
        vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Interior frame where actual content is placed
        self.interior = tk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")

        # Bind resize events to update scroll region / width
        self.interior.bind("<Configure>", self._configure_interior)
        self.canvas.bind("<Configure>", self._configure_canvas)

        # Mouse wheel support (Windows / Linux)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Extra events (some X11 systems use Button-4/5)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _configure_interior(self, _):
        """Update scrollable region when interior changes size."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _configure_canvas(self, event):
        """Ensure interior frame width tracks the canvas width."""
        self.canvas.itemconfig(self.interior_id, width=event.width)

    def _on_mousewheel(self, event):
        """Translate mouse wheel delta into vertical scroll."""
        delta = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(delta, "units")


class RegressionApp:
    """
    Main application class encapsulating:
    - Data parsing
    - Model training for four regression approaches
    - Metrics computation and display
    - Plotting selected model
    """

    def __init__(self, master):
        self.master = master
        self.master.title("Regresión Lineal Simple - Comparador de Métodos")
        self.master.geometry("1150x750")

        # Will store model results keyed by method identifier
        self.resultados = {}
        # Selected method for plotting
        self.metodo_seleccionado = tk.StringVar(value="linear_sklearn")

        # Scrollable root container
        self.scroll = ScrollableFrame(master)
        self.scroll.pack(fill="both", expand=True)
        self.container = self.scroll.interior

        self._crear_widgets()

    def _crear_widgets(self):
        """Create and layout all GUI widgets."""
        self.lbl_titulo = tk.Label(
            self.container,
            text="Modelo de Regresión Lineal (n pares de datos)",
            font=("Arial", 16, "bold")
        )
        self.lbl_titulo.pack(pady=8)

        # Input frames
        frame_inputs = tk.Frame(self.container)
        frame_inputs.pack(fill="x", padx=10)

        # X values text box
        frame_x = tk.LabelFrame(frame_inputs, text="Valores X (separados por coma o salto de línea)")
        frame_x.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.txt_x = tk.Text(frame_x, height=12)
        self.txt_x.pack(fill="both", expand=True, padx=5, pady=5)

        # y values text box
        frame_y = tk.LabelFrame(frame_inputs, text="Valores y (separados por coma o salto de línea)")
        frame_y.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.txt_y = tk.Text(frame_y, height=12)
        self.txt_y.pack(fill="both", expand=True, padx=5, pady=5)
        
        if not hasattr(self, "alpha_var"):
            self.alpha_var = tk.StringVar(value="1.0")
            frame_alpha = tk.Frame(self.container)
            frame_alpha.pack(fill="x", padx=10, pady=(0, 5))
            tk.Label(frame_alpha, text="Alpha (solo Ridge, Lasso y Elastic Net):").pack(side="left")
            self.alpha_entry = tk.Entry(frame_alpha, textvariable=self.alpha_var, width=10)
            self.alpha_entry.pack(side="left", padx=5)

        # Buttons
        frame_btns = tk.Frame(self.container)
        frame_btns.pack(fill="x", padx=10, pady=5)

        tk.Button(
            frame_btns,
            text="Calcular Modelos",
            command=self.calcular_modelos,
            bg="#2e86de",
            fg="white"
        ).pack(side="left", padx=5)

        tk.Button(
            frame_btns,
            text="Mostrar Gráfica del Método Seleccionado",
            command=self.mostrar_grafica,
            bg="#27ae60",
            fg="white"
        ).pack(side="left", padx=5)

        tk.Button(
            frame_btns,
            text="Limpiar",
            command=self.limpiar,
            bg="#c0392b",
            fg="white"
        ).pack(side="left", padx=5)

        # Methods + metrics table
        frame_metodos = tk.LabelFrame(self.container, text="Métodos y Métricas")
        frame_metodos.pack(fill="x", padx=10, pady=5)

        headers = ["Seleccionar", "Método", "R2", "RMSE", "MSE", "Fórmula"]
        for c, h in enumerate(headers):
            tk.Label(frame_metodos, text=h, font=("Arial", 10, "bold")).grid(row=0, column=c, padx=5, pady=3)

        # Row widgets registry
        self.rows = {}
        nombres = [
            ("linear_sklearn", "LinearRegression (Sklearn)"),
            ("normal_eq", "Ecuación Normal"),
            ("grad_desc", "Descenso de Gradiente por lotes                   "),
            ("sgd", "Descenso de Gradiente Estocástico"),
            ("svd", "SVD"),
            ("qr", "QR"),
            ("lu", "LU"),
            ("ridge", "Ridge"), 
            ("lasso", "Lasso"),
            ("elastic_net", "Elastic Net")
        ]
        for i, (key, name) in enumerate(nombres, start=1):
            rb = tk.Radiobutton(frame_metodos, variable=self.metodo_seleccionado, value=key)
            rb.grid(row=i, column=0)
            lbl_name = tk.Label(frame_metodos, text=name, anchor="w")
            lbl_name.grid(row=i, column=1, sticky="w")
            lbl_r2 = tk.Label(frame_metodos, text="-"); lbl_r2.grid(row=i, column=2)
            lbl_rmse = tk.Label(frame_metodos, text="-"); lbl_rmse.grid(row=i, column=3)
            lbl_mse = tk.Label(frame_metodos, text="-"); lbl_mse.grid(row=i, column=4)
            lbl_formula = tk.Label(frame_metodos, text="-", anchor="w"); lbl_formula.grid(row=i, column=5, sticky="w")
            self.rows[key] = {
                "r2": lbl_r2,
                "rmse": lbl_rmse,
                "mse": lbl_mse,
                "formula": lbl_formula,
                "name": lbl_name
            }

        # Plot frame
        frame_graf = tk.LabelFrame(self.container, text="Gráfica del Modelo Seleccionado")
        frame_graf.pack(fill="both", expand=True, padx=10, pady=5)

        # Matplotlib figure + axes
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("y")
        self.ax.set_title("Gráfico")
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_graf)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Info label for selected model
        self.lbl_info = tk.Label(
            self.container,
            text="Información del modelo seleccionado aparecerá aquí.",
            font=("Arial", 11)
        )
        self.lbl_info.pack(fill="x", padx=10, pady=5)

    def limpiar(self):
        """Reset inputs, metrics, plot, and state."""
        self.txt_x.delete("1.0", tk.END)
        self.txt_y.delete("1.0", tk.END)
        for key, comps in self.rows.items():
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
        self.lbl_info.config(text="Información del modelo seleccionado aparecerá aquí.")
        self.lbl_titulo.config(text="Modelo de Regresión Lineal (n pares de datos)")

    def parse_numbers(self, text):
        """
        Parse a string containing numbers separated by commas, whitespace, semicolons, or newlines.
        Returns list[float]. Raises ValueError on invalid tokens.
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

    def calcular_modelos(self):
        """Parse input data, fit all regression methods, compute metrics por método, actualizar tabla."""
        try:
            xs = self.parse_numbers(self.txt_x.get("1.0", tk.END))
            ys = self.parse_numbers(self.txt_y.get("1.0", tk.END))
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        if len(xs) != len(ys):
            messagebox.showerror("Error", f"La cantidad de valores X ({len(xs)}) y y ({len(ys)}) debe coincidir.")
            return
        if len(xs) < 2:
            messagebox.showerror("Error", f"Se requieren al menos 2 pares de datos. Actualmente X={len(xs)}, y={len(ys)}.")
            return

        n = len(xs)
        self.lbl_titulo.config(text=f"Modelo de Regresión Lineal ({n} pares de datos)")

        X = np.array(xs).reshape(-1, 1)
        y = np.array(ys)

        resultados = {}

        # Campo alpha (si no existe)

        try:
            alpha = float(self.alpha_var.get())
        except ValueError:
            alpha = 1.0

        # Función de métricas por método (no se comparte nada salvo y_true/y_pred)
        def _metric_pack(intercepto, coef, y_true, y_pred):
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_true, y_pred)
            return {
                "intercept": intercepto,
                "coef": coef,
                "mse": mse,
                "rmse": rmse,
                "r2": r2,
                "y_pred": y_pred
            }

        # 1. LinearRegression
        lr = LinearRegression()
        lr.fit(X, y)
        y_pred_lr = lr.predict(X)
        resultados["linear_sklearn"] = _metric_pack(lr.intercept_, lr.coef_[0], y, y_pred_lr)

        # 2. Normal Equation
        X_b = np.c_[np.ones((X.shape[0], 1)), X]
        theta_ne = np.linalg.pinv(X_b.T @ X_b) @ X_b.T @ y
        intercept_ne, coef_ne = theta_ne[0], theta_ne[1]
        y_pred_ne = intercept_ne + coef_ne * X.flatten()
        resultados["normal_eq"] = _metric_pack(intercept_ne, coef_ne, y, y_pred_ne)

        # 3. Gradient Descent (batch)
        intercept_gd, coef_gd, y_pred_gd = self._gradiente_desc(X, y, lr=0.01, iters=5000)
        resultados["grad_desc"] = _metric_pack(intercept_gd, coef_gd, y, y_pred_gd)

        # 4. SGD (escalado y luego reescala)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        sgd = SGDRegressor(
            max_iter=10000,
            tol=1e-6,
            penalty=None,
            eta0=0.001,
            learning_rate="constant",
            random_state=42
        )
        sgd.fit(X_scaled, y)
        coef_sgd = sgd.coef_[0] / scaler.scale_[0] # type: ignore
        intercept_sgd = sgd.intercept_[0] - (coef_sgd * scaler.mean_[0]) # type: ignore
        y_pred_sgd = intercept_sgd + coef_sgd * X.flatten()
        resultados["sgd"] = _metric_pack(intercept_sgd, coef_sgd, y, y_pred_sgd)

        # 5. SVD
        U, s, Vt = np.linalg.svd(X_b, full_matrices=False)
        theta_svd = Vt.T @ (np.diag(1 / s) @ U.T @ y)
        intercept_svd, coef_svd = theta_svd[0], theta_svd[1]
        y_pred_svd = intercept_svd + coef_svd * X.flatten()
        resultados["svd"] = _metric_pack(intercept_svd, coef_svd, y, y_pred_svd)

        # 6. QR
        Q, R = np.linalg.qr(X_b)
        theta_qr = np.linalg.solve(R, Q.T @ y)
        intercept_qr, coef_qr = theta_qr[0], theta_qr[1]
        y_pred_qr = intercept_qr + coef_qr * X.flatten()
        resultados["qr"] = _metric_pack(intercept_qr, coef_qr, y, y_pred_qr)

        # 7. LU (solve sobre ecuaciones normales)
        A = X_b.T @ X_b
        b_vec = X_b.T @ y
        theta_lu = np.linalg.solve(A, b_vec)
        intercept_lu, coef_lu = theta_lu[0], theta_lu[1]
        y_pred_lu = intercept_lu + coef_lu * X.flatten()
        resultados["lu"] = _metric_pack(intercept_lu, coef_lu, y, y_pred_lu)

        # 8. Ridge
        ridge = Ridge(alpha=alpha)
        ridge.fit(X, y)
        y_pred_ridge = ridge.predict(X)
        resultados["ridge"] = _metric_pack(ridge.intercept_, ridge.coef_[0], y, y_pred_ridge)

        # 9. Lasso
        lasso = Lasso(alpha=alpha, max_iter=10000)
        lasso.fit(X, y)
        y_pred_lasso = lasso.predict(X)
        resultados["lasso"] = _metric_pack(lasso.intercept_, lasso.coef_[0], y, y_pred_lasso)

        # 10. Elastic Net
        enet = ElasticNet(alpha=alpha, l1_ratio=0.5, max_iter=10000, random_state=42)
        enet.fit(X, y)
        y_pred_enet = enet.predict(X)
        resultados["elastic_net"] = _metric_pack(enet.intercept_, enet.coef_[0], y, y_pred_enet)

        self.resultados = resultados
        self._actualizar_tabla()
        messagebox.showinfo("Éxito", "Modelos calculados. Seleccione uno y genere la gráfica.")

    def _crear_resultado(self, intercepto, coef, y_true, y_pred):
        # Manteniendo compatibilidad (no usado directamente)
        mse = np.mean((y_true - y_pred) ** 2)
        rmse = np.sqrt(mse)
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - y_true.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0
        return {
            "intercept": intercepto,
            "coef": coef,
            "mse": mse,
            "rmse": rmse,
            "r2": r2,
            "y_pred": y_pred
        }

    def _gradiente_desc(self, X, y, lr=0.01, iters=10000):
        """
        Batch Gradient Descent for simple linear regression.
        Normalizes X for numerical stability, then rescales learned weights.
        Returns (intercept, slope, predicted_values_on_original_X).
        """
        X_mean = np.mean(X)
        X_std = np.std(X)
        if X_std == 0:
            X_std = 1.0  # Avoid division by zero if all X are identical
        X_norm = (X.flatten() - X_mean) / X_std

        m = len(y)
        w = 0.0  # slope in normalized space
        b = 0.0  # intercept

        for _ in range(iters):
            y_pred = w * X_norm + b
            # Derivatives for MSE cost
            dw = (-2 / m) * np.sum((y - y_pred) * X_norm)
            db = (-2 / m) * np.sum(y - y_pred)
            w -= lr * dw
            b -= lr * db

        # Rescale parameters back to original feature space
        w_rescaled = w / X_std
        b_rescaled = b - (w * X_mean / X_std)
        y_pred_final = b_rescaled + w_rescaled * X.flatten()
        return b_rescaled, w_rescaled, y_pred_final

    def _actualizar_tabla(self):
        """Populate the metrics table and highlight best (lowest RMSE) model."""
        if not self.resultados:
            return
        # Select key of best model by RMSE
        mejor_key = min(self.resultados.keys(), key=lambda k: self.resultados[k]["rmse"])
        for key, comps in self.rows.items():
            if key in self.resultados:
                r = self.resultados[key]
                comps["r2"].config(text=f"{r['r2']:.4f}")
                comps["rmse"].config(text=f"{r['rmse']:.4f}")
                comps["mse"].config(text=f"{r['mse']:.4f}")
                comps["formula"].config(text=f"y = {r['intercept']:.4f} + {r['coef']:.4f}x")
                comps["name"].config(fg="green" if key == mejor_key else "black")
            else:
                # Reset if no results
                comps["r2"].config(text="-")
                comps["rmse"].config(text="-")
                comps["mse"].config(text="-")
                comps["formula"].config(text="-")
                comps["name"].config(fg="black")

    def mostrar_grafica(self):
        """Plot selected model line against the original data points."""
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

        # Validate again (in case user changed inputs after computing models)
        if len(xs) != len(ys):
            messagebox.showerror("Error", f"La cantidad de valores X ({len(xs)}) y y ({len(ys)}) debe coincidir.")
            return
        if len(xs) < 2:
            messagebox.showerror("Error", f"Se requieren al menos 2 pares de datos. Actualmente X={len(xs)}, y={len(ys)}.")
            return

        X = np.array(xs)
        y = np.array(ys)
        r = self.resultados[metodo]

        # Clear and redraw scatter + regression line
        self.ax.clear()
        self.ax.scatter(X, y, color="#2980b9", label="Datos Reales")

        # Sort for a clean line plot
        orden = np.argsort(X)
        X_sorted = X[orden]
        y_line = r["intercept"] + r["coef"] * X_sorted
        self.ax.plot(X_sorted, y_line, color="#e74c3c", label="Modelo")
        self.ax.set_title("Regresión Lineal - Método Seleccionado")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("y")
        self.ax.legend()
        self.canvas.draw()

        # Update info label
        info = (
            f"Método: {metodo}\n"
            f"Fórmula: y = {r['intercept']:.6f} + {r['coef']:.6f}x\n"
            f"R2: {r['r2']:.6f} | MSE: {r['mse']:.6f} | RMSE: {r['rmse']:.6f}"
        )
        self.lbl_info.config(text=info)


def main():
    """Entry point for launching the Tkinter application."""
    root = tk.Tk()
    app = RegressionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()