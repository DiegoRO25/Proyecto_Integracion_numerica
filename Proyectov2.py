
import tkinter as tk
from tkinter import ttk, messagebox

import sympy as sp
import math
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ==========================================
# FUNCIONES DEL ALGORITMO
# ==========================================

# Funcion para pedir y validar la funcion
def pedirfuncion(texto):
    x = sp.Symbol('x')

    expresion = sp.sympify(texto)

    if expresion.free_symbols - {x}:
        raise ValueError("Solo se permite utilizar la variable x.")

    frapida = sp.lambdify(x, expresion, modules=['math'])

    return expresion, frapida, x


# Funcion para calcular delta x
def calculardeltax(a, b, rectangulos):
    dx = (b - a) / rectangulos
    return dx


# Funcion para calcular el ciclo sumatorio
# y la aproximacion numerica
def ciclosumatoria(dx, frapida, a, rectangulos):
    suma = 0

    for i in range(1, rectangulos + 1):
        punto_medio = a + (i - 0.5) * dx
        valor = frapida(punto_medio)

        if not math.isfinite(valor):
            raise ValueError(
                "La funcion no esta definida en el intervalo."
            )

        suma += valor

    return dx * suma


# Funcion para calcular el error de truncamiento
def calculoerror(expresion, a, x, b, rectangulos):

    segundaderivada = sp.diff(expresion, x, 2)

    # Comprobamos continuidad de la segunda derivada
    intervalo = sp.Interval(a, b)

    try:
        continua = sp.calculus.util.continuous_domain(
            segundaderivada, x, intervalo
        )
    except Exception:
        return None

    if continua != intervalo:
        return None

    f2_rapida = sp.lambdify(
        x, segundaderivada, modules=['math']
    )

    # Buscamos el maximo aproximado de |f''(x)|
    pasos = 1000
    h = (b - a) / pasos
    max_f2 = 0.0

    for i in range(pasos + 1):
        punto = a + i * h

        try:
            valor = abs(f2_rapida(punto))

            if not math.isfinite(valor):
                return None

        except Exception:
            return None

        if valor > max_f2:
            max_f2 = valor

    error = ((b - a)**3 / (24 * rectangulos**2)) * max_f2

    return error


# ==========================================
# FUNCION PARA GRAFICAR
# ==========================================

def graficar(expresion, x, a, b, rectangulos, dx, frapida):

    # Limpiamos las graficas anteriores
    ax1.clear()
    ax2.clear()

    # Generamos puntos para la grafica
    puntos = np.linspace(a, b, 500)

    funcion_grafica = sp.lambdify(
        x, expresion, modules=['numpy']
    )

    with np.errstate(all='ignore'):
        valores = np.asarray(funcion_grafica(puntos))

    if valores.ndim == 0:
        valores = np.full_like(puntos, valores)

    if np.iscomplexobj(valores):
        valores = np.where(
            np.abs(np.imag(valores)) < 1e-10,
            np.real(valores),
            np.nan
        )

    valores = np.asarray(valores, dtype=float)
    valores[~np.isfinite(valores)] = np.nan

    # Primera grafica: funcion original
    ax1.plot(puntos, valores, label='f(x)')
    ax1.set_title('Grafica de la funcion')
    ax1.set_xlabel('x')
    ax1.set_ylabel('f(x)')
    ax1.grid(True)
    ax1.legend()

    # Segunda grafica: rectangulos del punto medio
    puntos_medios = []
    alturas = []

    for i in range(1, rectangulos + 1):
        punto_medio = a + (i - 0.5) * dx
        valor = frapida(punto_medio)

        puntos_medios.append(punto_medio)
        alturas.append(valor)

    ax2.bar(
        puntos_medios,
        alturas,
        width=dx,
        align='center',
        edgecolor='black',
        alpha=0.5,
        label='Rectangulos del punto medio'
    )

    ax2.plot(puntos, valores, label='f(x)')

    ax2.set_title('Sumatoria del punto medio')
    ax2.set_xlabel('x')
    ax2.set_ylabel('f(x)')
    ax2.grid(True)
    ax2.legend()

    figura.tight_layout()
    canvas.draw()


# ==========================================
# FUNCION PRINCIPAL DEL BOTON
# ==========================================

