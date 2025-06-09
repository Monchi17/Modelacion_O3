import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from itertools import permutations
import random
import numpy as np
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Modelación O3 Libre Crecimiento", layout="wide")

# Título de la aplicación
st.title("Modelación O3 Libre Crecimiento - V1")

# Inicializar variables de estado
if 'planos_generados' not in st.session_state:
    st.session_state['planos_generados'] = False
if 'plano_seleccionado' not in st.session_state:
    st.session_state['plano_seleccionado'] = None
if 'planos_filtrados' not in st.session_state:
    st.session_state['planos_filtrados'] = None

# El código de las clases y funciones permanece igual
# Dimensiones de la casa
largo_casa = 2.440 * 2
ancho_casa = 2.440 * 3
        
# Clasificación por rangos de ancho y altura
CLASIFICACIONES = [
    {"nombre": "Baño", "ancho_min": 0.0, "ancho_max": 1.351, "largo_min": 0.0, "largo_max": 2.983},
    {"nombre": "Dor", "ancho_min": 3.5, "ancho_max": 3.6, "largo_min": 3.9, "largo_max": 4.0},
    {"nombre": "Cocina - Comedor", "ancho_min": 2.5, "ancho_max": 2.6, "largo_min": 2.8, "largo_max": 2.9},
    {"nombre": "Estar", "ancho_min": 2.2, "ancho_max": 2.4, "largo_min": 2.4, "largo_max": 4.0},
    {"nombre": "Recibidor", "ancho_min": 2.2, "ancho_max": 4.9, "largo_min": 1.4, "largo_max": 1.6}]

RESTRICCIONES_ESPACIALES = {
    ("Baño", "Dor"),
    ("Estar", "Recibidor"),
    ("Recibidor", "Cocina - Comedor"),
    ("Estar", "Cocina - Comedor"),
}

class Habitacion:
    def __init__(self, nombre, vertices):
        self.nombre = nombre
        self.vertices = vertices
        x_vals = [x for x, y in vertices]
        y_vals = [y for x, y in vertices]
        self.ancho = round(max(x_vals) - min(x_vals), 3)
        self.altura = round(max(y_vals) - min(y_vals), 3)

    def area(self):
        x, y = zip(*self.vertices)
        return 0.5 * abs(sum(x[i] * y[i+1] - x[i+1] * y[i] for i in range(-1, len(x)-1)))


class Casa:
    def __init__(self, largo, ancho):
        self.largo = largo
        self.ancho = ancho
        self.area_total = largo * ancho
        self.habitaciones = []
        self.area_usada = 0
        self.posicion_x = 0
        self.posicion_y = 0
        self.altura_fila_actual = 0

    def agregar_habitacion(self, habitacion):
        if self.area_usada + habitacion.area() <= self.area_total:
            if self.posicion_x + habitacion.ancho > self.largo:
                self.posicion_x = 0
                self.posicion_y += self.altura_fila_actual
                self.altura_fila_actual = 0

            vertices_desplazados = [(x + self.posicion_x, y + self.posicion_y) for x, y in habitacion.vertices]
            habitacion_desplazada = Habitacion(habitacion.nombre, vertices_desplazados)
            self.habitaciones.append(habitacion_desplazada)
            self.area_usada += habitacion.area()

            self.posicion_x += habitacion.ancho
            self.altura_fila_actual = max(self.altura_fila_actual, habitacion.altura)

            if self.posicion_y + self.altura_fila_actual > self.ancho:
                return False
            return True
        return False

    def agregar_habitacion_inferior(self, habitacion_final):
        if self.posicion_y + self.altura_fila_actual + habitacion_final.altura <= self.ancho:
            self.posicion_x = 0
            self.posicion_y += self.altura_fila_actual

            vertices_desplazados = [(x + self.posicion_x, y + self.posicion_y) for x, y in habitacion_final.vertices]
            habitacion_desplazada = Habitacion(habitacion_final.nombre, vertices_desplazados)
            self.habitaciones.append(habitacion_desplazada)
            self.area_usada += habitacion_final.area()

            self.posicion_x += habitacion_final.ancho
            self.altura_fila_actual = habitacion_final.altura
            return True
        return False

    def cumple_dimensiones_exactas(self):
        return self.posicion_x == self.largo and self.posicion_y + self.altura_fila_actual == self.ancho

    def es_valida(self):
        return (self.area_usada <= self.area_total and 
                self.posicion_y + self.altura_fila_actual <= self.ancho)

    def visualizar_plano(self, ax):
        contador_dormitorios = 1

        for hab in self.habitaciones:
            poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
            ax.add_patch(poligono)
            cx = sum([v[0] for v in hab.vertices]) / len(hab.vertices)
            cy = sum([v[1] for v in hab.vertices]) / len(hab.vertices)
            nombre_funcional = obtener_nombre_funcional_por_rango(hab.ancho, hab.altura)
            
            if nombre_funcional == "Dor":
                texto = f"{hab.nombre}\nDor {contador_dormitorios}"
                contador_dormitorios += 1
            else:
                texto = f"{hab.nombre}\n{nombre_funcional}"

            ax.text(cx, cy, texto, ha='center', va='center', fontsize=17)
            
        ax.set_xlim(0, self.largo)
        ax.set_ylim(0, self.ancho)
        ax.set_aspect('equal', adjustable='box')

