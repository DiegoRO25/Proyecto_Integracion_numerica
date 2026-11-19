
import math  
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable


def suma_riemann_punto_medio(
    funcion: Callable[[float], float],
    inicio: float,
    fin: float,
    subintervalos: int,
) -> float:
    """
    Aproxima el área bajo la curva de `funcion` en [inicio, fin]
    dividiendo el intervalo en `subintervalos` (n) partes iguales.
    """
  
    if subintervalos <= 0:
        raise ValueError("El número de subintervalos debe ser mayor que 0.")
    if fin < inicio:
        raise ValueError("El límite 'fin' no puede ser menor que 'inicio'.")
    if fin == inicio:
        return 0.0  

    ancho = (fin - inicio) / subintervalos
    acumulado = 0.0


    for i in range(subintervalos):

        punto_medio = inicio + (i + 0.5) * ancho

        acumulado += funcion(punto_medio)

    return acumulado * ancho



def potencia_worker_watts(
    t: float,
    potencia_base: float = 45.0,
    amplitud: float = 15.0,
    frecuencia: float = 0.1,
) -> float:
    """
    Simula el consumo eléctrico (en Watts) del worker en el segundo `t`:
    P(t) = potencia_base + amplitud * sin(frecuencia * t).
    Solo se evalúa en cada punto medio sin necesidad de integrarla a mano.
    """
    return potencia_base + amplitud * math.sin(frecuencia * t)


def estimar_energia_wh(
    duracion_segundos: float,
    muestras: int = 120,
    potencia_base: float = 45.0,
    amplitud: float = 15.0,
    frecuencia: float = 0.1,
) -> tuple[float, float]:
    """
    Convierte la potencia a energía integrando P(t) desde 0 hasta `duracion_segundos`.
    Retorna (energia_wh, energia_joules).
    """
    energia_joules = suma_riemann_punto_medio(
        funcion=lambda t: potencia_worker_watts(t, potencia_base, amplitud, frecuencia),
        inicio=0.0,
        fin=duracion_segundos,
        subintervalos=muestras,
    )
    return energia_joules / 3600.0, energia_joules


def cota_error_potencia(
    duracion_segundos: float,
    muestras: int,
    amplitud: float,
    frecuencia: float,
) -> float:
    """
    Calcula la cota superior del error: |E_n| <= K * (b - a)^3 / (24 * n^2).
    """

    k_cota = abs(amplitud) * (frecuencia ** 2)

    return (k_cota * (duracion_segundos ** 3)) / (24.0 * (muestras ** 2))



#----INTERFAZ GRÁFICA----

class AppEnergiaWorker:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Estimador de Energía del Worker — Punto Medio")
        self.root.geometry("640x520")
        self.root.resizable(False, False)

        self._crear_interfaz()
        self._calcular()

    def _crear_interfaz(self) -> None:
        contenedor = ttk.Frame(self.root, padding=16)
        contenedor.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            contenedor,
            text="Estimación de Energía",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor=tk.W)

        ttk.Label(
            contenedor,
            text="P(t) = base + amplitud · sin(frecuencia · t)  |  Regla del punto medio",
            font=("Segoe UI", 9),
        ).pack(anchor=tk.W, pady=(0, 12))

        form = ttk.LabelFrame(contenedor, text="Parámetros de ejecución", padding=12)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Duración (s):").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.entry_duracion = ttk.Entry(form, width=14)
        self.entry_duracion.insert(0, "60")
        self.entry_duracion.grid(row=0, column=1, sticky=tk.W, padx=6, pady=4)

        ttk.Label(form, text="Subintervalos (n):").grid(row=0, column=2, sticky=tk.W, pady=4)
        self.entry_muestras = ttk.Entry(form, width=14)
        self.entry_muestras.insert(0, "120")
        self.entry_muestras.grid(row=0, column=3, sticky=tk.W, padx=6, pady=4)

        ttk.Label(form, text="Potencia base (W):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.entry_base = ttk.Entry(form, width=14)
        self.entry_base.insert(0, "45.0")
        self.entry_base.grid(row=1, column=1, sticky=tk.W, padx=6, pady=4)

        ttk.Label(form, text="Amplitud (W):").grid(row=1, column=2, sticky=tk.W, pady=4)
        self.entry_amplitud = ttk.Entry(form, width=14)
        self.entry_amplitud.insert(0, "15.0")
        self.entry_amplitud.grid(row=1, column=3, sticky=tk.W, padx=6, pady=4)

        ttk.Label(form, text="Frecuencia w (rad/s):").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.entry_freq = ttk.Entry(form, width=14)
        self.entry_freq.insert(0, "0.1")
        self.entry_freq.grid(row=2, column=1, sticky=tk.W, padx=6, pady=4)

        ttk.Button(
            contenedor,
            text="Calcular Energía",
            command=self._calcular,
        ).pack(anchor=tk.W, pady=10)

        salida_box = ttk.LabelFrame(contenedor, text="Resultados", padding=10)
        salida_box.pack(fill=tk.BOTH, expand=True)

        self.txt_resultados = tk.Text(salida_box, height=13, wrap=tk.WORD, font=("Consolas", 9))
        self.txt_resultados.pack(fill=tk.BOTH, expand=True)

    def _calcular(self) -> None:
        try:
            duracion = float(self.entry_duracion.get().strip())
            muestras = int(self.entry_muestras.get().strip())
            base = float(self.entry_base.get().strip())
            amplitud = float(self.entry_amplitud.get().strip())
            freq = float(self.entry_freq.get().strip())

            if duracion < 0:
                raise ValueError("La duración no puede ser negativa.")

            energia_wh, energia_j = estimar_energia_wh(
                duracion_segundos=duracion,
                muestras=muestras,
                potencia_base=base,
                amplitud=amplitud,
                frecuencia=freq,
            )
            cota_j = cota_error_potencia(duracion, muestras, amplitud, freq)
            cota_wh = cota_j / 3600.0
            delta_t = duracion / muestras

            lineas = [
                f"Ventana evaluada: [0.0, {duracion}] s   |   n = {muestras}   |   Δt = {delta_t:.4f} s",
                f"Energía estimada: {energia_wh:.6f} Wh  ({energia_j:.4f} J)",
                f"Cota de error teórica: <= {cota_wh:.8f} Wh  ({cota_j:.6f} J)",
                "",
                "Primeros puntos medios m_i y potencia P(m_i):",
            ]
            for i in range(min(muestras, 10)):
                m_i = (i + 0.5) * delta_t
                p_i = potencia_worker_watts(m_i, base, amplitud, freq)
                lineas.append(f"  i={i + 1}: t = {m_i:.3f} s  ->  P(t) = {p_i:.3f} W")
            if muestras > 10:
                lineas.append(f"  ... ({muestras - 10} subintervalos adicionales)")

            self.txt_resultados.delete("1.0", tk.END)
            self.txt_resultados.insert(tk.END, "\n".join(lineas))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))


if __name__ == "__main__":
    root = tk.Tk()
    app = AppEnergiaWorker(root)
    root.mainloop()