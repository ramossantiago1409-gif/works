import math
import tkinter as tk
from tkinter import messagebox, ttk

# Configuración segura de matplotlib para entornos de escritorio (Tkinter)
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class LeyEnfriamientoTab(ttk.Frame):
    """Pestaña interactiva para la Ley de Enfriamiento de Newton."""

    def __init__(self, parent):
        super().__init__(parent)
        self.init_layout()

    def init_layout(self):
        # Permitir que las columnas se expandan proporcionalmente al cambiar el tamaño de ventana
        self.columnconfigure(0, weight=1, minsize=400)
        self.columnconfigure(1, weight=2, minsize=450)
        self.rowconfigure(0, weight=1)

        # ================= PANEL IZQUIERDO: CONTROLES Y PROCEDIMIENTO =================
        left_panel = ttk.Frame(self, padding=15)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)  # Expandir el procedimiento

        # Título
        lbl_title = ttk.Label(left_panel, text="Ley de Enfriamiento de Newton", font=("Helvetica", 14, "bold"))
        lbl_title.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Panel de Parámetros
        form_frame = ttk.LabelFrame(left_panel, text=" Parámetros de Entrada ", padding=10)
        form_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)

        # Entradas numéricas
        ttk.Label(form_frame, text="Ta - Temp. Ambiente (°C):").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_ta = ttk.Entry(form_frame)
        self.entry_ta.insert(0, "24.0")
        self.entry_ta.grid(row=0, column=1, sticky="ew", pady=3, padx=(10, 0))

        ttk.Label(form_frame, text="T0 - Temp. Inicial (°C):").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_t0 = ttk.Entry(form_frame)
        self.entry_t0.insert(0, "100.0")
        self.entry_t0.grid(row=1, column=1, sticky="ew", pady=3, padx=(10, 0))

        ttk.Label(form_frame, text="k - Constante de enfriamiento (min⁻¹):").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_k = ttk.Entry(form_frame)
        self.entry_k.insert(0, "0.05")
        self.entry_k.grid(row=2, column=1, sticky="ew", pady=3, padx=(10, 0))

        ttk.Label(form_frame, text="t - Tiempo límite (minutos):").grid(row=3, column=0, sticky="w", pady=3)
        self.entry_t = ttk.Entry(form_frame)
        self.entry_t.insert(0, "45.0")
        self.entry_t.grid(row=3, column=1, sticky="ew", pady=3, padx=(10, 0))

        # Panel de Procedimiento Paso a Paso
        proc_frame = ttk.LabelFrame(left_panel, text=" Procedimiento Paso a Paso ", padding=10)
        proc_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        proc_frame.columnconfigure(0, weight=1)
        proc_frame.rowconfigure(0, weight=1)

        self.txt_procedure = tk.Text(proc_frame, wrap="word", font=("Courier New", 10), height=10, bg="#fcfcfc")
        self.txt_procedure.grid(row=0, column=0, sticky="nsew")
        self.txt_procedure.insert("1.0", "Ingresa los datos arriba y presiona 'Calcular' para ver el procedimiento detallado.")
        self.txt_procedure.config(state="disabled")

        # Botón Calcular
        self.btn_calc = ttk.Button(left_panel, text="Calcular y Graficar", command=self.calcular)
        self.btn_calc.grid(row=3, column=0, sticky="ew")

        # ================= PANEL DERECHO: GRÁFICO MATPLOTLIB =================
        self.right_panel = ttk.Frame(self, padding=10)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(0, weight=1)

        # Crear figura inicial limpia
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Evolución de la Temperatura")
        self.ax.set_xlabel("Tiempo (min)")
        self.ax.set_ylabel("Temperatura (°C)")
        self.ax.grid(True, linestyle="--", alpha=0.6)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def calcular(self):
        try:
            ta = float(self.entry_ta.get())
            t0 = float(self.entry_t0.get())
            k = float(self.entry_k.get())
            t = float(self.entry_t.get())

            if t <= 0 or k < 0:
                raise ValueError("El tiempo límite debe ser mayor a cero y k no puede ser negativo.")

            # Cálculo final
            t_final = ta + (t0 - ta) * math.exp(-k * t)

            # Generar procedimiento matemático detallado
            self.txt_procedure.config(state="normal")
            self.txt_procedure.delete("1.0", tk.END)
            
            proc_steps = (
                f"1. DATOS IDENTIFICADOS:\n"
                f"   • Temperatura Ambiente (Ta) = {ta} °C\n"
                f"   • Temperatura Inicial  (T0) = {t0} °C\n"
                f"   • Constante de Enfriam. (k) = {k} min⁻¹\n"
                f"   • Tiempo Evaluado       (t) = {t} min\n\n"
                f"2. FÓRMULA UTILIZADA:\n"
                f"   T(t) = Ta + (T0 - Ta) * e^(-k * t)\n\n"
                f"3. SUSTITUCIÓN Y CÁLCULOS INTERMEDIOS:\n"
                f"   • Diferencia (T0 - Ta) = {t0} - {ta} = {t0 - ta:.2f} °C\n"
                f"   • Exponente (-k * t)   = -({k}) * {t} = {-k * t:.4f}\n"
                f"   • Factor Exponencial   = e^({-k * t:.4f}) ≈ {math.exp(-k * t):.6f}\n"
                f"   • Cambio de Temp.      = {t0 - ta:.2f} * {math.exp(-k * t):.6f} ≈ {(t0 - ta) * math.exp(-k * t):.2f} °C\n\n"
                f"4. RESULTADO FINAL:\n"
                f"   T({t}) = {ta} + {(t0 - ta) * math.exp(-k * t):.2f}\n"
                f"   T({t}) = {t_final:.2f} °C"
            )
            self.txt_procedure.insert("1.0", proc_steps)
            self.txt_procedure.config(state="disabled")

            # Actualizar Gráfico
            self.ax.clear()
            # Generar 150 puntos para la curva de 0 a t
            t_vals = [i * (t / 149) for i in range(150)]
            temp_vals = [ta + (t0 - ta) * math.exp(-k * tv) for tv in t_vals]

            self.ax.plot(t_vals, temp_vals, color="#0066cc", label="Curva de Enfriamiento", linewidth=2)
            self.ax.axhline(ta, color="#ff9900", linestyle="--", label=f"T. Ambiente ({ta}°C)")
            self.ax.plot(t, t_final, 'ro', label=f"Punto T({t}) = {t_final:.1f}°C")
            
            self.ax.set_title("Ley de Enfriamiento de Newton", fontsize=11, fontweight="bold")
            self.ax.set_xlabel("Tiempo (minutos)")
            self.ax.set_ylabel("Temperatura (°C)")
            self.ax.legend(loc="upper right")
            self.ax.grid(True, linestyle="--", alpha=0.5)
            self.canvas.draw()

        except ValueError as e:
            messagebox.showerror("Error de Entrada", f"Verifica los datos numéricos.\nDetalle: {e}")