# Definición de habitaciones
habitaciones_v1 = [Habitacion("P1", [(0, 0), (3.529, 0), (3.529, 2.983), (0, 2.983)]),
                   Habitacion("P2", [(0, 0), (1.351, 0), (1.351, 2.983), (0, 2.983)]),
                   Habitacion("P3", [(0, 0), (2.585, 0), (2.585, 2.856), (0, 2.856)]),
                   Habitacion("P4", [(0, 0), (2.295, 0), (2.295, 2.856), (0, 2.856)]),]

habitaciones_finales = [Habitacion("P8", [(0, 0), (2.295, 0), (2.295, 1.487), (0, 1.487)]),
                        Habitacion("P11", [(0, 0), (2.295, 0), (2.295, 1.588), (0, 1.588)]),
                        Habitacion("P5", [(0, 0), (4.880, 0), (4.880, 1.481), (0, 1.481)])]

def son_adyacentes(hab1, hab2):
    for i in range(len(hab1.vertices)):
        p1 = hab1.vertices[i]
        p2 = hab1.vertices[(i + 1) % len(hab1.vertices)]
        for j in range(len(hab2.vertices)):
            q1 = hab2.vertices[j]
            q2 = hab2.vertices[(j + 1) % len(hab2.vertices)]

            # Segmentos horizontales o verticales
            if p1[1] == p2[1] and q1[1] == q2[1] and p1[1] == q1[1]:
                x1, x2 = sorted([p1[0], p2[0]])
                x3, x4 = sorted([q1[0], q2[0]])
                if x1 <= x4 and x2 >= x3:
                    return True
            elif p1[0] == p2[0] and q1[0] == q2[0] and p1[0] == q1[0]:
                y1, y2 = sorted([p1[1], p2[1]])
                y3, y4 = sorted([q1[1], q2[1]])
                if y1 <= y4 and y2 >= y3:
                    return True
    return False

def obtener_nombre_funcional_por_rango(ancho, largo):
    for clasificacion in CLASIFICACIONES:
        if (clasificacion["ancho_min"] <= ancho <= clasificacion["ancho_max"] and
            clasificacion["largo_min"] <= largo <= clasificacion["largo_max"]):
            return clasificacion["nombre"]
    return "Dor"