def calcular():

    try:
        # Obtenemos los datos de la interfaz
        texto = entrada_funcion.get()

        rectangulos = int(entrada_rectangulos.get())
        a = float(entrada_a.get())
        b = float(entrada_b.get())

        # Validamos los datos
        if rectangulos <= 0:
            raise ValueError(
                "El numero de rectangulos debe ser mayor a 0."
            )

        if a >= b:
            raise ValueError(
                "El limite superior debe ser mayor al inferior."
            )

        # Obtenemos la funcion
        expr, f, x = pedirfuncion(texto)

        # Calculamos la aproximacion
        dx = calculardeltax(a, b, rectangulos)

        aproximacion = ciclosumatoria(
            dx, f, a, rectangulos
        )

        # Calculamos el error
        error = calculoerror(
            expr, a, x, b, rectangulos
        )

        # Mostramos los resultados
        resultado_aproximacion.config(
            text=f"Aproximacion: {aproximacion:.10f}"
        )

        resultado_dx.config(
            text=f"Delta x: {dx:.10f}"
        )

        if error is not None:
            resultado_error.config(
                text=f"Estimacion de la cota del error: {error:.10f}"
            )
        else:
            resultado_error.config(
                text="No fue posible estimar la cota del error."
            )

        # Actualizamos las graficas
        graficar(
            expr, x, a, b, rectangulos, dx, f
        )

    except Exception as e:
        messagebox.showerror(
            "Error",
            f"No se pudo realizar el calculo:\n{e}"
        )


# ==========================================
# CONFIGURACION DE LA VENTANA
# ==========================================

ventana = tk.Tk()
ventana.title("Sumatoria de Riemann - Punto Medio")
ventana.geometry("1050x750")
ventana.minsize(850, 650)

# Estilo general
estilo = ttk.Style()
estilo.theme_use('clam')

# Contenedor principal
contenedor = ttk.Frame(ventana, padding=15)
contenedor.pack(fill='both', expand=True)

# ==========================================
# TITULO
# ==========================================

titulo = ttk.Label(
    contenedor,
    text="SUMATORIA DE RIEMANN - PUNTO MEDIO",
    font=("Arial", 17, "bold")
)
titulo.pack(pady=10)


# ==========================================
# APARTADO DE ENTRADAS
# ==========================================

frame_entradas = ttk.LabelFrame(
    contenedor,
    text="Datos de entrada",
    padding=12
)
frame_entradas.pack(fill='x', pady=10)

# Funcion
ttk.Label(
    frame_entradas,
    text="Funcion f(x):"
).grid(row=0, column=0, padx=5, pady=8, sticky='w')

entrada_funcion = ttk.Entry(
    frame_entradas,
    width=35
)
entrada_funcion.grid(row=0, column=1, padx=5, pady=8)
entrada_funcion.insert(0, "x**2")

# Numero de rectangulos
ttk.Label(
    frame_entradas,
    text="Numero de rectangulos:"
).grid(row=0, column=2, padx=5, pady=8, sticky='w')

entrada_rectangulos = ttk.Entry(
    frame_entradas,
    width=12
)
entrada_rectangulos.grid(row=0, column=3, padx=5, pady=8)
entrada_rectangulos.insert(0, "4")

# Limite inferior
ttk.Label(
    frame_entradas,
    text="Limite inferior (a):"
).grid(row=1, column=0, padx=5, pady=8, sticky='w')

entrada_a = ttk.Entry(
    frame_entradas,
    width=15
)
entrada_a.grid(row=1, column=1, padx=5, pady=8, sticky='w')
entrada_a.insert(0, "0")

# Limite superior
ttk.Label(
    frame_entradas,
    text="Limite superior (b):"
).grid(row=1, column=2, padx=5, pady=8, sticky='w')

entrada_b = ttk.Entry(
    frame_entradas,
    width=12
)
entrada_b.grid(row=1, column=3, padx=5, pady=8, sticky='w')
entrada_b.insert(0, "1")


# ==========================================
# BOTON DE CALCULO
# ==========================================

boton_calcular = ttk.Button(
    contenedor,
    text="Calcular",
    command=calcular
)
boton_calcular.pack(pady=10)


# ==========================================
# APARTADO DE RESULTADOS
# ==========================================

frame_resultados = ttk.LabelFrame(
    contenedor,
    text="Resultados",
    padding=12
)
frame_resultados.pack(fill='x', pady=10)

resultado_aproximacion = ttk.Label(
    frame_resultados,
    text="Aproximacion: --",
    font=("Arial", 11)
)
resultado_aproximacion.pack(anchor='w', pady=3)

resultado_dx = ttk.Label(
    frame_resultados,
    text="Delta x: --",
    font=("Arial", 11)
)
resultado_dx.pack(anchor='w', pady=3)

resultado_error = ttk.Label(
    frame_resultados,
    text="Estimacion de la cota del error: --",
    font=("Arial", 11)
)
resultado_error.pack(anchor='w', pady=3)


# ==========================================
# APARTADO DE GRAFICAS
# ==========================================

frame_graficas = ttk.LabelFrame(
    contenedor,
    text="Graficas",
    padding=8
)
frame_graficas.pack(fill='both', expand=True, pady=10)

# Creamos una figura dividida en dos graficas
figura, (ax1, ax2) = plt.subplots(
    1, 2,
    figsize=(10, 4)
)

figura.tight_layout()

# Integramos Matplotlib en Tkinter
canvas = FigureCanvasTkAgg(
    figura,
    master=frame_graficas
)

canvas.draw()

canvas.get_tk_widget().pack(
    fill='both',
    expand=True
)


# ==========================================
# INICIAR INTERFAZ
# ==========================================

ventana.mainloop()