class ModeloLogisticoTab(ttk.Frame):
    """Pestaña interactiva para el Modelo Logístico de Crecimiento."""

    def __init__(self, parent):
        super().__init__(parent)
        self.init_layout()

    def init_layout(self):
        self.columnconfigure(0, weight=1, minsize=400)
        self.columnconfigure(1, weight=2, minsize=450)
        self.rowconfigure(0, weight=1)

        # ================= PANEL IZQUIERDO =================
        left_panel = ttk.Frame(self, padding=15)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)

        lbl_title = ttk.Label(left_panel, text="Modelo Logístico de Población", font=("Helvetica", 14, "bold"))
        lbl_title.grid(row=0, column=0, sticky="w", pady=(0, 5))

        form_frame = ttk.LabelFrame(left_panel, text=" Parámetros de Entrada ", padding=10)
        form_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="K - Capacidad de carga:").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_k = ttk.Entry(form_frame)
        self.entry_k.insert(0, "1000")
        self.entry_k.grid(row=0, column=1, sticky="ew", pady=3, padx=(10, 0))

        ttk.Label(form_frame, text="P0 - Población Inicial:").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_p0 = ttk.Entry(form_frame)
        self.entry_p0.insert(0, "50")
        self.entry_p0.grid(row=1, column=1, sticky="ew", pady=3, padx=(10, 0))

        ttk.Label(form_frame, text="r - Tasa de crecimiento (r):").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_r = ttk.Entry(form_frame)
        self.entry_r.insert(0, "0.3")
        self.entry_r.grid(row=2, column=1, sticky="ew", pady=3, padx=(10, 0))

        ttk.Label(form_frame, text="t - Tiempo límite de análisis:").grid(row=3, column=0, sticky="w", pady=3)
        self.entry_t = ttk.Entry(form_frame)
        self.entry_t.insert(0, "30")
        self.entry_t.grid(row=3, column=1, sticky="ew", pady=3, padx=(10, 0))

        # Panel de Procedimiento
        proc_frame = ttk.LabelFrame(left_panel, text=" Procedimiento Paso a Paso ", padding=10)
        proc_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        proc_frame.columnconfigure(0, weight=1)
        proc_frame.rowconfigure(0, weight=1)

        self.txt_procedure = tk.Text(proc_frame, wrap="word", font=("Courier New", 10), height=10, bg="#fcfcfc")
        self.txt_procedure.grid(row=0, column=0, sticky="nsew")
        self.txt_procedure.insert("1.0", "Ingresa los datos arriba y presiona 'Calcular' para ver el procedimiento detallado.")
        self.txt_procedure.config(state="disabled")

        self.btn_calc = ttk.Button(left_panel, text="Calcular y Graficar", command=self.calcular)
        self.btn_calc.grid(row=3, column=0, sticky="ew")

        # ================= PANEL DERECHO =================
        self.right_panel = ttk.Frame(self, padding=10)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(0, weight=1)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Crecimiento Logístico")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Población")
        self.ax.grid(True, linestyle="--", alpha=0.6)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def calcular(self):
        try:
            k = float(self.entry_k.get())
            p0 = float(self.entry_p0.get())
            r = float(self.entry_r.get())
            t = float(self.entry_t.get())

            if p0 <= 0 or k <= 0:
                raise ValueError("La población inicial y la capacidad de carga deben ser mayores a cero.")
            if t <= 0:
                raise ValueError("El tiempo de simulación debe ser mayor a cero.")

            # Cálculo de la fórmula
            factor_escala = (k - p0) / p0
            exponencial = math.exp(-r * t)
            denominador = 1 + factor_escala * exponencial
            p_final = k / denominador

            # Generar procedimiento matemático detallado
            self.txt_procedure.config(state="normal")
            self.txt_procedure.delete("1.0", tk.END)
            
            proc_steps = (
                f"1. DATOS IDENTIFICADOS:\n"
                f"   • Capacidad de Carga  (K)  = {k:.1f}\n"
                f"   • Población Inicial   (P0) = {p0:.1f}\n"
                f"   • Tasa Crecimiento    (r)  = {r:.3f}\n"
                f"   • Tiempo Evaluado     (t)  = {t:.1f}\n\n"
                f"2. FÓRMULA UTILIZADA:\n"
                f"   P(t) = K / [1 + ((K - P0) / P0) * e^(-r * t)]\n\n"
                f"3. SUSTITUCIÓN Y CÁLCULOS INTERMEDIOS:\n"
                f"   • Constante de Escala ((K - P0) / P0):\n"
                f"     ({k} - {p0}) / {p0} = {factor_escala:.4f}\n"
                f"   • Factor Exponencial (e^(-r * t)):\n"
                f"     e^(-({r}) * {t}) = e^({-r*t:.3f}) ≈ {exponencial:.6f}\n"
                f"   • Término Denominador:\n"
                f"     1 + ({factor_escala:.4f} * {exponencial:.6f}) = {denominador:.5f}\n\n"
                f"4. RESULTADO FINAL:\n"
                f"   P({t}) = {k} / {denominador:.5f}\n"
                f"   P({t}) = {p_final:.2f} individuos"
            )
            self.txt_procedure.insert("1.0", proc_steps)
            self.txt_procedure.config(state="disabled")

            # Actualizar Gráfico
            self.ax.clear()
            t_vals = [i * (t / 149) for i in range(150)]
            p_vals = [k / (1 + factor_escala * math.exp(-r * tv)) for tv in t_vals]

            self.ax.plot(t_vals, p_vals, color="#228b22", label="Sigmoide Logística", linewidth=2.5)
            self.ax.axhline(k, color="#dc3545", linestyle="--", label=f"Capacidad de Carga K ({k})")
            self.ax.plot(t, p_final, 'bo', label=f"Población P({t:.1f}) = {p_final:.1f}")
            
            self.ax.set_title("Crecimiento de Población (Modelo Logístico)", fontsize=11, fontweight="bold")
            self.ax.set_xlabel("Tiempo (t)")
            self.ax.set_ylabel("Población (N° Individuos)")
            self.ax.legend(loc="lower right")
            self.ax.grid(True, linestyle="--", alpha=0.5)
            self.canvas.draw()

        except ValueError as e:
            messagebox.showerror("Error de Entrada", f"Verifica los datos numéricos.\nDetalle: {e}")


