import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

class EDOCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora Científica de EDOs con Procedimiento")
        self.root.geometry("1200x750")
        self.root.minsize(1100, 650)
        
        # Configuración del tema / Estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configurar_estilos()
        
        # Inicialización de variables de la GUI
        self.eq_var = tk.StringVar(value="-2*y + sin(x)")
        self.x0_var = tk.StringVar(value="0")
        self.y0_var = tk.StringVar(value="1")
        self.xf_var = tk.StringVar(value="2") # Reducido por defecto para que el paso a paso no sea infinito
        self.h_var = tk.StringVar(value="0.5") # Paso ligeramente mayor para apreciar los pasos individuales
        self.metodo_var = tk.StringVar(value="Runge-Kutta 4 (RK4)")
        
        self.crear_interfaz()

    def configurar_estilos(self):
        """Define la paleta de colores y estilos de los componentes."""
        COLOR_BG = "#f5f6fa"
        COLOR_PANEL = "#ffffff"
        COLOR_PRIMARY = "#2f3640"
        COLOR_ACCENT = "#00a8ff"
        
        self.root.configure(bg=COLOR_BG)
        
        self.style.configure(".", background=COLOR_BG, foreground=COLOR_PRIMARY, font=("Segoe UI", 10))
        self.style.configure("TFrame", background=COLOR_BG)
        self.style.configure("Panel.TFrame", background=COLOR_PANEL, relief="solid", borderwidth=1)
        
        self.style.configure("TLabel", background=COLOR_PANEL, font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background=COLOR_PANEL, font=("Segoe UI", 12, "bold"), foreground=COLOR_PRIMARY)
        self.style.configure("Header.TLabel", background=COLOR_BG, font=("Segoe UI", 14, "bold"), foreground=COLOR_PRIMARY)
        
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), background=COLOR_PRIMARY, foreground="white", borderwidth=0)
        self.style.map("TButton", background=[("active", COLOR_ACCENT)])

    def crear_interfaz(self):
        """Construye la estructura de la UI dividida en Control, Gráficos y Pasos."""
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título Superior
        header = ttk.Label(main_frame, text="Solucionador Avanzado de Ecuaciones Diferenciales con Pasos (y' = f(x, y))", style="Header.TLabel")
        header.pack(anchor=tk.W, pady=(0, 15))
        
        # Contenedor de Contenido Principal
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. PANEL IZQUIERDO: Control y Entradas
        left_panel = ttk.Frame(content_frame, width=320, style="Panel.TFrame", padding=15)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        ttk.Label(left_panel, text="Configuración Matemática", style="Title.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(left_panel, text="Función f(x, y):").pack(anchor=tk.W, pady=(5, 2))
        eq_entry = ttk.Entry(left_panel, textvariable=self.eq_var, font=("Consolas", 11))
        eq_entry.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(left_panel, text="Ej: -2*y + sin(x)", font=("Segoe UI", 8, "italic"), foreground="gray").pack(anchor=tk.W, pady=(0, 10))
        
        cond_frame = ttk.Frame(left_panel, style="Panel.TFrame")
        cond_frame.pack(fill=tk.X, pady=5)
        ttk.Label(cond_frame, text="x₀:").grid(row=0, column=0, sticky=tk.W, padx=2)
        ttk.Entry(cond_frame, textvariable=self.x0_var, width=7).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(cond_frame, text="y₀:").grid(row=0, column=2, sticky=tk.W, padx=2)
        ttk.Entry(cond_frame, textvariable=self.y0_var, width=7).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(left_panel, text="x final:").pack(anchor=tk.W, pady=(5, 2))
        ttk.Entry(left_panel, textvariable=self.xf_var).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(left_panel, text="Tamaño del paso (h):").pack(anchor=tk.W, pady=(5, 2))
        ttk.Entry(left_panel, textvariable=self.h_var).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(left_panel, text="Método Numérico:").pack(anchor=tk.W, pady=(5, 2))
        metodos = ["Euler", "Runge-Kutta 4 (RK4)", "SciPy RK45 (Adaptativo)"]
        combo_metodo = ttk.Combobox(left_panel, textvariable=self.metodo_var, values=metodos, state="readonly")
        combo_metodo.pack(fill=tk.X, pady=(0, 15))
        
        btn_calcular = ttk.Button(left_panel, text="RESOLVER Y GRAFICAR", command=self.procesar_y_resolver)
        btn_calcular.pack(fill=tk.X, ipady=8, pady=(5, 0))
        
        # Contenedor para el centro y la derecha (Gráfico y Texto)
        right_content_frame = ttk.Frame(content_frame)
        right_content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 2. PANEL CENTRAL: Gráfico de Matplotlib
        chart_panel = ttk.Frame(right_content_frame, style="Panel.TFrame")
        chart_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.fig, self.ax = plt.subplots(figsize=(5, 5), dpi=100)
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.toolbar = NavigationToolbar2Tk(self.canvas, chart_panel)
        self.toolbar.update()
        
        # 3. PANEL DERECHO: Texto del procedimiento paso a paso
        steps_panel = ttk.Frame(right_content_frame, width=380, style="Panel.TFrame", padding=10)
        steps_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        steps_panel.pack_propagate(False)
        
        ttk.Label(steps_panel, text="Procedimiento Paso a Paso", style="Title.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        # Área de texto con scroll incorporado
        self.txt_pasos = scrolledtext.ScrolledText(steps_panel, wrap=tk.WORD, font=("Consolas", 9), bg="#fafafa", fg="#2f3640")
        self.txt_pasos.pack(fill=tk.BOTH, expand=True)

    # --- Motor de Cálculo Numérico con Historial de Pasos ---
    def resolver_euler(self, f, x0, y0, xf, h):
        pasos = int(np.ceil((xf - x0) / h))
        x = np.zeros(pasos + 1)
        y = np.zeros(pasos + 1)
        x[0], y[0] = x0, y0
        
        texto_pasos = f"MÉTODO DE EULER\nCondiciones: x0={x0}, y0={y0}, h={h}\n"
        texto_pasos += "="*45 + "\n\n"
        
        for i in range(pasos):
            if x[i] + h > xf:
                h = xf - x[i]
            
            f_val = f(x[i], y[i])
            y_siguiente = y[i] + h * f_val
            x_siguiente = x[i] + h
            
            texto_pasos += f"--> PASO {i+1}:\n"
            texto_pasos += f"  x[{i}] = {x[i]:.4f}, y[{i}] = {y[i]:.4f}\n"
            texto_pasos += f"  f(x, y) = {f_val:.4f}\n"
            texto_pasos += f"  y_{i+1} = {y[i]:.4f} + {h:.4f} * ({f_val:.4f}) = {y_siguiente:.4f}\n"
            texto_pasos += f"  x_{i+1} = {x_siguiente:.4f}\n\n"
            
            y[i+1] = y_siguiente
            x[i+1] = x_siguiente
            
        return x, y, texto_pasos

    def resolver_rk4(self, f, x0, y0, xf, h):
        pasos = int(np.ceil((xf - x0) / h))
        x = np.zeros(pasos + 1)
        y = np.zeros(pasos + 1)
        x[0], y[0] = x0, y0
        
        texto_pasos = f"MÉTODO RUNGE-KUTTA 4 (RK4)\nCondiciones: x0={x0}, y0={y0}, h={h}\n"
        texto_pasos += "="*45 + "\n\n"
        
        for i in range(pasos):
            if x[i] + h > xf:
                h = xf - x[i]
                
            k1 = f(x[i], y[i])
            k2 = f(x[i] + h/2, y[i] + h*k1/2)
            k3 = f(x[i] + h/2, y[i] + h*k2/2)
            k4 = f(x[i] + h, y[i] + h*k3)
            
            y_siguiente = y[i] + (h/6) * (k1 + 2*k2 + 2*k3 + k4)
            x_siguiente = x[i] + h
            
            texto_pasos += f"--> PASO {i+1}:\n"
            texto_pasos += f"  x[{i}] = {x[i]:.4f}, y[{i}] = {y[i]:.4f}\n"
            texto_pasos += f"  k1 = f({x[i]:.3f}, {y[i]:.3f}) = {k1:.4f}\n"
            texto_pasos += f"  k2 = f({x[i]+h/2:.3f}, {y[i]+h*k1/2:.3f}) = {k2:.4f}\n"
            texto_pasos += f"  k3 = f({x[i]+h/2:.3f}, {y[i]+h*k2/2:.3f}) = {k3:.4f}\n"
            texto_pasos += f"  k4 = f({x[i]+h:.3f}, {y[i]+h*k3:.3f}) = {k4:.4f}\n"
            texto_pasos += f"  y_{i+1} = {y[i]:.4f} + ({h:.3f}/6)*({k1:.3f} + 2*{k2:.3f} + 2*{k3:.3f} + {k4:.3f}) = {y_siguiente:.4f}\n"
            texto_pasos += f"  x_{i+1} = {x_siguiente:.4f}\n\n"
            
            y[i+1] = y_siguiente
            x[i+1] = x_siguiente
            
        return x, y, texto_pasos

    # --- Lógica de Control y Procesamiento ---
    def procesar_y_resolver(self):
        try:
            # 1. Recuperar y validar parámetros de la GUI
            s_eq = self.eq_var.get().strip()
            x0 = float(self.x0_var.get())
            y0 = float(self.y0_var.get())
            xf = float(self.xf_var.get())
            h = float(self.h_var.get())
            metodo = self.metodo_var.get()
            
            if xf <= x0:
                raise ValueError("El valor de x final debe ser estrictamente mayor que x₀.")
            if h <= 0:
                raise ValueError("El tamaño de paso 'h' debe ser un número positivo.")
            
            # Limpiar panel de pasos de texto previo
            self.txt_pasos.delete('1.0', tk.END)
            
            # 2. Parseo Seguro con SymPy
            transformaciones = standard_transformations + (implicit_multiplication_application,)
            x_sym, y_sym = sp.symbols('x y')
            
            try:
                expr_sympy = parse_expr(s_eq, transformations=transformaciones)
            except Exception as parse_err:
                raise ValueError(f"Error de sintaxis matemática en f(x,y): {parse_err}")
                
            f_num = sp.lambdify((x_sym, y_sym), expr_sympy, modules=['numpy', 'sympy'])
            
            def f_segura(x_val, y_val):
                try:
                    res = f_num(x_val, y_val)
                    if np.isnan(res) or np.isinf(res):
                        raise ArithmeticError("Se alcanzó una indeterminación matemática o desbordamiento (Inf/NaN).")
                    return res
                except Exception as e:
                    raise ArithmeticError(f"Error evaluando la función en x={x_val:.3f}, y={y_val:.3f}: {e}")

            # 3. Intento de Solución Analítica Exacta (SymPy dsolve)
            sol_analitica_disponible = False
            x_analitica, y_analitica = None, None
            texto_analitico = "SOLUCIÓN ANALÍTICA (SymPy):\n"
            
            try:
                y_func = sp.Function('y')
                ode_eq = sp.Eq(y_func(x_sym).diff(x_sym), expr_sympy.subs(y_sym, y_func(x_sym)))
                sol_exacta = sp.dsolve(ode_eq, y_func(x_sym), ics={y_func(x0): y0})
                
                if isinstance(sol_exacta, sp.Eq):
                    expr_exacta = sol_exacta.rhs
                    # Formatear de forma amigable para imprimir
                    texto_analitico += f"y(x) = {expr_exacta}\n\n"
                    
                    f_exacta_num = sp.lambdify(x_sym, expr_exacta, modules=['numpy'])
                    x_analitica = np.linspace(x0, xf, 400)
                    y_analitica = f_exacta_num(x_analitica)
                    
                    if np.isrealobj(y_analitica):
                        sol_analitica_disponible = True
            except Exception:
                texto_analitico += "No se pudo hallar una solución analítica explícita.\n\n"

            # 4. Ejecución del Método Numérico Seleccionado y escritura de pasos
            if metodo == "Euler":
                x_num, y_num, pasos_detallados = self.resolver_euler(f_segura, x0, y0, xf, h)
            elif metodo == "Runge-Kutta 4 (RK4)":
                x_num, y_num, pasos_detallados = self.resolver_rk4(f_segura, x0, y0, xf, h)
            else: # SciPy RK45 Adaptativo
                sol_sp = solve_ivp(f_segura, [x0, xf], [y0], method='RK45', max_step=h)
                x_num, y_num = sol_sp.t, sol_sp.y[0]
                
                # Formatear pasos para el método adaptativo
                pasos_detallados = "MÉTODO ADAPTATIVO SCIPY RK45\n"
                pasos_detallados += "Nota: Este método ajusta dinámicamente el tamaño de paso.\n"
                pasos_detallados += "="*45 + "\n\n"
                for idx, (t_val, y_val) in enumerate(zip(x_num, y_num)):
                    pasos_detallados += f"Punto {idx}: x = {t_val:.4f}, y = {y_val:.4f}\n"

            # Insertar los textos procesados en la UI
            self.txt_pasos.insert(tk.END, texto_analitico)
            self.txt_pasos.insert(tk.END, pasos_detallados)

            # 5. Actualización del Gráfico en Pantalla
            self.ax.clear()
            self.ax.grid(True, linestyle='--', alpha=0.6)
            
            self.ax.plot(x_num, y_num, 'o-', color="#00a8ff", markersize=4, label=f"Numérico ({metodo})")
            
            if sol_analitica_disponible:
                self.ax.plot(x_analitica, y_analitica, color="#e67e22", linewidth=2, label="Analítico Exacto")
            
            self.ax.set_title(f"Solución para y' = {s_eq}")
            self.ax.set_xlabel("x")
            self.ax.set_ylabel("y")
            self.ax.legend(loc="best")
            
            self.canvas.draw()
            
        except ValueError as val_err:
            messagebox.showerror("Error de Validación", str(val_err))
        except ArithmeticError as art_err:
            messagebox.showerror("Error de Cálculo Semántico", str(art_err))
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error crítico no controlado: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EDOCalculatorApp(root)
    root.mainloop()