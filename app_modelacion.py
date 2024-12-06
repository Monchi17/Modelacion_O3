from itertools import permutations
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import random
import streamlit as st

# Título de la aplicación
st.title("Configuración de dimensiones de la casa")

# Inputs para las dimensiones de la casa
largo_casa = st.number_input("Ingrese el largo de la casa (en metros):", min_value=0.0, value=2.440 * 2, step=0.01)
ancho_casa = st.number_input("Ingrese el ancho de la casa (en metros):", min_value=0.0, value=2.440 * 6, step=0.01)

# Mostrar las dimensiones ingresadas
st.write(f"Dimensiones ingresadas: Largo = {largo_casa} m, Ancho = {ancho_casa} m")

# Puedes usar las variables largo_casa y ancho_casa en el resto de tu código


# Clase para definir habitaciones
class Habitacion:
    def __init__(self, nombre, vertices):
        self.nombre = nombre
        self.vertices = vertices
        self.ancho = max(x for x, y in vertices) - min(x for x, y in vertices)
        self.largo = max(y for x, y in vertices) - min(y for x, y in vertices)

# Función para actualizar espacios
def actualizar_espacios(espacios, habitacion, x_offset, y_offset):
    nuevos_espacios = []
    for x, y, ancho, alto in espacios:
        if not (x_offset + habitacion.ancho <= x or  # A la izquierda del espacio
                x_offset >= x + ancho or           # A la derecha del espacio
                y_offset + habitacion.largo <= y or  # Debajo del espacio
                y_offset >= y + alto):               # Encima del espacio
            if x_offset > x:  # Espacio a la izquierda
                nuevos_espacios.append((x, y, x_offset - x, alto))
            if x_offset + habitacion.ancho < x + ancho:  # Espacio a la derecha
                nuevos_espacios.append((x_offset + habitacion.ancho, y, (x + ancho) - (x_offset + habitacion.ancho), alto))
            if y_offset > y:  # Espacio abajo
                nuevos_espacios.append((x, y, ancho, y_offset - y))
            if y_offset + habitacion.largo < y + alto:  # Espacio arriba
                nuevos_espacios.append((x, y_offset + habitacion.largo, ancho, (y + alto) - (y_offset + habitacion.largo)))
        else:
            nuevos_espacios.append((x, y, ancho, alto))  # Sin cambios
    return nuevos_espacios

# Función para colocar habitaciones
def colocar_habitaciones(habitaciones, largo_casa, ancho_casa, espacios):
    colocadas = []
    for habitacion in habitaciones:
        for x, y, ancho, alto in espacios:
            if habitacion.ancho <= ancho and habitacion.largo <= alto:
                vertices_ajustados = [(x + vx, y + vy) for vx, vy in habitacion.vertices]
                colocadas.append(Habitacion(habitacion.nombre, vertices_ajustados))
                espacios = actualizar_espacios(espacios, habitacion, x, y)
                break
    return colocadas, espacios

# Función para plotear habitaciones
def plotear_habitaciones(habitaciones, largo_casa, ancho_casa, numero_plano):
    fig, ax = plt.subplots()
    patches = []
    for habitacion in habitaciones:
        polygon = Polygon(habitacion.vertices, closed=True)
        patches.append(polygon)
        x_coords = [v[0] for v in habitacion.vertices]
        y_coords = [v[1] for v in habitacion.vertices]
        ax.text(
            sum(x_coords) / len(x_coords),
            sum(y_coords) / len(y_coords),
            habitacion.nombre, color="black", ha="center", va="center"
        )
    p = PatchCollection(patches, alpha=0.5, edgecolor="black")
    ax.add_collection(p)
    ax.set_xlim(-largo_casa, largo_casa )  # Ajustado para doble ancho (izquierda + derecha)
    ax.set_ylim(0, ancho_casa)
    ax.set_aspect("equal")
    plt.title(f"Plano {numero_plano}")
    plt.show()