class CircuitoRCTab(ttk.Frame):
    """Pestaña interactiva para la Carga de un Capacitor (Circuito RC)."""

    def __init__(self, parent):
        super().__init__(parent)
        self.init_layout()

    def init_layout(self):
        self.columnconfigure(0, weight=1, minsize=400)
        self.columnconfigure(1, weight=2, minsize=450)
        self.rowconfigure(0, weight=1)

        # ================= PANEL IZQUIERDO =================
        left_panel = ttk.Frame(self, padding=15)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)

        lbl_title = ttk.Label(left_panel, text="Voltaje de Capacitor en Circuito RC", font=("Helvetica", 14, "bold"))
        lbl_title.grid(row=0, column=0, sticky="w", pady=(0, 5))

        form_frame = ttk.LabelFrame(left_panel, text=" Parámetros de Entrada ", padding=10)
        form_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="V - Voltaje de Fuente (V):").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_v = ttk.Entry(form_frame)
        self.entry_v.insert(0, "10.0")
        self.entry_v.grid(row=0, column=1, sticky="ew", pady=3, padx=(10, 0))

        ttk.Label(form_frame, text="R - Resistencia (Ω):").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_r = ttk.Entry(form_frame)
        self.entry_r.insert(0, "5000")
        self.entry_r.grid(row=1, column=1, sticky="ew", pady=3, padx=(10, 0))

        ttk.Label(form_frame, text="C - Capacitancia (F):").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_c = ttk.Entry(form_frame)
        self.entry_c.insert(0, "0.001")  # 1000 uF o 1mF
        self.entry_c.grid(row=2, column=1, sticky="ew", pady=3, padx=(10, 0))

        ttk.Label(form_frame, text="t - Tiempo de carga (s):").grid(row=3, column=0, sticky="w", pady=3)
        self.entry_t = ttk.Entry(form_frame)
        self.entry_t.insert(0, "15.0")
        self.entry_t.grid(row=3, column=1, sticky="ew", pady=3, padx=(10, 0))

        # Panel de Procedimiento
        proc_frame = ttk.LabelFrame(left_panel, text=" Procedimiento Paso a Paso ", padding=10)
        proc_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        proc_frame.columnconfigure(0, weight=1)
        proc_frame.rowconfigure(0, weight=1)

        self.txt_procedure = tk.Text(proc_frame, wrap="word", font=("Courier New", 10), height=10, bg="#fcfcfc")
        self.txt_procedure.grid(row=0, column=0, sticky="nsew")
        self.txt_procedure.insert("1.0", "Ingresa los datos arriba y presiona 'Calcular' para ver el procedimiento detallado.")
        self.txt_procedure.config(state="disabled")

        self.btn_calc = ttk.Button(left_panel, text="Calcular y Graficar", command=self.calcular)
        self.btn_calc.grid(row=3, column=0, sticky="ew")

        # ================= PANEL DERECHO =================
        self.right_panel = ttk.Frame(self, padding=10)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(0, weight=1)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Carga del Capacitor")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Voltaje (V)")
        self.ax.grid(True, linestyle="--", alpha=0.6)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def calcular(self):
        try:
            v = float(self.entry_v.get())
            r = float(self.entry_r.get())
            c = float(self.entry_c.get())
            t = float(self.entry_t.get())

            if r <= 0 or c <= 0 or v < 0:
                raise ValueError("V, R y C no pueden ser negativos, y R y C deben ser mayores a cero.")
            if t <= 0:
                raise ValueError("El tiempo transcurrido t debe ser mayor a cero.")

            # Parámetros físicos secundarios
            tau = r * c
            exponente = -t / tau
            exponencial = math.exp(exponente)
            vc = v * (1 - exponencial)

            # Generar procedimiento matemático detallado
            self.txt_procedure.config(state="normal")
            self.txt_procedure.delete("1.0", tk.END)
            
            proc_steps = (
                f"1. DATOS IDENTIFICADOS:\n"
                f"   • Voltaje Fuente    (V) = {v:.2f} V\n"
                f"   • Resistencia       (R) = {r:.1f} Ω\n"
                f"   • Capacitancia      (C) = {c:.6f} F\n"
                f"   • Tiempo Evaluado   (t) = {t:.2f} s\n\n"
                f"2. CONSTANTE DE TIEMPO (Tau):\n"
                f"   τ = R * C\n"
                f"   τ = {r} * {c} = {tau:.5f} segundos\n\n"
                f"3. SUSTITUCIÓN EN LA FÓRMULA:\n"
                f"   Vc(t) = V * (1 - e^(-t / τ))\n"
                f"   Vc({t}) = {v} * (1 - e^(-{t} / {tau:.5f}))\n\n"
                f"4. CÁLCULOS INTERMEDIOS:\n"
                f"   • Exponente (-t / τ) = {-t / tau:.5f}\n"
                f"   • Exponencial (e^-({t/tau:.4f})) ≈ {exponencial:.6f}\n"
                f"   • Factor de Carga (1 - e^...)  ≈ {1 - exponencial:.6f}\n\n"
                f"5. RESULTADO FINAL:\n"
                f"   Vc({t}) = {v} * {1 - exponencial:.5f}\n"
                f"   Vc({t}) = {vc:.3f} Voltios"
            )
            self.txt_procedure.insert("1.0", proc_steps)
            self.txt_procedure.config(state="disabled")

            # Actualizar Gráfico
            self.ax.clear()
            t_vals = [i * (t / 149) for i in range(150)]
            v_vals = [v * (1 - math.exp(-tv / tau)) for tv in t_vals]

            self.ax.plot(t_vals, v_vals, color="#b22222", label="Carga del Capacitor", linewidth=2)
            self.ax.axhline(v, color="#ff7f0e", linestyle="--", label=f"Voltaje de Fuente ({v} V)")
            self.ax.plot(t, vc, 'go', label=f"Vc({t:.1f}s) = {vc:.2f}V")
            
            self.ax.set_title("Carga en un Circuito RC", fontsize=11, fontweight="bold")
            self.ax.set_xlabel("Tiempo (segundos)")
            self.ax.set_ylabel("Voltaje del Capacitor (V)")
            self.ax.legend(loc="lower right")
            self.ax.grid(True, linestyle="--", alpha=0.5)
            self.canvas.draw()

        except ValueError as e:
            messagebox.showerror("Error de Entrada", f"Verifica los datos numéricos.\nDetalle: {e}")


class SimuladorCientificoApp(tk.Tk):
    """Ventana principal que gestiona las pestañas y el comportamiento ajustable."""

    def __init__(self):
        super().__init__()
        self.title("Simulador Educativo con Análisis Gráfico y Paso a Paso")
        self.geometry("950x650")
        self.minimum_size_width = 850
        self.minimum_size_height = 550
        self.minsize(self.minimum_size_width, self.minimum_size_height)

        # Configurar la cuadrícula del contenedor principal para que sea ajustable
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Configuración del estilo visual (Ttk Clam para multiplataforma uniforme)
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Crear el control de pestañas (Notebook)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Inicializar pestañas dinámicas
        self.tab1 = LeyEnfriamientoTab(self.notebook)
        self.tab2 = ModeloLogisticoTab(self.notebook)
        self.tab3 = CircuitoRCTab(self.notebook)

        self.notebook.add(self.tab1, text="Enfriamiento de Newton")
        self.notebook.add(self.tab2, text="Crecimiento Logístico")
        self.notebook.add(self.tab3, text="Circuito RC (Carga)")


if __name__ == "__main__":
    app = SimuladorCientificoApp()
    app.mainloop()