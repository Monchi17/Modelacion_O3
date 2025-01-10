import streamlit as st
from itertools import permutations
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

# Título de la aplicación
st.title("Generador de Planos para Casas")

# Opciones predefinidas para las dimensiones de la casa
opciones = {
    "Ancho 2440*2, Largo 2440*3": (2440 * 2, 2440 * 3),
    "Ancho 2440*2, Largo 2440*4": (2440 * 2, 2440 * 4),
    "Ancho 2440*2, Largo 2440*6": (2440 * 2, 2440 * 6),
    "Ancho 2440*3, Largo 2440*6": (2440 * 3, 2440 * 6),
    "Ancho 2440*4, Largo 2440*6": (2440 * 4, 2440 * 6),
}

# Input para seleccionar la opción
opcion_seleccionada = st.selectbox(
    "Seleccione las dimensiones de la casa:",
    opciones.keys()
)

# Asignar las dimensiones según la selección
largo_casa, ancho_casa = opciones[opcion_seleccionada]


#st.write(f"Area del plano {largo_casa * ancho_casa} M^2")

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
        if not (x_offset + habitacion.ancho <= x or
                x_offset >= x + ancho or
                y_offset + habitacion.largo <= y or
                y_offset >= y + alto):
            if x_offset > x:
                nuevos_espacios.append((x, y, x_offset - x, alto))
            if x_offset + habitacion.ancho < x + ancho:
                nuevos_espacios.append((x_offset + habitacion.ancho, y, (x + ancho) - (x_offset + habitacion.ancho), alto))
            if y_offset > y:
                nuevos_espacios.append((x, y, ancho, y_offset - y))
            if y_offset + habitacion.largo < y + alto:
                nuevos_espacios.append((x, y_offset + habitacion.largo, ancho, (y + alto) - (y_offset + habitacion.largo)))
        else:
            nuevos_espacios.append((x, y, ancho, alto))
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
    ax.set_xlim(-largo_casa, largo_casa)
    ax.set_ylim(0, ancho_casa)
    ax.set_aspect("equal")
    plt.title(f"Plano {numero_plano}")
    st.pyplot(fig)

# Habitaciones opcionales y finales
habitaciones_opcionales_sin_P8_P11 = [
    Habitacion("P6", [(0, 0), (2.295, 0), (2.295, 2.433), (0, 2.433)]),
    Habitacion("P7", [(0, 0), (2.585, 0), (2.585, 3.920), (0, 3.920)]),
    Habitacion("P9", [(0, 0), (2.295, 0), (2.295, 4.779), (0, 4.779)]),
    Habitacion("P10", [(0, 0), (2.585, 0), (2.585, 4.880), (0, 4.880)])
]
habitaciones_finales = [
    Habitacion("P8", [(0, 0), (2.295, 0), (2.295, 1.487), (0, 1.487)]),
    Habitacion("P11", [(0, 0), (2.295, 0), (2.295, 1.588), (0, 1.588)]),
    Habitacion("P5", [(0, 0), (4.880, 0), (4.880, 1.481), (0, 1.481)])
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

# Procesar combinaciones y plotear
if st.button("Generar planos"):
    numero_plano = 1
    for combinacion in combinaciones_sin_P8_P11:
        for final in habitaciones_finales:
            combinacion_completa = list(combinacion) + [final]
            habitaciones_colocadas_opcionales, _ = colocar_habitaciones(
                combinacion_completa, largo_casa, ancho_casa, espacios_actualizados[:]
            )
            plano = habitaciones_colocadas_fijas + habitaciones_colocadas_opcionales
            plotear_habitaciones(plano, largo_casa, ancho_casa, numero_plano)
            numero_plano += 1
