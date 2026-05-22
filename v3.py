import math
import tkinter as tk
from tkinter import messagebox, ttk

# Configuración de matplotlib para integración limpia con Tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class LeyEnfriamientoTab(ttk.Frame):
    """Pestaña interactiva para la Ley de Enfriamiento de Newton con resolvedor de derivadas."""

    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=1, minsize=420)
        self.columnconfigure(1, weight=2, minsize=450)
        self.rowconfigure(0, weight=1)
        self.init_layout()

    def init_layout(self):
        # ================= PANEL IZQUIERDO: CONTROLES =================
        left_panel = ttk.Frame(self, padding=10)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)

        # Título
        lbl_title = ttk.Label(left_panel, text="Ley de Enfriamiento de Newton", font=("Helvetica", 13, "bold"))
        lbl_title.grid(row=0, column=0, sticky="w", pady=(0, 2))

        # Checkbox para habilitar modo analítico por derivadas
        self.var_modo_deriv = tk.BooleanVar(value=False)
        chk_deriv = ttk.Checkbutton(
            left_panel, 
            text="Activar Modo Avanzado: Calcular k por Derivadas (EDO)", 
            variable=self.var_modo_deriv,
            command=self.toggle_modo_deriv
        )
        chk_deriv.grid(row=1, column=0, sticky="w", pady=(0, 8))

        # Contenedor de parámetros estándar
        self.frame_stand = ttk.LabelFrame(left_panel, text=" Parámetros Estándar ", padding=8)
        self.frame_stand.grid(row=2, column=0, sticky="nsew", pady=(0, 5))
        self.frame_stand.columnconfigure(1, weight=1)

        ttk.Label(self.frame_stand, text="Ta - Temp. Ambiente (°C):").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_ta = ttk.Entry(self.frame_stand)
        self.entry_ta.insert(0, "24.0")
        self.entry_ta.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(self.frame_stand, text="T0 - Temp. Inicial (°C):").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_t0 = ttk.Entry(self.frame_stand)
        self.entry_t0.insert(0, "100.0")
        self.entry_t0.grid(row=1, column=1, sticky="ew", pady=2, padx=(5, 0))

        # Label para k que cambiará dinámicamente si se deduce
        self.lbl_k_desc = ttk.Label(self.frame_stand, text="k - Constante Enfriamiento (min⁻¹):")
        self.lbl_k_desc.grid(row=2, column=0, sticky="w", pady=2)
        self.entry_k = ttk.Entry(self.frame_stand)
        self.entry_k.insert(0, "0.05")
        self.entry_k.grid(row=2, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(self.frame_stand, text="t - Tiempo límite (min):").grid(row=3, column=0, sticky="w", pady=2)
        self.entry_t = ttk.Entry(self.frame_stand)
        self.entry_t.insert(0, "45.0")
        self.entry_t.grid(row=3, column=1, sticky="ew", pady=2, padx=(5, 0))

        # Contenedor de parámetros por derivadas (oculto por defecto)
        self.frame_deriv = ttk.LabelFrame(left_panel, text=" Deducción de k mediante Derivadas / EDO ", padding=8)
        self.frame_deriv.columnconfigure(1, weight=1)

        ttk.Label(self.frame_deriv, text="T(t_d) - Temp. medida (°C):").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_td_val = ttk.Entry(self.frame_deriv)
        self.entry_td_val.insert(0, "60.0")
        self.entry_td_val.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(self.frame_deriv, text="Orden de la Derivada conocida:").grid(row=1, column=0, sticky="w", pady=2)
        self.combo_orden = ttk.Combobox(self.frame_deriv, values=["1° Derivada (dT/dt)", "2° Derivada (d²T/dt²)", "3° Derivada (d³T/dt³)"], state="readonly")
        self.combo_orden.set("1° Derivada (dT/dt)")
        self.combo_orden.grid(row=1, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(self.frame_deriv, text="Valor de la Derivada dada:").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_deriv_val = ttk.Entry(self.frame_deriv)
        self.entry_deriv_val.insert(0, "-1.8")
        self.entry_deriv_val.grid(row=2, column=1, sticky="ew", pady=2, padx=(5, 0))

        # Procedimiento Paso a Paso
        proc_frame = ttk.LabelFrame(left_panel, text=" Desarrollo Matemático y Deducción ", padding=8)
        proc_frame.grid(row=3, column=0, sticky="nsew", pady=(5, 5))
        proc_frame.columnconfigure(0, weight=1)
        proc_frame.rowconfigure(0, weight=1)

        self.txt_procedure = tk.Text(proc_frame, wrap="word", font=("Courier New", 9), height=7, bg="#fbfbfb")
        self.txt_procedure.grid(row=0, column=0, sticky="nsew")
        self.txt_procedure.insert("1.0", "Ingresa los parámetros y presiona Calcular para ver el procedimiento.")
        self.txt_procedure.config(state="disabled")

        # Botón Calcular
        self.btn_calc = ttk.Button(left_panel, text="Calcular, Deducir y Graficar", command=self.calcular)
        self.btn_calc.grid(row=4, column=0, sticky="ew", pady=(2, 5))

        # ================= PANEL DERECHO: GRÁFICA =================
        self.right_panel = ttk.Frame(self, padding=8)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(0, weight=1)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True, linestyle="--", alpha=0.5)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def toggle_modo_deriv(self):
        """Muestra u oculta el panel de derivadas según el Checkbox."""
        if self.var_modo_deriv.get():
            self.frame_deriv.grid(row=2, column=0, sticky="nsew", pady=(0, 5))
            self.entry_k.config(state="disabled")
            self.lbl_k_desc.config(text="k - Constante (Se deducirá):")
        else:
            self.frame_deriv.grid_forget()
            self.entry_k.config(state="normal")
            self.lbl_k_desc.config(text="k - Constante Enfriamiento (min⁻¹):")

    def calcular(self):
        try:
            ta = float(self.entry_ta.get())
            t0 = float(self.entry_t0.get())
            t = float(self.entry_t.get())
            
            if t <= 0:
                raise ValueError("El tiempo límite t debe ser mayor a cero.")

            procedimiento = "=== LEY DE ENFRIAMIENTO DE NEWTON ===\n"
            procedimiento += f"Ecuación Diferencial Fundamental: dT/dt = -k(T - Ta)\n"
            procedimiento += f"Solución General: T(t) = Ta + (T0 - Ta) * e^(-k * t)\n\n"

            # Determinar k
            if self.var_modo_deriv.get():
                t_medido = float(self.entry_td_val.get())
                deriv_val = float(self.entry_deriv_val.get())
                orden = self.combo_orden.get()

                procedimiento += f"MODO DEDUCCIÓN DE CONSTANTE POR DERIVADAS:\n"
                procedimiento += f"  • Temperatura en el instante dado T(t_d) = {t_medido:.2f} °C\n"
                procedimiento += f"  • Diferencia de Temperatura (T(t_d) - Ta) = {t_medido - ta:.2f} °C\n"

                # Cálculo de k según el orden de la derivada
                if orden.startswith("1°"):
                    # dT/dt = -k*(T - Ta) => k = - (dT/dt) / (T - Ta)
                    denominador = t_medido - ta
                    if abs(denominador) < 1e-6:
                        raise ValueError("La diferencia (T(t_d) - Ta) es demasiado cercana a cero para calcular k.")
                    k = -deriv_val / denominador
                    procedimiento += f"  • 1° Derivada conocida: dT/dt = {deriv_val:.4f}\n"
                    procedimiento += f"  • Ecuación diferencial: dT/dt = -k * (T - Ta)\n"
                    procedimiento += f"  • Deducción de k:\n"
                    procedimiento += f"    k = -(dT/dt) / (T - Ta) = -({deriv_val}) / ({t_medido} - {ta})\n"
                    procedimiento += f"    k = {k:.6f} min⁻¹\n\n"
                elif orden.startswith("2°"):
                    # d^2T/dt^2 = k^2*(T - Ta) => k = sqrt( (d^2T/dt^2) / (T - Ta) )
                    numerador = deriv_val
                    denominador = t_medido - ta
                    if denominador == 0 or (numerador / denominador) < 0:
                        raise ValueError("Imposible deducir k real con una 2° derivada y diferencia de temperatura de signos opuestos.")
                    k = math.sqrt(numerador / denominador)
                    procedimiento += f"  • 2° Derivada conocida: d²T/dt² = {deriv_val:.4f}\n"
                    procedimiento += f"  • Relación d²T/dt² = k² * (T - Ta)\n"
                    procedimiento += f"  • Deducción de k:\n"
                    procedimiento += f"    k = √[ (d²T/dt²) / (T - Ta) ] = √[ {numerador} / {denominador} ]\n"
                    procedimiento += f"    k = {k:.6f} min⁻¹\n\n"
                else:
                    # d^3T/dt^3 = -k^3*(T - Ta) => k = cbrt( -(d^3T/dt^3) / (T - Ta) )
                    denominador = t_medido - ta
                    if denominador == 0:
                        raise ValueError("Diferencia de temperatura nula impide la división.")
                    valor_interno = -deriv_val / denominador
                    if valor_interno < 0:
                        k = -abs(valor_interno)**(1/3) # Raíz cúbica real negativa
                    else:
                        k = valor_interno**(1/3)
                    procedimiento += f"  • 3° Derivada conocida: d³T/dt³ = {deriv_val:.4f}\n"
                    procedimiento += f"  • Relación d³T/dt³ = -k³ * (T - Ta)\n"
                    procedimiento += f"  • Deducción de k:\n"
                    procedimiento += f"    k = ³√[ -(d³T/dt³) / (T - Ta) ] = ³√[ {-deriv_val} / {denominador} ]\n"
                    procedimiento += f"    k = {k:.6f} min⁻¹\n\n"
                
                if k < 0:
                    procedimiento += "⚠️ ADVERTENCIA: Se obtuvo un k negativo. Indica calentamiento o un sistema inestable.\n\n"
            else:
                k = float(self.entry_k.get())
                procedimiento += f"MODO ESTÁNDAR (k proporcionado por usuario):\n"
                procedimiento += f"  • Constante k establecida: {k:.5f} min⁻¹\n\n"

            # Calcular temperatura final T(t)
            t_final = ta + (t0 - ta) * math.exp(-k * t)

            procedimiento += f"CÁLCULO DE LA TEMPERATURA FINAL EN t = {t} min:\n"
            procedimiento += f"  • T({t}) = {ta} + ({t0} - {ta}) * e^(-{k:.5f} * {t})\n"
            procedimiento += f"  • T({t}) = {ta} + ({t0-ta:.2f}) * {math.exp(-k*t):.5f}\n"
            procedimiento += f"  • Resultado: T({t}) = {t_final:.4f} °C\n"

            # Actualizar Caja de texto
            self.txt_procedure.config(state="normal")
            self.txt_procedure.delete("1.0", tk.END)
            self.txt_procedure.insert("1.0", procedimiento)
            self.txt_procedure.config(state="disabled")

            self.ax.clear()
            t_vals = [i * (max(t, 60) / 149) for i in range(150)]
            temp_vals = [ta + (t0 - ta) * math.exp(-k * tv) for tv in t_vals]

            self.ax.plot(t_vals, temp_vals, color="#1f77b4", label="Curva T(t)", linewidth=2)
            self.ax.axhline(ta, color="#ff7f0e", linestyle="--", label=f"T. Ambiente ({ta:.1f}°C)")
            self.ax.plot(t, t_final, 'ro', markersize=8, label=f"T({t:.1f}) = {t_final:.1f}°C")
            
            self.ax.set_title("Evolución de la Temperatura (Ley de Newton)", fontsize=10, fontweight="bold")
            self.ax.set_xlabel("Tiempo (minutos)")
            self.ax.set_ylabel("Temperatura (°C)")
            self.ax.legend(loc="upper right", fontsize=8)
            self.ax.grid(True, linestyle="--", alpha=0.5)
            self.canvas.draw()

        except ValueError as e:
            messagebox.showerror("Error de Entrada", f"Verifica los datos de entrada o derivada.\nDetalle: {e}")

class ModeloLogisticoTab(ttk.Frame):
    """Pestaña interactiva para el Modelo Logístico con cálculo de tasas por derivadas."""

    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=1, minsize=420)
        self.columnconfigure(1, weight=2, minsize=450)
        self.rowconfigure(0, weight=1)
        self.init_layout()

    def init_layout(self):
        left_panel = ttk.Frame(self, padding=10)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)

        lbl_title = ttk.Label(left_panel, text="Modelo Logístico de Población", font=("Helvetica", 13, "bold"))
        lbl_title.grid(row=0, column=0, sticky="w", pady=(0, 2))

        self.var_modo_deriv = tk.BooleanVar(value=False)
        chk_deriv = ttk.Checkbutton(
            left_panel, 
            text="Activar Modo Avanzado: Calcular r por Derivadas (EDO)", 
            variable=self.var_modo_deriv,
            command=self.toggle_modo_deriv
        )
        chk_deriv.grid(row=1, column=0, sticky="w", pady=(0, 8))

        # Parámetros Estándar
        self.frame_stand = ttk.LabelFrame(left_panel, text=" Parámetros Estándar ", padding=8)
        self.frame_stand.grid(row=2, column=0, sticky="nsew", pady=(0, 5))
        self.frame_stand.columnconfigure(1, weight=1)

        ttk.Label(self.frame_stand, text="K - Capacidad de carga:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_k = ttk.Entry(self.frame_stand)
        self.entry_k.insert(0, "1000")
        self.entry_k.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(self.frame_stand, text="P0 - Población Inicial:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_p0 = ttk.Entry(self.frame_stand)
        self.entry_p0.insert(0, "50")
        self.entry_p0.grid(row=1, column=1, sticky="ew", pady=2, padx=(5, 0))

        self.lbl_r_desc = ttk.Label(self.frame_stand, text="r - Tasa de Crecimiento:")
        self.lbl_r_desc.grid(row=2, column=0, sticky="w", pady=2)
        self.entry_r = ttk.Entry(self.frame_stand)
        self.entry_r.insert(0, "0.3")
        self.entry_r.grid(row=2, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(self.frame_stand, text="t - Tiempo límite (t):").grid(row=3, column=0, sticky="w", pady=2)
        self.entry_t = ttk.Entry(self.frame_stand)
        self.entry_t.insert(0, "30.0")
        self.entry_t.grid(row=3, column=1, sticky="ew", pady=2, padx=(5, 0))

        # Deducción de r por Derivadas
        self.frame_deriv = ttk.LabelFrame(left_panel, text=" Deducción de r mediante Derivadas / EDO ", padding=8)
        self.frame_deriv.columnconfigure(1, weight=1)

        ttk.Label(self.frame_deriv, text="P(t_d) - Pob. medida:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_pd_val = ttk.Entry(self.frame_deriv)
        self.entry_pd_val.insert(0, "200.0")
        self.entry_pd_val.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(self.frame_deriv, text="Orden de la Derivada conocida:").grid(row=1, column=0, sticky="w", pady=2)
        self.combo_orden = ttk.Combobox(self.frame_deriv, values=["1° Derivada (dP/dt)", "2° Derivada (d²P/dt²)"], state="readonly")
        self.combo_orden.set("1° Derivada (dP/dt)")
        self.combo_orden.grid(row=1, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(self.frame_deriv, text="Valor de la Derivada dada:").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_deriv_val = ttk.Entry(self.frame_deriv)
        self.entry_deriv_val.insert(0, "48.0")
        self.entry_deriv_val.grid(row=2, column=1, sticky="ew", pady=2, padx=(5, 0))

        # Procedimiento
        proc_frame = ttk.LabelFrame(left_panel, text=" Desarrollo Matemático y Deducción ", padding=8)
        proc_frame.grid(row=3, column=0, sticky="nsew", pady=(5, 5))
        proc_frame.columnconfigure(0, weight=1)
        proc_frame.rowconfigure(0, weight=1)

        self.txt_procedure = tk.Text(proc_frame, wrap="word", font=("Courier New", 9), height=7, bg="#fbfbfb")
        self.txt_procedure.grid(row=0, column=0, sticky="nsew")
        self.txt_procedure.insert("1.0", "Ingresa los parámetros y presiona Calcular para ver el desarrollo.")
        self.txt_procedure.config(state="disabled")

        self.btn_calc = ttk.Button(left_panel, text="Calcular, Deducir y Graficar", command=self.calcular)
        self.btn_calc.grid(row=4, column=0, sticky="ew", pady=(2, 5))

        # Panel de Gráfica
        self.right_panel = ttk.Frame(self, padding=8)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(0, weight=1)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True, linestyle="--", alpha=0.5)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def toggle_modo_deriv(self):
        if self.var_modo_deriv.get():
            self.frame_deriv.grid(row=2, column=0, sticky="nsew", pady=(0, 5))
            self.entry_r.config(state="disabled")
            self.lbl_r_desc.config(text="r - Tasa (Se deducirá):")
        else:
            self.frame_deriv.grid_forget()
            self.entry_r.config(state="normal")
            self.lbl_r_desc.config(text="r - Tasa de Crecimiento:")

    def calcular(self):
        try:
            k_cap = float(self.entry_k.get())
            p0 = float(self.entry_p0.get())
            t = float(self.entry_t.get())

            if k_cap <= 0 or p0 <= 0 or t <= 0:
                raise ValueError("K, P0 y el tiempo límite t deben ser mayores que cero.")

            procedimiento = "=== MODELO DE CRECIMIENTO LOGÍSTICO ===\n"
            procedimiento += f"Ecuación Diferencial: dP/dt = r * P * (1 - P / K)\n"
            procedimiento += f"Solución: P(t) = K / [ 1 + ((K - P0)/P0) * e^(-r*t) ]\n\n"

            if self.var_modo_deriv.get():
                p_medida = float(self.entry_pd_val.get())
                deriv_val = float(self.entry_deriv_val.get())
                orden = self.combo_orden.get()

                procedimiento += f"MODO DEDUCCIÓN DE TASA r POR DERIVADAS:\n"
                procedimiento += f"  • Población medida P(t_d) = {p_medida:.2f}\n"

                if orden.startswith("1°"):
                    # dP/dt = r*P*(1 - P/K) => r = (dP/dt) / (P*(1 - P/K))
                    factor_logistic = p_medida * (1 - p_medida / k_cap)
                    if abs(factor_logistic) < 1e-6:
                        raise ValueError("La población medida coincide con la capacidad de carga (ó cero), dP/dt es nulo.")
                    r = deriv_val / factor_logistic
                    procedimiento += f"  • 1° Derivada dP/dt = {deriv_val:.4f}\n"
                    procedimiento += f"  • Ecuación diferencial: dP/dt = r * P * (1 - P/K)\n"
                    procedimiento += f"  • Deducción de r:\n"
                    procedimiento += f"    r = (dP/dt) / [ P * (1 - P/K) ]\n"
                    procedimiento += f"    r = {deriv_val} / [ {p_medida} * (1 - {p_medida}/{k_cap}) ]\n"
                    procedimiento += f"    r = {r:.6f}\n\n"
                else:
                    # d^2P/dt^2 = r * dP/dt * (1 - 2P/K)
                    # dP/dt = r*P*(1-P/K) => d^2P/dt^2 = r^2 * P*(1-P/K)*(1-2P/K) => r = sqrt( (d^2P/dt^2) / [P*(1-P/K)*(1-2P/K)] )
                    denominador = p_medida * (1 - p_medida/k_cap) * (1 - 2*p_medida/k_cap)
                    if denominador == 0 or (deriv_val / denominador) < 0:
                        raise ValueError("Condiciones incompatibles para obtener una tasa de crecimiento real positiva con la 2° derivada dada.")
                    r = math.sqrt(deriv_val / denominador)
                    procedimiento += f"  • 2° Derivada d²P/dt² = {deriv_val:.4f}\n"
                    procedimiento += f"  • d²P/dt² = r² * P * (1 - P/K) * (1 - 2P/K)\n"
                    procedimiento += f"  • Deducción de r:\n"
                    procedimiento += f"    r = √[ (d²P/dt²) / (P*(1 - P/K)*(1 - 2P/K)) ]\n"
                    procedimiento += f"    r = {r:.6f}\n\n"
            else:
                r = float(self.entry_r.get())
                procedimiento += f"MODO ESTÁNDAR (r proporcionado por usuario):\n"
                procedimiento += f"  • Tasa r establecida: {r:.5f}\n\n"

            # Crecimiento logístico cálculo
            factor_escala = (k_cap - p0) / p0
            exponencial = math.exp(-r * t)
            denominador_final = 1 + factor_escala * exponencial
            p_final = k_cap / denominador_final

            procedimiento += f"CÁLCULO DE LA POBLACIÓN EN t = {t}:\n"
            procedimiento += f"  • Constante de escala (K-P0)/P0 = {factor_escala:.4f}\n"
            procedimiento += f"  • Término Exponencial e^(-{r:.5f}*{t}) = {exponencial:.6f}\n"
            procedimiento += f"  • P({t}) = {k_cap} / [ 1 + {factor_escala:.4f} * {exponencial:.6f} ]\n"
            procedimiento += f"  • Resultado: P({t}) = {p_final:.2f} individuos\n"

            self.txt_procedure.config(state="normal")
            self.txt_procedure.delete("1.0", tk.END)
            self.txt_procedure.insert("1.0", procedimiento)
            self.txt_procedure.config(state="disabled")

            self.ax.clear()
            t_vals = [i * (max(t, 40) / 149) for i in range(150)]
            p_vals = [k_cap / (1 + factor_escala * math.exp(-r * tv)) for tv in t_vals]

            self.ax.plot(t_vals, p_vals, color="#2ca02c", label="Curva Sigmoidal P(t)", linewidth=2.5)
            self.ax.axhline(k_cap, color="#d62728", linestyle="--", label=f"Capacidad K ({k_cap})")
            self.ax.plot(t, p_final, 'bo', markersize=8, label=f"P({t:.1f}) = {p_final:.1f}")
            
            self.ax.set_title("Crecimiento Logístico de Población", fontsize=10, fontweight="bold")
            self.ax.set_xlabel("Tiempo")
            self.ax.set_ylabel("Población")
            self.ax.legend(loc="lower right", fontsize=8)
            self.ax.grid(True, linestyle="--", alpha=0.5)
            self.canvas.draw()

        except ValueError as e:
            messagebox.showerror("Error de Entrada", f"Verifica los datos de entrada o derivada.\nDetalle: {e}")

class CircuitoRCTab(ttk.Frame):
    """Pestaña interactiva para el Voltaje en un capacitor RC con resolvedor de derivadas."""

    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=1, minsize=420)
        self.columnconfigure(1, weight=2, minsize=450)
        self.rowconfigure(0, weight=1)
        self.init_layout()

    def init_layout(self):
        left_panel = ttk.Frame(self, padding=10)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)

        lbl_title = ttk.Label(left_panel, text="Voltaje de Capacitor en Circuito RC", font=("Helvetica", 13, "bold"))
        lbl_title.grid(row=0, column=0, sticky="w", pady=(0, 2))

        self.var_modo_deriv = tk.BooleanVar(value=False)
        chk_deriv = ttk.Checkbutton(
            left_panel, 
            text="Activar Modo Avanzado: Calcular RC (Tau) por Derivadas", 
            variable=self.var_modo_deriv,
            command=self.toggle_modo_deriv
        )
        chk_deriv.grid(row=1, column=0, sticky="w", pady=(0, 8))

        # Parámetros Estándar
        self.frame_stand = ttk.LabelFrame(left_panel, text=" Parámetros Estándar ", padding=8)
        self.frame_stand.grid(row=2, column=0, sticky="nsew", pady=(0, 5))
        self.frame_stand.columnconfigure(1, weight=1)

        ttk.Label(self.frame_stand, text="V - Voltaje Fuente (V):").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_v = ttk.Entry(self.frame_stand)
        self.entry_v.insert(0, "10.0")
        self.entry_v.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))

        self.lbl_rc_desc = ttk.Label(self.frame_stand, text="RC - Constante de tiempo (s):")
        self.lbl_rc_desc.grid(row=1, column=0, sticky="w", pady=2)
        self.entry_rc = ttk.Entry(self.frame_stand)
        self.entry_rc.insert(0, "1.5")
        self.entry_rc.grid(row=1, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(self.frame_stand, text="t - Tiempo de análisis (s):").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_t = ttk.Entry(self.frame_stand)
        self.entry_t.insert(0, "5.0")
        self.entry_t.grid(row=2, column=1, sticky="ew", pady=2, padx=(5, 0))

        # Deducción de RC por Derivadas
        self.frame_deriv = ttk.LabelFrame(left_panel, text=" Deducción de τ (RC) mediante Derivadas ", padding=8)
        self.frame_deriv.columnconfigure(1, weight=1)

        ttk.Label(self.frame_deriv, text="Vc(t_d) - Voltaje medido (V):").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_vcd_val = ttk.Entry(self.frame_deriv)
        self.entry_vcd_val.insert(0, "6.32")
        self.entry_vcd_val.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(self.frame_deriv, text="Orden de la Derivada conocida:").grid(row=1, column=0, sticky="w", pady=2)
        self.combo_orden = ttk.Combobox(self.frame_deriv, values=["1° Derivada (dVc/dt)", "2° Derivada (d²Vc/dt²)", "3° Derivada (d³Vc/dt³)"], state="readonly")
        self.combo_orden.set("1° Derivada (dVc/dt)")
        self.combo_orden.grid(row=1, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(self.frame_deriv, text="Valor de la Derivada dada (V/s):").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_deriv_val = ttk.Entry(self.frame_deriv)
        self.entry_deriv_val.insert(0, "2.45")
        self.entry_deriv_val.grid(row=2, column=1, sticky="ew", pady=2, padx=(5, 0))

        # Procedimiento
        proc_frame = ttk.LabelFrame(left_panel, text=" Desarrollo Matemático y Deducción ", padding=8)
        proc_frame.grid(row=3, column=0, sticky="nsew", pady=(5, 5))
        proc_frame.columnconfigure(0, weight=1)
        proc_frame.rowconfigure(0, weight=1)

        self.txt_procedure = tk.Text(proc_frame, wrap="word", font=("Courier New", 9), height=7, bg="#fbfbfb")
        self.txt_procedure.grid(row=0, column=0, sticky="nsew")
        self.txt_procedure.insert("1.0", "Ingresa los parámetros y presiona Calcular para ver el desarrollo.")
        self.txt_procedure.config(state="disabled")

        self.btn_calc = ttk.Button(left_panel, text="Calcular, Deducir y Graficar", command=self.calcular)
        self.btn_calc.grid(row=4, column=0, sticky="ew", pady=(2, 5))

        # Panel de Gráfica
        self.right_panel = ttk.Frame(self, padding=8)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(0, weight=1)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True, linestyle="--", alpha=0.5)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def toggle_modo_deriv(self):
        if self.var_modo_deriv.get():
            self.frame_deriv.grid(row=2, column=0, sticky="nsew", pady=(0, 5))
            self.entry_rc.config(state="disabled")
            self.lbl_rc_desc.config(text="RC (Tau) - (Se deducirá):")
        else:
            self.frame_deriv.grid_forget()
            self.entry_rc.config(state="normal")
            self.lbl_rc_desc.config(text="RC - Constante de tiempo (s):")

    def calcular(self):
        try:
            v_fuente = float(self.entry_v.get())
            t = float(self.entry_t.get())

            if v_fuente <= 0 or t <= 0:
                raise ValueError("V y el tiempo límite t deben ser mayores que cero.")

            procedimiento = "=== CIRCUITO RC (CARGA DE CAPACITOR) ===\n"
            procedimiento += f"Ecuación Diferencial: dVc/dt = (V - Vc) / (R * C)\n"
            procedimiento += f"Solución: Vc(t) = V * (1 - e^(-t / τ))\n\n"

            if self.var_modo_deriv.get():
                vc_medida = float(self.entry_vcd_val.get())
                deriv_val = float(self.entry_deriv_val.get())
                orden = self.combo_orden.get()

                procedimiento += f"MODO DEDUCCIÓN DE CONSTANTE DE TIEMPO τ POR DERIVADAS:\n"
                procedimiento += f"  • Voltaje medido Vc(t_d) = {vc_medida:.2f} V\n"
                procedimiento += f"  • Gradiente de potencial (V - Vc) = {v_fuente - vc_medida:.2f} V\n"

                if orden.startswith("1°"):
                    # dVc/dt = (V - Vc) / tau => tau = (V - Vc) / (dVc/dt)
                    if abs(deriv_val) < 1e-6:
                        raise ValueError("La primera derivada dada no puede ser cero.")
                    tau = (v_fuente - vc_medida) / deriv_val
                    procedimiento += f"  • 1° Derivada dVc/dt = {deriv_val:.4f} V/s\n"
                    procedimiento += f"  • Deducción de τ:\n"
                    procedimiento += f"    τ = (V - Vc) / (dVc/dt) = ({v_fuente} - {vc_medida}) / {deriv_val}\n"
                    procedimiento += f"    τ = {tau:.6f} segundos\n\n"
                elif orden.startswith("2°"):
                    # d^2Vc/dt^2 = -(dVc/dt) / tau => tau = -(dVc/dt) / (d^2Vc/dt^2)
                    # En carga: dVc/dt = (V-Vc)/tau, d^2Vc/dt^2 = - (V-Vc)/tau^2
                    # Por tanto, tau = - (V-Vc) / tau^2 => No. Mejor d^2Vc/dt^2 = -(V - Vc) / tau^2 => tau = sqrt( (Vc - V) / (d^2Vc/dt^2) )
                    numerador = vc_medida - v_fuente
                    denominador = deriv_val
                    if denominador == 0 or (numerador / denominador) < 0:
                        raise ValueError("Condiciones incompatibles para obtener un Tau real positivo con d²Vc/dt².")
                    tau = math.sqrt(numerador / denominador)
                    procedimiento += f"  • 2° Derivada d²Vc/dt² = {deriv_val:.4f} V/s²\n"
                    procedimiento += f"  • d²Vc/dt² = -(V - Vc) / τ²\n"
                    procedimiento += f"  • Deducción de τ:\n"
                    procedimiento += f"    τ = √[ (Vc - V) / (d²Vc/dt²) ] = √[ ({vc_medida} - {v_fuente}) / {deriv_val} ]\n"
                    procedimiento += f"    τ = {tau:.6f} segundos\n\n"
                else:
                    # d^3Vc/dt^3 = (V - Vc)/tau^3 => tau = cbrt( (V - Vc) / (d^3Vc/dt^3) )
                    denominador = deriv_val
                    if denominador == 0:
                        raise ValueError("La tercera derivada dada no puede ser cero.")
                    numerador = v_fuente - vc_medida
                    val_interno = numerador / denominador
                    if val_interno < 0:
                        tau = -abs(val_interno)**(1/3)
                    else:
                        tau = val_interno**(1/3)
                    procedimiento += f"  • 3° Derivada d³Vc/dt³ = {deriv_val:.4f} V/s³\n"
                    procedimiento += f"  • d³Vc/dt³ = (V - Vc) / τ³\n"
                    procedimiento += f"  • Deducción de τ:\n"
                    procedimiento += f"    τ = ³√[ (V - Vc) / (d³Vc/dt³) ]\n"
                    procedimiento += f"    τ = {tau:.6f} segundos\n\n"
                
                if tau <= 0:
                    raise ValueError("Se dedujo un tiempo constante τ negativo o nulo, físicamente inconsistente.")
            else:
                tau = float(self.entry_rc.get())
                procedimiento += f"MODO ESTÁNDAR (RC proporcionado por usuario):\n"
                procedimiento += f"  • Constante τ (RC) establecida: {tau:.5f} s\n\n"

            # Calcular Vc(t)
            exponencial = math.exp(-t / tau)
            vc_final = v_fuente * (1 - exponencial)

            procedimiento += f"CÁLCULO DEL VOLTAJE EN EL CAPACITOR EN t = {t} s:\n"
            procedimiento += f"  • Exponente (-t / τ) = -{t} / {tau:.4f} = {-t/tau:.4f}\n"
            procedimiento += f"  • Vc({t}) = {v_fuente} * (1 - e^({-t/tau:.4f}))\n"
            procedimiento += f"  • Vc({t}) = {v_fuente} * (1 - {exponencial:.6f})\n"
            procedimiento += f"  • Resultado: Vc({t}) = {vc_final:.4f} Voltios\n"

            self.txt_procedure.config(state="normal")
            self.txt_procedure.delete("1.0", tk.END)
            self.txt_procedure.insert("1.0", procedimiento)
            self.txt_procedure.config(state="disabled")

            self.ax.clear()
            t_vals = [i * (max(t, 10.0) / 149) for i in range(150)]
            vc_vals = [v_fuente * (1 - math.exp(-tv / tau)) for tv in t_vals]

            self.ax.plot(t_vals, vc_vals, color="#d62728", label="Voltaje del Capacitor Vc(t)", linewidth=2)
            self.ax.axhline(v_fuente, color="#7f7f7f", linestyle="--", label=f"Voltaje Fuente ({v_fuente}V)")
            self.ax.plot(t, vc_final, 'go', markersize=8, label=f"Vc({t:.1f}s) = {vc_final:.2f}V")
            
            self.ax.set_title("Carga de un Capacitor en un Circuito RC", fontsize=10, fontweight="bold")
            self.ax.set_xlabel("Tiempo (segundos)")
            self.ax.set_ylabel("Voltaje (V)")
            self.ax.legend(loc="lower right", fontsize=8)
            self.ax.grid(True, linestyle="--", alpha=0.5)
            self.canvas.draw()

        except ValueError as e:
            messagebox.showerror("Error de Entrada", f"Verifica los datos de entrada o derivada.\nDetalle: {e}")

class ResolutorGeneralODETab(ttk.Frame):
    """Pestaña avanzada para ingresar cualquier EDO de 1°, 2° o 3° orden y resolverla numéricamente (RK4)."""

    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=1, minsize=420)
        self.columnconfigure(1, weight=2, minsize=450)
        self.rowconfigure(0, weight=1)
        self.init_layout()

    def init_layout(self):
        # ================= PANEL IZQUIERDO =================
        left_panel = ttk.Frame(self, padding=10)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)

        # Título
        lbl_title = ttk.Label(left_panel, text="Resolutor General de EDOs (RK4)", font=("Helvetica", 13, "bold"))
        lbl_title.grid(row=0, column=0, sticky="w", pady=(0, 2))

        # Contenedor de Formulario
        form_frame = ttk.LabelFrame(left_panel, text=" Configuración de la Ecuación Diferencial ", padding=8)
        form_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Orden de la EDO:").grid(row=0, column=0, sticky="w", pady=2)
        self.combo_orden = ttk.Combobox(form_frame, values=["1° Orden: y' = f(t, y)", "2° Orden: y'' = f(t, y, y')", "3° Orden: y''' = f(t, y, y', y'')"], state="readonly")
        self.combo_orden.set("2° Orden: y'' = f(t, y, y')")
        self.combo_orden.bind("<<ComboboxSelected>>", self.on_orden_changed)
        self.combo_orden.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(form_frame, text="Función f(...) en Python:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_expr = ttk.Entry(form_frame)
        self.entry_expr.insert(0, "-0.2 * dy - 1.5 * y") # Sistema amortiguado clásico
        self.entry_expr.grid(row=1, column=1, sticky="ew", pady=2, padx=(5, 0))

        # Guía de variables
        self.lbl_guia = ttk.Label(form_frame, text="Soporta variables: t, y, dy (para y'), ddy (para y'')", font=("Helvetica", 8, "italic"), foreground="#555")
        self.lbl_guia.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 4))

        # Condiciones Iniciales
        self.frame_condiciones = ttk.LabelFrame(left_panel, text=" Condiciones Iniciales & Tiempo ", padding=8)
        self.frame_condiciones.grid(row=2, column=0, sticky="nsew", pady=(0, 5))
        self.frame_condiciones.columnconfigure(1, weight=1)

        ttk.Label(self.frame_condiciones, text="t0 (Tiempo Inicial):").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_t0 = ttk.Entry(self.frame_condiciones)
        self.entry_t0.insert(0, "0.0")
        self.entry_t0.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(self.frame_condiciones, text="y(t0) [Valor Inicial]:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_y0 = ttk.Entry(self.frame_condiciones)
        self.entry_y0.insert(0, "5.0")
        self.entry_y0.grid(row=1, column=1, sticky="ew", pady=2, padx=(5, 0))

        # Segunda condición inicial (y')
        self.lbl_dy0 = ttk.Label(self.frame_condiciones, text="y'(t0) [Derivada Inicial]:")
        self.lbl_dy0.grid(row=2, column=0, sticky="w", pady=2)
        self.entry_dy0 = ttk.Entry(self.frame_condiciones)
        self.entry_dy0.insert(0, "0.0")
        self.entry_dy0.grid(row=2, column=1, sticky="ew", pady=2, padx=(5, 0))

        # Tercera condición inicial (y'')
        self.lbl_ddy0 = ttk.Label(self.frame_condiciones, text="y''(t0) [2° Derivada Inicial]:")
        self.entry_ddy0 = ttk.Entry(self.frame_condiciones)
        self.entry_ddy0.insert(0, "0.0")

        ttk.Label(self.frame_condiciones, text="t_final (Tiempo Final):").grid(row=4, column=0, sticky="w", pady=2)
        self.entry_tf = ttk.Entry(self.frame_condiciones)
        self.entry_tf.insert(0, "20.0")
        self.entry_tf.grid(row=4, column=1, sticky="ew", pady=2, padx=(5, 0))

        # Actualizar visibilidad de campos de condiciones iniciales
        self.on_orden_changed(None)

        # Procedimiento Paso a Paso del sistema
        proc_frame = ttk.LabelFrame(left_panel, text=" Espacio de Estados y Solución Numérica (RK4) ", padding=8)
        proc_frame.grid(row=3, column=0, sticky="nsew", pady=(5, 5))
        proc_frame.columnconfigure(0, weight=1)
        proc_frame.rowconfigure(0, weight=1)

        self.txt_procedure = tk.Text(proc_frame, wrap="word", font=("Courier New", 9), height=6, bg="#fbfbfb")
        self.txt_procedure.grid(row=0, column=0, sticky="nsew")
        self.txt_procedure.insert("1.0", "Haz clic en Integrar para compilar la ecuación y ver su espacio de estados.")
        self.txt_procedure.config(state="disabled")

        # Botón Integrar
        self.btn_integrate = ttk.Button(left_panel, text="Integrar Numéricamente EDO (RK4)", command=self.resolver_edo)
        self.btn_integrate.grid(row=4, column=0, sticky="ew", pady=(2, 5))

        # ================= PANEL DERECHO: GRÁFICA MULTI-CURVA =================
        self.right_panel = ttk.Frame(self, padding=8)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(0, weight=1)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True, linestyle="--", alpha=0.5)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def on_orden_changed(self, event):
        """Muestra u oculta selectores según el orden seleccionado para la EDO."""
        orden = self.combo_orden.get()
        if orden.startswith("1°"):
            self.lbl_dy0.grid_forget()
            self.entry_dy0.grid_forget()
            self.lbl_ddy0.grid_forget()
            self.entry_ddy0.grid_forget()
        elif orden.startswith("2°"):
            self.lbl_dy0.grid(row=2, column=0, sticky="w", pady=2)
            self.entry_dy0.grid(row=2, column=1, sticky="ew", pady=2, padx=(5, 0))
            self.lbl_ddy0.grid_forget()
            self.entry_ddy0.grid_forget()
        else:
            self.lbl_dy0.grid(row=2, column=0, sticky="w", pady=2)
            self.entry_dy0.grid(row=2, column=1, sticky="ew", pady=2, padx=(5, 0))
            self.lbl_ddy0.grid(row=3, column=0, sticky="w", pady=2)
            self.entry_ddy0.grid(row=3, column=1, sticky="ew", pady=2, padx=(5, 0))

    def resolver_edo(self):
        try:
            expr_str = self.entry_expr.get().strip()
            t0 = float(self.entry_t0.get())
            tf = float(self.entry_tf.get())
            y0_val = float(self.entry_y0.get())
            orden = self.combo_orden.get()

            if tf <= t0:
                raise ValueError("El tiempo final tf debe ser mayor que el inicial t0.")

            # Recoger condiciones iniciales según orden
            state = []
            if orden.startswith("1°"):
                state = [y0_val]
                vars_labels = ["y"]
            elif orden.startswith("2°"):
                dy0_val = float(self.entry_dy0.get())
                state = [y0_val, dy0_val]
                vars_labels = ["y", "y'"]
            else:
                dy0_val = float(self.entry_dy0.get())
                ddy0_val = float(self.entry_ddy0.get())
                state = [y0_val, dy0_val, ddy0_val]
                vars_labels = ["y", "y'", "y''"]

            # Evaluación de la expresión de forma segura
            # Diccionario con funciones matemáticas estándar
            safe_dict = {
                "math": math,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "exp": math.exp,
                "log": math.log,
                "sqrt": math.sqrt,
                "pi": math.pi,
                "e": math.e
            }

            # Definir la función vectorial del sistema de primer orden dy/dt = F(t, State)
            def F(t, u):
                # u es un vector de estado
                # 1° Orden: u = [y] => u' = [ f(t, y) ]
                # 2° Orden: u = [y, dy] => u' = [ dy, f(t, y, dy) ]
                # 3° Orden: u = [y, dy, ddy] => u' = [ dy, ddy, f(t, y, dy, ddy) ]
                if len(u) == 1:
                    local_dict = {"t": t, "y": u[0]}
                    local_dict.update(safe_dict)
                    try:
                        f_val = eval(expr_str, {"__builtins__": None}, local_dict)
                    except Exception as err:
                        raise ValueError(f"Expresión matemática inválida para f(t, y): {err}")
                    return [f_val]
                elif len(u) == 2:
                    local_dict = {"t": t, "y": u[0], "dy": u[1]}
                    local_dict.update(safe_dict)
                    try:
                        f_val = eval(expr_str, {"__builtins__": None}, local_dict)
                    except Exception as err:
                        raise ValueError(f"Expresión matemática inválida para f(t, y, y'): {err}")
                    return [u[1], f_val]
                else:
                    local_dict = {"t": t, "y": u[0], "dy": u[1], "ddy": u[2]}
                    local_dict.update(safe_dict)
                    try:
                        f_val = eval(expr_str, {"__builtins__": None}, local_dict)
                    except Exception as err:
                        raise ValueError(f"Expresión matemática inválida para f(t, y, y', y''): {err}")
                    return [u[1], u[2], f_val]

            # Ejecución de Runge-Kutta de 4° Orden (RK4)
            n_steps = 400
            dt = (tf - t0) / n_steps
            t_hist = [t0]
            u_hist = [list(state)]

            t_curr = t0
            u_curr = list(state)

            for _ in range(n_steps):
                # k1
                deriv1 = F(t_curr, u_curr)
                k1 = [dt * d for d in deriv1]
                
                # k2
                u_k2 = [u + 0.5 * k for u, k in zip(u_curr, k1)]
                deriv2 = F(t_curr + 0.5 * dt, u_k2)
                k2 = [dt * d for d in deriv2]
                
                # k3
                u_k3 = [u + 0.5 * k for u, k in zip(u_curr, k2)]
                deriv3 = F(t_curr + 0.5 * dt, u_k3)
                k3 = [dt * d for d in deriv3]
                
                # k4
                u_k4 = [u + k for u, k in zip(u_curr, k3)]
                deriv4 = F(t_curr + dt, u_k4)
                k4 = [dt * d for d in deriv4]

                # Nueva aproximación de estado
                for i in range(len(u_curr)):
                    u_curr[i] += (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6.0
                
                t_curr += dt
                t_hist.append(t_curr)
                u_hist.append(list(u_curr))

            # Generar texto descriptivo de la reducción a espacio de estados
            procedimiento = f"=== SOLUCIÓN DE EDO POR ESPACIO DE ESTADOS ===\n"
            procedimiento += f"Ecuación: d^{len(state)}y/dt^{len(state)} = {expr_str}\n"
            procedimiento += f"Paso de Integración (dt) = {dt:.5f} s ({n_steps} iteraciones)\n\n"
            procedimiento += "REDUCCIÓN A SISTEMA DE 1° ORDEN:\n"
            
            if len(state) == 1:
                procedimiento += "  Let: u1 = y\n"
                procedimiento += f"  Sujeto a: u1' = f(t, u1) = {expr_str}\n"
            elif len(state) == 2:
                procedimiento += "  Let: u1 = y, u2 = y'\n"
                procedimiento += "  Ecuaciones de Estado:\n"
                procedimiento += "    u1' = u2\n"
                procedimiento += f"    u2' = f(t, u1, u2) = {expr_str}\n"
            else:
                procedimiento += "  Let: u1 = y, u2 = y', u3 = y''\n"
                procedimiento += "  Ecuaciones de Estado:\n"
                procedimiento += "    u1' = u2\n"
                procedimiento += "    u2' = u3\n"
                procedimiento += f"    u3' = f(t, u1, u2, u3) = {expr_str}\n"

            procedimiento += f"\nCONDICIONES INICIALES DE ESTADO:\n"
            for label, val in zip(vars_labels, state):
                procedimiento += f"  • {label}({t0:.1f}) = {val:.2f}\n"

            procedimiento += f"\nRESULTADO DE INTEGRACIÓN NUMÉRICA (RK4):\n"
            procedimiento += f"  • y({tf:.2f}) ≈ {u_curr[0]:.6f}\n"
            if len(state) > 1:
                procedimiento += f"  • y'({tf:.2f}) ≈ {u_curr[1]:.6f}\n"
            if len(state) > 2:
                procedimiento += f"  • y''({tf:.2f}) ≈ {u_curr[2]:.6f}\n"

            self.txt_procedure.config(state="normal")
            self.txt_procedure.delete("1.0", tk.END)
            self.txt_procedure.insert("1.0", procedimiento)
            self.txt_procedure.config(state="disabled")

            self.ax.clear()
            # Desglosar historia de vectores para graficar
            y_vals = [u[0] for u in u_hist]
            self.ax.plot(t_hist, y_vals, color="#1f77b4", label="y(t) [Solución]", linewidth=2)

            if len(state) > 1:
                dy_vals = [u[1] for u in u_hist]
                self.ax.plot(t_hist, dy_vals, color="#ff7f0e", linestyle="--", label="y'(t) [Tasa de cambio]")
            if len(state) > 2:
                ddy_vals = [u[2] for u in u_hist]
                self.ax.plot(t_hist, ddy_vals, color="#2ca02c", linestyle=":", label="y''(t) [Aceleración]")

            self.ax.set_title("Solución Numérica de la Ecuación Diferencial", fontsize=10, fontweight="bold")
            self.ax.set_xlabel("Tiempo (t)")
            self.ax.set_ylabel("Magnitud")
            self.ax.legend(loc="best", fontsize=8)
            self.ax.grid(True, linestyle="--", alpha=0.5)
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Error de Compilación / Ejecución", f"No se pudo resolver la EDO.\nDetalle: {e}")

class SimuladorCientificoApp(tk.Tk):
    """Ventana principal adaptable que alberga todas las pestañas avanzadas."""

    def __init__(self):
        super().__init__()
        self.title("Simulador Científico Avanzado: Resolvedor de EDOs e Inferencia por Derivadas")
        self.geometry("1050x700")
        self.minsize(950, 600)

        # Hacer que el área de contenido principal se expanda dinámicamente
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Aplicar tema visual consistente
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Notebook para organizar las vistas independientes
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Instanciar las pestañas dinámicas
        self.tab1 = LeyEnfriamientoTab(self.notebook)
        self.tab2 = ModeloLogisticoTab(self.notebook)
        self.tab3 = CircuitoRCTab(self.notebook)
        self.tab4 = ResolutorGeneralODETab(self.notebook)

        # Agregar pestañas al control Notebook
        self.notebook.add(self.tab1, text="Enfriamiento de Newton")
        self.notebook.add(self.tab2, text="Crecimiento Logístico")
        self.notebook.add(self.tab3, text="Circuito RC (Carga)")
        self.notebook.add(self.tab4, text="Resolutor de EDOs (RK4)")


if __name__ == "__main__":
    app = SimuladorCientificoApp()
    app.mainloop()