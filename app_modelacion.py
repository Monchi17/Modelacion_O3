import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from itertools import permutations
import random
import hashlib
import numpy as np

# Configura la página
st.set_page_config(layout="wide", page_title="Modelación O3 - Libre Crecimiento")

# Título y descripción principal
st.title("Modelación O3 - Libre Crecimiento")
st.write("Aplicación para el diseño de planos arquitectónicos mediante generación computacional.")

# Sidebar para navegación
pagina = st.sidebar.radio(
    "Selecciona la etapa:", 
    ["V1 - Base", "V2 - Ampliación", "V3 - Optimización", "V4 - Extensión lateral", "V5 - Extensión completa"]
)

# Inicializar variables en session_state si no existen
if 'planos_aleatorios' not in st.session_state:
    st.session_state.planos_aleatorios = []
if 'planos_V2' not in st.session_state:
    st.session_state.planos_V2 = []
if 'planos_V3_B' not in st.session_state:
    st.session_state.planos_V3_B = []
if 'planos_v4' not in st.session_state:
    st.session_state.planos_v4 = []
if 'planos_v5' not in st.session_state:
    st.session_state.planos_v5 = []

# Función principal que controla el flujo
def main():
    if pagina == "V1 - Base":
        mostrar_v1()
    elif pagina == "V2 - Ampliación":
        mostrar_v2()
    elif pagina == "V3 - Optimización":
        mostrar_v3()
    elif pagina == "V4 - Extensión lateral":
        mostrar_v4()
    elif pagina == "V5 - Extensión completa":
        mostrar_v5()

# Ejecutar la aplicación
main()

    
largo_casa = 2.440 * 2
ancho_casa = 2.440 * 3
        
# Clasificación por rangos de ancho y altura
CLASIFICACIONES_V1 = [
    {"nombre": "Baño", "ancho_min": 0.0, "ancho_max": 1.351, "largo_min": 0.0, "largo_max": 2.983},
    {"nombre": "Dor", "ancho_min": 3.5, "ancho_max": 3.6, "largo_min": 3.9, "largo_max": 4.0},
    {"nombre": "Cocina - Comedor", "ancho_min": 2.5, "ancho_max": 2.6, "largo_min": 2.8, "largo_max": 2.9},
    {"nombre": "Estar", "ancho_min": 2.2, "ancho_max": 2.4, "largo_min": 2.4, "largo_max": 4.0},
    {"nombre": "Recibidor", "ancho_min": 2.2, "ancho_max": 4.9, "largo_min": 1.4, "largo_max": 1.6}]