# Habitaciones opcionales y finales
habitaciones_opcionales_sin_P8_P11 = [
    Habitacion("P6", [(0, 0), (2.295, 0), (2.295, 2.433), (0, 2.433)]),
    Habitacion("P7", [(0, 0), (2.585, 0), (2.585, 3.920), (0, 3.920)]),
    Habitacion("P9", [(0, 0), (2.295, 0), (2.295, 4.779), (0, 4.779)]),
    Habitacion("P10", [(0, 0), (2.585, 0), (2.585, 4.880), (0, 4.880)])
]
habitaciones_finales = [
    Habitacion("P8", [(0, 0), (2.295, 0), (2.295, 1.487), (0, 1.487)]),
    Habitacion("P11", [(0, 0), (2.295, 0), (2.295, 1.588), (0, 1.588)])
]

# Colocar habitaciones fijas
habitaciones_fijas = [
    Habitacion("P1", [(0, 0), (3.529, 0), (3.529, 2.983), (0, 2.983)]),
    Habitacion("P2", [(0, 0), (1.351, 0), (1.351, 2.983), (0, 2.983)]),
    Habitacion("P3", [(0, 0), (2.585, 0), (2.585, 2.856), (0, 2.856)]),
    Habitacion("P4", [(0, 0), (2.295, 0), (2.295, 2.856), (0, 2.856)])
]

espacios_restantes = [(0, 0, largo_casa, ancho_casa)]
habitaciones_colocadas_fijas, espacios_actualizados = colocar_habitaciones(
    habitaciones_fijas, largo_casa, ancho_casa, espacios_restantes[:]
)

# Generar combinaciones para las habitaciones opcionales sin P8 y P11
combinaciones_sin_P8_P11 = permutations(habitaciones_opcionales_sin_P8_P11)

# Función para verificar si un plano cumple con las dimensiones de la casa
def verificar_dimensiones(habitaciones, largo_casa, ancho_casa, tolerancia=1e-3):
    max_x = max(max(v[0] for v in habitacion.vertices) for habitacion in habitaciones)
    max_y = max(max(v[1] for v in habitacion.vertices) for habitacion in habitaciones)
    return abs(max_x - largo_casa) <= tolerancia and abs(max_y - ancho_casa) <= tolerancia

# Función para normalizar el plano (ordenar habitaciones y vértices)
def normalizar_plano(habitaciones, decimales=3):
    return tuple(
        tuple(sorted((round(v[0], decimales), round(v[1], decimales)) for v in habitacion.vertices))
        for habitacion in sorted(habitaciones, key=lambda h: (min(v[0] for v in h.vertices), min(v[1] for v in h.vertices)))
    )

# Probar todas las combinaciones y agregar P8 o P11 al final
planos_unicos = set()  # Conjunto para almacenar disposiciones únicas
planos_guardados = []
numero_plano = 1
contador_combinaciones = 0

for combinacion in combinaciones_sin_P8_P11:  # Primer ciclo: todas las combinaciones de habitaciones opcionales
    for final in habitaciones_finales:  # Segundo ciclo: agrega P8 o P11 a cada combinación
        contador_combinaciones += 1
        combinacion_completa = list(combinacion) + [final]
        habitaciones_colocadas_opcionales, _ = colocar_habitaciones(
            combinacion_completa, largo_casa, ancho_casa, espacios_actualizados[:]
        )
        plano = habitaciones_colocadas_fijas + habitaciones_colocadas_opcionales
        plano_tupla = tuple((h.nombre, tuple(h.vertices)) for h in plano)
        if plano_tupla not in planos_unicos:
            planos_unicos.add(plano_tupla)
            planos_guardados.append(plano)
        # Normalizar el plano para verificar unicidad
        plano_normalizado = normalizar_plano(plano)
        
        # Verificar dimensiones y unicidad antes de agregar al conjunto único y plotear
        if plano_normalizado not in planos_unicos and verificar_dimensiones(plano, largo_casa, ancho_casa):
            planos_unicos.add(plano_normalizado)  # Agregar disposición única al conjunto
            plotear_habitaciones(plano, largo_casa, ancho_casa, numero_plano)
            numero_plano += 1

print(f"Total de combinaciones generadas: {contador_combinaciones}")

planos_generados = planos_guardados
