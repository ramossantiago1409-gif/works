import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

class SimuladorTemperaturaModerno:
    def __init__(self, root):
        self.root = root
        self.root.title("Thermodynamic Analyzer v2.0")
        self.root.geometry("1050x650") 
        self.root.configure(bg="#1e1e24")

        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Modern.TEntry', fieldbackground="#2e2e38", foreground="white", borderwidth=0)
        style.configure('Modern.TButton', background="#3f51b5", foreground="white", font=("Segoe UI", 11, "bold"), padding=10)

        panel_izq = tk.Frame(root, bg="#25252d", width=380)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)
        panel_izq.pack_propagate(False)

        tk.Label(panel_izq, text="ANÁLISIS TÉRMICO", font=("Segoe UI", 16, "bold"), fg="#ffffff", bg="#25252d").pack(anchor="w", padx=15, pady=15)
        
        # Formulario
        form_frame = tk.Frame(panel_izq, bg="#25252d")
        form_frame.pack(fill=tk.X, padx=15, pady=5)

        self.txt_t0 = self.crear_fila_input(form_frame, "Temperatura Inicial (T₀)", "°C", "90", 0)
        self.txt_tm = self.crear_fila_input(form_frame, "Temperatura Ambiente (Tm)", "°C", "20", 1)
        self.txt_k  = self.crear_fila_input(form_frame, "Constante (k)", "1/s", "0.03", 2)
        self.txt_t  = self.crear_fila_input(form_frame, "Tiempo (t)", "seg", "30", 3)
        self.txt_tf = self.crear_fila_input(form_frame, "Temperatura Final T(t)", "°C", "", 4)

        # Botón fijo al final del panel izquierdo
        btn_calcular = ttk.Button(panel_izq, text="CALCULAR Y GRAFICAR", style='Modern.TButton', command=self.ejecutar_calculo)
        btn_calcular.pack(fill=tk.X, padx=15, pady=30)

        self.lbl_error = tk.Label(panel_izq, text="", font=("Segoe UI", 9, "bold"), fg="#ff5252", bg="#25252d", wraplength=340)
        self.lbl_error.pack(fill=tk.X, padx=15)

        # Panel Derecho
        panel_der = tk.Frame(root, bg="#25252d")
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 15), pady=15)

        self.fig, self.ax = plt.subplots(figsize=(6, 4.5), facecolor='#25252d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=panel_der)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.actualizar_grafica(90.0, 20.0, 0.03, 30.0)

    def crear_fila_input(self, master, label_text, unit_text, default_val, row):
        tk.Label(master, text=label_text, font=("Segoe UI", 10), fg="#ffffff", bg="#25252d").grid(row=row*2, column=0, sticky="w", pady=(8, 0))
        entry = ttk.Entry(master, width=25, font=("Segoe UI", 10), style='Modern.TEntry')
        entry.insert(0, default_val)
        entry.grid(row=row*2+1, column=0, sticky="w", pady=(0, 8))
        tk.Label(master, text=unit_text, font=("Segoe UI", 9), fg="#8a8a98", bg="#25252d").grid(row=row*2+1, column=1, sticky="w", padx=5)
        return entry

    def ejecutar_calculo(self):
        try:
            # Obtenemos valores. Si un campo está vacío, lo tratamos como None
            vals = [self.txt_t0.get(), self.txt_tm.get(), self.txt_k.get(), self.txt_t.get(), self.txt_tf.get()]
            data = [float(v.strip()) if v.strip() else None for v in vals]
            t0, tm, k, t, tf = data

            # CASO 1: Si falta uno, despejamos
            if data.count(None) == 1:
                if tf is None:
                    tf = tm + (t0 - tm) * math.exp(-k * t)
                    self.txt_tf.delete(0, tk.END); self.txt_tf.insert(0, f"{tf:.2f}")
                elif t is None:
                    t = -math.log((tf - tm) / (t0 - tm)) / k
                    self.txt_t.delete(0, tk.END); self.txt_t.insert(0, f"{t:.2f}")
                elif t0 is None:
                    t0 = tm + (tf - tm) / math.exp(-k * t)
                    self.txt_t0.delete(0, tk.END); self.txt_t0.insert(0, f"{t0:.2f}")
                elif tm is None:
                    tm = (tf - t0 * math.exp(-k * t)) / (1 - math.exp(-k * t))
                    self.txt_tm.delete(0, tk.END); self.txt_tm.insert(0, f"{tm:.2f}")
                elif k is None:
                    k = -math.log((tf - tm) / (t0 - tm)) / t
                    self.txt_k.delete(0, tk.END); self.txt_k.insert(0, f"{k:.4f}")
            
            # CASO 2: Si están todos llenos, recalculamos T(t) para actualizar la gráfica con esos nuevos datos
            else:
                tf = tm + (t0 - tm) * math.exp(-k * t)
                self.txt_tf.delete(0, tk.END); self.txt_tf.insert(0, f"{tf:.2f}")

            self.actualizar_grafica(t0, tm, k, t)
            self.lbl_error.config(text="")
        except Exception as e:
            self.lbl_error.config(text=f"Error: {str(e)}")

    def actualizar_grafica(self, t0, tm, k, t):
        self.ax.clear()
        self.ax.set_facecolor('#1e1e24')
        self.ax.tick_params(colors='white')
        
        limite = max(t * 1.5, 10)
        t_axis = np.linspace(0, limite, 200)
        temp = tm + (t0 - tm) * np.exp(-k * t_axis)

        self.ax.plot(t_axis, temp, color="#00e676", linewidth=2.5, label="Enfriamiento")
        self.ax.axhline(tm, color="#ff1744", linestyle="--", label="Ambiente")
        self.ax.plot(t, tm + (t0 - tm) * math.exp(-k * t), 'o', color="#29b6f6", markersize=8)
        
        self.ax.set_title("Grafica de la temperatura", color='white')
        self.ax.grid(True, color="#33333d")
        self.ax.legend(facecolor='#25252d', edgecolor='none', labelcolor='white')
        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorTemperaturaModerno(root)
    root.mainloop()