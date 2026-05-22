import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Configura Matplotlib para trabajar con Tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

class SimuladorTemperatura:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Ecuación de Temperatura")
        self.root.geometry("950x550")
        self.root.configure(bg="#f5f5f5")

        # --- PANEL IZQUIERDO: FORMULARIO Y DATOS ---
        # Corrección: Eliminado 'padding' de tk.Frame para evitar el TclError
        frame_izq = tk.Frame(root, bg="#f5f5f5", width=350)
        frame_izq.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)
        frame_izq.pack_propagate(False)

        # Título Ecuación
        tk.Label(frame_izq, text="La Ecuación (Ley de Newton):", font=("Arial", 12, "bold"), bg="#f5f5f5").pack(anchor="w", pady=5)
        
        # Corrección: En tk.Label tampoco se usa 'padding' directamente como argumento en algunas versiones viejas, usamos padx/pady
        lbl_ec = tk.Label(frame_izq, text="T(t) = Tm + (T₀ - Tm) * e^(-k*t)", font=("Courier", 11, "bold"), 
                          bg="#e0e0e0", fg="#1a237e", bd=5, relief="groove", padx=8, pady=8)
        lbl_ec.pack(fill=tk.X, pady=5)

        tk.Label(frame_izq, text="Instrucciones:\ncolocar la variables.", 
                 font=("Arial", 9, "italic"), fg="#555555", bg="#f5f5f5", justify="left").pack(anchor="w", pady=5)

        # Contenedor de las entradas de texto (Grid)
        grid_frame = tk.Frame(frame_izq, bg="#f5f5f5")
        grid_frame.pack(fill=tk.X, pady=10)

        # Campos de texto y variables internas
        self.txt_t0 = self.crear_campo(grid_frame, "Temp. Inicial (T₀):", "90", 0, 0)
        self.txt_tm = self.crear_campo(grid_frame, "Temp. Ambiente (Tm):", "20", 1, 0)
        self.txt_k  = self.crear_campo(grid_frame, "Constante (k):", "0.03", 2, 0)
        self.txt_t  = self.crear_campo(grid_frame, "Tiempo (t):", "30", 3, 0)
        self.txt_tf = self.crear_campo(grid_frame, "Temp. Final T(t):", "", 4, 0) # Vacío inicial

        # Botón de ejecución
        btn_calcular = ttk.Button(frame_izq, text="Calcular y Graficar", command=self.calcular_faltante)
        btn_calcular.pack(fill=tk.X, pady=15)

        # Etiqueta de error
        self.lbl_error = tk.Label(frame_izq, text="", font=("Arial", 10, "bold"), fg="red", bg="#f5f5f5", wraplength=300, justify="left")
        self.lbl_error.pack(fill=tk.X)

        # --- PANEL DERECHO: GRÁFICA ---
        self.frame_der = tk.Frame(root, bg="white", bd=1, relief="sunken")
        self.frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Inicialización del objeto gráfico de Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_der)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Cargar gráfica por defecto al abrir
        self.actualizar_grafica(90.0, 20.0, 0.03, 30.0)

    def crear_campo(self, master, label_text, default_val, row, col):
        """Función auxiliar para construir filas de entrada rápidamente"""
        lbl = tk.Label(master, text=label_text, font=("Arial", 10), bg="#f5f5f5")
        lbl.grid(row=row, column=col, sticky="w", pady=6, padx=5)
        
        entry = ttk.Entry(master, width=15, font=("Arial", 10))
        entry.insert(0, default_val)
        entry.grid(row=row, column=col+1, pady=6, padx=5, sticky="e")
        return entry

    def actualizar_grafica(self, t_0, t_m, k, t_max):
        self.ax.clear()

        # Determinar el alcance del eje X (Tiempo)
        limite_tiempo = max(t_max * 1.5, 10) if (t_max and t_max > 0) else 50
        t_axis = np.linspace(0, limite_tiempo, 200)
        t_res = t_m + (t_0 - t_m) * np.exp(-k * t_axis)

        # Dibujar las líneas de la física
        self.ax.plot(t_axis, t_res, label="Curva Térmica", color="#1a237e", linewidth=2.5)
        self.ax.axhline(y=t_m, color="#d32f2f", linestyle="--", label=f"Temp. Ambiente ({t_m}°C)")

        # Marcar punto exacto si existe un tiempo calculado o ingresado
        if t_max and t_max > 0:
            y_especifico = t_m + (t_0 - t_m) * math.exp(-k * t_max)
            self.ax.plot(t_max, y_especifico, 'go', markersize=8)
            self.ax.annotate(f"({t_max:.1f}s, {y_especifico:.1f}°C)", (t_max, y_especifico),
                             textcoords="offset points", xytext=(10, 10), ha='left', color="green", weight='bold')

        self.ax.set_title("Evolución de la Temperatura en el Tiempo", fontdict={'weight': 'bold', 'size': 11})
        self.ax.set_xlabel("Tiempo (segundos)")
        self.ax.set_ylabel("Temperatura (°C)")
        self.ax.grid(True, linestyle=":")
        self.ax.legend()
        self.fig.tight_layout()
        
        # Redibujar el lienzo de Tkinter
        self.canvas.draw()

    def calcular_faltante(self):
        try:
            # Corrección: Uso estándar de .get() para todas las variables de Tkinter
            t_val = float(self.txt_t.get().strip()) if (self.txt_t.get().strip()) else None
            t_m_val = float(self.txt_tm.get().strip()) if (self.txt_tm.get().strip()) else None
            t_0_val = float(self.txt_t0.get().strip()) if (self.txt_t0.get().strip()) else None
            k_val = float(self.txt_k.get().strip()) if (self.txt_k.get().strip()) else None
            tf_val = float(self.txt_tf.get().strip()) if (self.txt_tf.get().strip()) else None

            # Contar cuántos campos vacíos hay
            valores_nulos = [t_val, t_m_val, t_0_val, k_val, tf_val].count(None)

            if valores_nulos != 1:
                self.lbl_error.config(text="Error: Deja exactamente UN campo vacío para calcularlo.")
                return

            self.lbl_error.config(text="") # Limpiar mensajes de error anteriores

            # Resolver según la variable faltante
            if tf_val is None:
                tf_val = t_m_val + (t_0_val - t_m_val) * math.exp(-k_val * t_val)
                self.txt_tf.delete(0, tk.END)
                self.txt_tf.insert(0, f"{tf_val:.2f}")
            
            elif t_val is None:
                val_log = (tf_val - t_m_val) / (t_0_val - t_m_val)
                if val_log <= 0: raise ValueError("Límite físico imposible. Revisa las temperaturas.")
                t_val = -math.log(val_log) / k_val
                self.txt_t.delete(0, tk.END)
                self.txt_t.insert(0, f"{t_val:.2f}")

            elif t_0_val is None:
                t_0_val = t_m_val + (tf_val - t_m_val) / math.exp(-k_val * t_val)
                self.txt_t0.delete(0, tk.END)
                self.txt_t0.insert(0, f"{t_0_val:.2f}")

            elif t_m_val is None:
                exp_term = math.exp(-k_val * t_val)
                if exp_term == 1: raise ValueError("El tiempo no puede ser cero para calcular Tm.")
                t_m_val = (tf_val - t_0_val * exp_term) / (1 - exp_term)
                self.txt_tm.delete(0, tk.END)
                self.txt_tm.insert(0, f"{t_m_val:.2f}")

            elif k_val is None:
                val_log = (tf_val - t_m_val) / (t_0_val - t_m_val)
                if val_log <= 0: raise ValueError("Límite físico imposible. Revisa las temperaturas.")
                k_val = -math.log(val_log) / t_val
                self.txt_k.delete(0, tk.END)
                self.txt_k.insert(0, f"{k_val:.4f}")

            # Refrescar la gráfica con los nuevos datos calculados
            self.actualizar_grafica(t_0_val, t_m_val, k_val, t_val if t_val else 0.0)

        except Exception as ex:
            self.lbl_error.config(text=f"Error: {str(ex)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorTemperatura(root)
    root.mainloop()