RESTRICCIONES_ESPACIALES_V1 = {
    ("Baño", "Dor"),
    #("Cocina", "Comedor"),
    ("Estar", "Recibidor"),
    ("Recibidor", "Cocina - Comedor"),
    ("Estar", "Cocina - Comedor"),
    #("Estar", "Estar"),
    #("Comedor", "Comedor")
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

    def visualizar_plano(casa, titulo=""):
        """
        Visualiza el plano de una casa mostrando todas sus habitaciones.
        
        Args:
            casa: Objeto Casa que contiene las habitaciones a visualizar
            titulo: Título opcional para la figura
            
        Returns:
            fig: Objeto figura de matplotlib
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        contador_dormitorios = 1
        contador_baños = 1
        
        for hab in casa.habitaciones:
            # Crear el polígono que representa la habitación
            poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
            ax.add_patch(poligono)
            
            # Calcular el centro de la habitación para colocar el texto
            cx = sum([v[0] for v in hab.vertices]) / len(hab.vertices)
            cy = sum([v[1] for v in hab.vertices]) / len(hab.vertices)
            nombre_funcional = obtener_nombre_funcional_por_rango(hab.ancho, hab.altura)
            
            # Formatear el texto según el tipo de habitación
            if nombre_funcional == "Dor":
                texto = f"{hab.nombre}\nDor {contador_dormitorios}"
                contador_dormitorios += 1
            elif nombre_funcional == "Baño":
                texto = f"{hab.nombre}\nBaño {contador_baños}"
                contador_baños += 1
            else:
                texto = f"{hab.nombre}\n{nombre_funcional}"
            
            # Añadir el texto al plano
            ax.text(cx, cy, texto, ha='center', va='center', fontsize=12)
        
        # Configurar los ejes y apariencia del plano
        ax.set_xlim(0, casa.largo)
        ax.set_ylim(0, casa.ancho)
        ax.set_aspect('equal', adjustable='box')
        ax.set_title(titulo, fontsize=14)
        
        return fig

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
    for clasificacion in CLASIFICACIONES_V1:
        if (clasificacion["ancho_min"] <= ancho <= clasificacion["ancho_max"] and
            clasificacion["largo_min"] <= largo <= clasificacion["largo_max"]):
            return clasificacion["nombre"]
    return "Dor"

def cumple_restricciones_espaciales(casa):
    tipos_presentes = {obtener_nombre_funcional_por_rango(h.ancho, h.altura) for h in casa.habitaciones}
    
    for tipo_a, tipo_b in RESTRICCIONES_ESPACIALES_V1:
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


def generar_planos_v1():
    combinaciones = generar_combinaciones(habitaciones_v1)
    planos_filtrados = [plano for plano in combinaciones if cumple_restricciones_espaciales(plano)]
    return random.sample(planos_filtrados, min(len(planos_filtrados), len(planos_filtrados)))

def generar_combinaciones_sin_p5(planos_aleatorios):
    combinaciones_sin_p5 = []

    for casa in planos_aleatorios:
        nueva_casa = Casa(largo=casa.largo, ancho=casa.ancho)
            
        # Agregar todas las habitaciones excepto la que corresponde a "P5"
        for habitacion in casa.habitaciones:
            if habitacion.nombre != "P5":
                nueva_casa.habitaciones.append(habitacion)
            
        # Copiar el área usada y otras variables necesarias
        nueva_casa.area_usada = sum(hab.area() for hab in nueva_casa.habitaciones)
        nueva_casa.posicion_x = casa.posicion_x
        nueva_casa.posicion_y = casa.posicion_y
        nueva_casa.altura_fila_actual = casa.altura_fila_actual

        combinaciones_sin_p5.append(nueva_casa)
    
    return combinaciones_sin_p5  # ¡Añadir esta línea para retornar el resultado!

def mostrar_v1():
    st.header("Etapa V1: Diseño Base")
    
    # Usar un botón para generar los planos
    if st.button("Generar planos V1"):
        with st.spinner("Generando planos..."):
            # Mover la generación de planos aquí
            combinaciones = generar_combinaciones(habitaciones_v1)
            planos_filtrados = [plano for plano in combinaciones if cumple_restricciones_espaciales(plano)]
            st.session_state.planos_aleatorios = random.sample(planos_filtrados, min(len(planos_filtrados), len(planos_filtrados)))
        st.success(f"Se han generado {len(st.session_state.planos_aleatorios)} planos válidos")
    
    # Mostrar planos si existen
    if st.session_state.planos_aleatorios:
        st.subheader(f"Planos generados: {len(st.session_state.planos_aleatorios)}")
        
        # Usar pestañas para navegar entre planos
        tabs = st.tabs([f"Plano {i+1}" for i in range(len(st.session_state.planos_aleatorios))])
        
        for i, (tab, casa) in enumerate(zip(tabs, st.session_state.planos_aleatorios)):
            with tab:
                fig = visualizar_plano(casa, f"Plano {i+1}")
                st.pyplot(fig)
        
        # Selección para la siguiente etapa
        plano_seleccionado = st.selectbox(
            "Seleccione un plano para continuar a V2:", 
            options=range(1, len(st.session_state.planos_aleatorios) + 1), 
            format_func=lambda x: f"Plano {x}"
        )
        
        if st.button("Continuar con este plano"):
            # Guardar selección y avanzar
            st.session_state.plano_v1_seleccion = plano_seleccionado - 1
            st.session_state.combinaciones_sin_p5 = generar_combinaciones_sin_p5(
                [st.session_state.planos_aleatorios[st.session_state.plano_v1_seleccion]])
            st.success(f"¡Plano {plano_seleccionado} seleccionado! Ahora puedes continuar a V2.")




    
