# Algoritmo para la sumatoria del punto medio
import sympy as sp
import math

# Funcion para pedir la funcion
def pedirfuncion():
    x= sp.Symbol('x')
    while True:
        texto = input("Ingresa la función, ejemplo: x**2, exp(x**2), x**2 + 2*x:  ")

        try:
            expresion = sp.sympify(texto)
            if expresion.free_symbols - {x}:
                raise ValueError("Solo se permite utilizar la variable x.")

            frapida = sp.lambdify(x, expresion, modules =['math'])
        
            return expresion, frapida, x
        
        except Exception as e:
            print(f"Error en la sintaxis de la función ({e}). Intenta de nuevo.\n")
            
            
# Funcion para calcular delta x
def calculardeltax(a, b, rectangulos):
    dx= (b - a) / rectangulos
    return dx 


# Funcion para calcular el ciclo sumatorio y la aproximacion numerica 
def ciclosumatoria(dx, frapida, a, rectangulos):
    suma = 0
    for i in range (1, rectangulos + 1):
        punto_medio = a + (i - 0.5) * dx
        valor = frapida(punto_medio)

        if not math.isfinite(valor):
            raise ValueError("La función no está definida en el intervalo.")

        suma += valor 
    return dx * suma

#Funcion para calcular el error de truncamiento 


def calculoerror(expresion, a, x, b, rectangulos):

    segundaderivada = sp.diff(expresion, x, 2)

    # Comprobamos continuidad de la segunda derivada
    continua = sp.calculus.util.continuous_domain(
        segundaderivada, x, sp.Interval(a, b)
    )

    if continua != sp.Interval(a, b):
        print("No se puede garantizar la cota del error: "
              "la segunda derivada no es continua en el intervalo.")
        return None

    f2_rapida = sp.lambdify(x, segundaderivada, modules=['math'])

    # Buscamos el máximo aproximado de |f''(x)|
    pasos = 1000
    h = (b - a) / pasos
    max_f2 = 0.0

    for i in range(pasos + 1):
        punto = a + i * h
        valor = abs(f2_rapida(punto))

        if not math.isfinite(valor):
            print("No se puede garantizar la cota del error.")
            return None

        if valor > max_f2:
            max_f2 = valor

    error = ((b - a)**3 / (24 * rectangulos**2)) * max_f2

    return error







print("Algoritmo para calcular la sumatoria de Riemann en el punto medio")

expr, f, x = pedirfuncion()
rectangulos = int(input("Ingresa el numero de rectangulos: "))    
a = float(input("Limite inferior: "))
b = float(input("Limite superior: "))
if rectangulos <=0 or a>=b:
    print("El numero de rectangulos debe ser mayor a 0 o el limite superior mayor al inferior")
    exit()




dx = calculardeltax(a,b,rectangulos)
aproximacion = (ciclosumatoria(dx,f,a,rectangulos ))
error = calculoerror(expr,a,x,b,rectangulos)


print(f"\nEl valor aproximado es: {aproximacion}")


if error is not None:
    print(f"Cota teorica estimada del error: {error}")
else:
    print("No fue posible garantizar la cota teorica del error.")