def cumple_restricciones_espaciales(casa):
    tipos_presentes = {obtener_nombre_funcional_por_rango(h.ancho, h.altura) for h in casa.habitaciones}
    
    for tipo_a, tipo_b in RESTRICCIONES_ESPACIALES:
        if tipo_a in tipos_presentes and tipo_b in tipos_presentes:
            encontrados_adyacentes = False
            for i in range(len(casa.habitaciones)):
                for j in range(i + 1, len(casa.habitaciones)):
                    hab1 = casa.habitaciones[i]
                    hab2 = casa.habitaciones[j]
                    tipo1 = obtener_nombre_funcional_por_rango(hab1.ancho, hab1.altura)
                    tipo2 = obtener_nombre_funcional_por_rango(hab2.ancho, hab2.altura)
                    if ((tipo1, tipo2) == (tipo_a, tipo_b) or 
                        (tipo1, tipo2) == (tipo_b, tipo_a)):
                        if son_adyacentes(hab1, hab2):
                            encontrados_adyacentes = True
                            break
                if encontrados_adyacentes:
                    break
            if not encontrados_adyacentes:
                return False
    return True

def generar_combinaciones(habitaciones):
    combinaciones_validas = []
    for habitacion_final in habitaciones_finales:
        for permutacion in permutations(habitaciones):
            casa = Casa(largo=largo_casa, ancho=ancho_casa)
            es_valido = True
            for habitacion in permutacion:
                if not casa.agregar_habitacion(habitacion):
                    es_valido = False
                    break
            if es_valido and casa.es_valida() and casa.agregar_habitacion_inferior(habitacion_final):
                if casa.cumple_dimensiones_exactas():
                    combinaciones_validas.append(casa)
    return combinaciones_validas

# Función para visualizar un plano individual en Streamlit
def visualizar_plano_streamlit(casa, titulo):
    fig, ax = plt.subplots(figsize=(10, 10))
    casa.visualizar_plano(ax)
    ax.set_title(titulo, fontsize=30)
    return fig

# Botón para generar planos
if st.button("Generar Planos V1") or st.session_state.planos_generados:
    with st.spinner("Generando planos, por favor espere..."):
        # Generar planos solo si no están ya generados
        if not st.session_state.planos_generados:
            combinaciones = generar_combinaciones(habitaciones_v1)
            planos_filtrados = [plano for plano in combinaciones if cumple_restricciones_espaciales(plano)]
            st.session_state.planos_filtrados = planos_filtrados
            st.session_state.planos_generados = True
        
        # Mostrar información sobre los planos
        st.success(f"Se han generado {len(st.session_state.planos_filtrados)} planos que cumplen las restricciones.")
        
        # Crear visualización de todos los planos en una cuadrícula
        num_cols = min(4, len(st.session_state.planos_filtrados))
        num_filas = (len(st.session_state.planos_filtrados) + num_cols - 1) // num_cols
        
        # Selector para elegir un plano
        opciones = [f"Plano {i+1}" for i in range(len(st.session_state.planos_filtrados))]
        seleccion = st.selectbox("Seleccione un plano:", opciones)
        indice_seleccionado = opciones.index(seleccion)
        st.session_state.plano_seleccionado = indice_seleccionado
        
        # Visualizar el plano seleccionado
        fig = visualizar_plano_streamlit(st.session_state.planos_filtrados[indice_seleccionado], seleccion)
        st.pyplot(fig)

# Botón para avanzar a V2 (solo visible cuando hay un plano seleccionado)
if st.session_state.plano_seleccionado is not None:
    if st.button("Siguiente - Pasar a V2"):
        st.success(f"Ha seleccionado el Plano {st.session_state.plano_seleccionado + 1}. Avanzando a la fase V2...")
        # Aquí se guardaría el plano seleccionado para V2
        # Por ejemplo:
        # st.session_state.plano_base_v2 = st.session_state.planos_filtrados[st.session_state.plano_seleccionado]
        
        # Como no queremos implementar V2 aún, solo mostramos un mensaje
        st.info("La implementación de V2 estará disponible próximamente.")
else:
    st.info("Primero genere los planos y seleccione uno para continuar.")
