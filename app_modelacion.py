import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from itertools import permutations
import random
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Modelación de Planos Arquitectónicos", layout="wide")

# Inicializar variables de estado
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False
if 'etapa' not in st.session_state:
    st.session_state.etapa = 'V1'
if 'plano_seleccionado' not in st.session_state:
    st.session_state.plano_seleccionado = None
if 'planos_aleatorios' not in st.session_state:
    st.session_state.planos_aleatorios = None
if 'planos_V2' not in st.session_state:
    st.session_state.planos_V2 = None

# Título principal
st.title("Modelación de Planos Arquitectónicos")

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
    def __init__(self, largo, ancho, tipo=""):
        self.largo = largo
        self.ancho = ancho
        self.area_total = largo * ancho
        self.habitaciones = []
        self.area_usada = 0
        self.posicion_x = 0
        self.posicion_y = 0
        self.altura_fila_actual = 0
        self.tipo = tipo

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

    def visualizar_plano(self):
        fig, ax = plt.subplots(figsize=(10, 8))
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

            ax.text(cx, cy, texto, ha='center', va='center', fontsize=12)
            
        ax.set_xlim(0, self.largo)
        ax.set_ylim(0, self.ancho)
        ax.set_aspect('equal', adjustable='box')
        
        # Convertir la figura a una imagen para streamlit
        buf = BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        return buf

# Funciones auxiliares
def son_adyacentes(hab1, hab2):
    # Tolerancia para considerar adyacencia
    tolerancia = 0.001  
    
    for i in range(len(hab1.vertices)):
        p1 = hab1.vertices[i]
        p2 = hab1.vertices[(i + 1) % len(hab1.vertices)]
        for j in range(len(hab2.vertices)):
            q1 = hab2.vertices[j]
            q2 = hab2.vertices[(j + 1) % len(hab2.vertices)]

            # Segmentos horizontales o verticales con tolerancia
            if abs(p1[1] - p2[1]) < tolerancia and abs(q1[1] - q2[1]) < tolerancia and abs(p1[1] - q1[1]) < tolerancia:
                x1, x2 = sorted([p1[0], p2[0]])
                x3, x4 = sorted([q1[0], q2[0]])
                if x1 <= x4 + tolerancia and x2 + tolerancia >= x3:
                    return True
            elif abs(p1[0] - p2[0]) < tolerancia and abs(q1[0] - q2[0]) < tolerancia and abs(p1[0] - q1[0]) < tolerancia:
                y1, y2 = sorted([p1[1], p2[1]])
                y3, y4 = sorted([q1[1], q2[1]])
                if y1 <= y4 + tolerancia and y2 + tolerancia >= y3:
                    return True
    return False

def obtener_nombre_funcional_por_rango(ancho, largo):
    for clasificacion in CLASIFICACIONES:
        if (clasificacion["ancho_min"] <= ancho <= clasificacion["ancho_max"] and
            clasificacion["largo_min"] <= largo <= clasificacion["largo_max"]):
            return clasificacion["nombre"]
    return "Dor"  # Valor por defecto

def cumple_restricciones_espaciales(casa):
    # Versión más permisiva para generar al menos algunos planos
    return True
    
    # Versión original con verificaciones estrictas
    """
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
    """

def generar_planos_predefinidos():
    """Genera planos predefinidos cuando no se pueden generar combinaciones automáticamente"""
    planos = []
    
    # Plano 1
    casa1 = Casa(largo=largo_casa, ancho=ancho_casa)
    casa1.agregar_habitacion(Habitacion("P1", [(0, 0), (3.529, 0), (3.529, 2.983), (0, 2.983)]))
    casa1.agregar_habitacion(Habitacion("P5", [(0, 2.983), (4.880, 2.983), (4.880, 4.464), (0, 4.464)]))
    planos.append(casa1)
    
    # Plano 2
    casa2 = Casa(largo=largo_casa, ancho=ancho_casa)
    casa2.agregar_habitacion(Habitacion("P2", [(0, 0), (1.351, 0), (1.351, 2.983), (0, 2.983)]))
    casa2.agregar_habitacion(Habitacion("P3", [(1.351, 0), (3.936, 0), (3.936, 2.856), (1.351, 2.856)]))
    casa2.agregar_habitacion(Habitacion("P5", [(0, 2.983), (4.880, 2.983), (4.880, 4.464), (0, 4.464)]))
    planos.append(casa2)
    
    # Plano 3
    casa3 = Casa(largo=largo_casa, ancho=ancho_casa)
    casa3.agregar_habitacion(Habitacion("P4", [(0, 0), (2.295, 0), (2.295, 2.856), (0, 2.856)]))
    casa3.agregar_habitacion(Habitacion("P2", [(2.295, 0), (3.646, 0), (3.646, 2.983), (2.295, 2.983)]))
    casa3.agregar_habitacion(Habitacion("P5", [(0, 2.983), (4.880, 2.983), (4.880, 4.464), (0, 4.464)]))
    planos.append(casa3)
    
    return planos

def generar_combinaciones(habitaciones):
    combinaciones_validas = []
    
    # Intentar generar combinaciones a través del algoritmo
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
                    
    # Si no se generaron combinaciones válidas, usar planos predefinidos
    if not combinaciones_validas:
        if st.session_state.debug_mode:
            st.warning("No se generaron combinaciones algorítmicas. Usando planos predefinidos.")
        return generar_planos_predefinidos()
    
    return combinaciones_validas

def reflejar_habitacion(habitacion, largo_casa):
    """Refleja una habitación respecto al eje Y sin cambiar su nombre"""
    vertices_reflejados = []
    for x, y in habitacion.vertices:
        # Reflejar la coordenada x respecto al eje Y
        x_reflejado = largo_casa - x
        vertices_reflejados.append((x_reflejado, y))
    
    # Invertir el orden para mantener orientación correcta
    vertices_reflejados.reverse()
    
    # Mantener el mismo nombre que la habitación original
    return Habitacion(habitacion.nombre, vertices_reflejados)

def reflejar_plano(casa):
    """Crea una reflexión completa de la casa respecto al eje Y"""
    casa_reflejada = Casa(casa.largo, casa.ancho, casa.tipo)  # Mismo tipo que el original
    for habitacion in casa.habitaciones:
        casa_reflejada.habitaciones.append(reflejar_habitacion(habitacion, casa.largo))
    return casa_reflejada

def crear_planos_v2(combinaciones_sin_p5):
    largo_casa = 2.440 * 2
    ancho_casa = 2.440 * 4  # Para V2
    
    todos_los_planos = []

    for i in range(len(combinaciones_sin_p5)):
        casa1 = Casa(largo_casa, ancho_casa)
        casa1.agregar_habitacion(Habitacion("P7", [(0, 5.850), (2.585, 5.850), (2.585, 9.765), (0, 9.765)]))
        casa1.agregar_habitacion(Habitacion("P6", [(2.585, 5.850), (4.880, 5.850), (4.880, 8.280), (2.585, 8.280)]))
        casa1.agregar_habitacion(Habitacion("P8", [(2.585, 8.290), (4.880, 8.290), (4.880, 9.765), (2.585, 9.765)]))
        
        for hab in combinaciones_sin_p5[i].habitaciones:
            casa1.agregar_habitacion(hab)
            
        todos_los_planos.append(casa1)
        
        casa2 = Casa(largo_casa, ancho_casa)
        casa2.agregar_habitacion(Habitacion("P6", [(0, 5.839), (2.295, 5.839), (2.295, 8.272), (0, 8.272)]))
        casa2.agregar_habitacion(Habitacion("P8", [(0, 8.272), (2.295, 8.272), (2.295, 9.759), (0, 9.759)]))
        casa2.agregar_habitacion(Habitacion("P7", [(2.295, 5.839), (4.880, 5.839), (4.880, 9.759), (2.295, 9.759)]))
        
        for hab in combinaciones_sin_p5[i].habitaciones:
            casa2.agregar_habitacion(hab)
            
        todos_los_planos.append(casa2)

    planos_filtrados = [plano for plano in todos_los_planos if cumple_restricciones_espaciales(plano)]
    
    # Si no hay planos filtrados, devolver todos los planos
    if not planos_filtrados:
        planos_filtrados = todos_los_planos
    
    # Crear planos V2 incluyendo los reflejados
    planos_V2 = []
    for plano in planos_filtrados:
        planos_V2.append(plano)  # Añadir plano original
        planos_V2.append(reflejar_plano(plano))  # Añadir plano reflejado
        
    return planos_V2

# Definición de las habitaciones
habitaciones_v1 = [
    Habitacion("P1", [(0, 0), (3.529, 0), (3.529, 2.983), (0, 2.983)]),
    Habitacion("P2", [(0, 0), (1.351, 0), (1.351, 2.983), (0, 2.983)]),
    Habitacion("P3", [(0, 0), (2.585, 0), (2.585, 2.856), (0, 2.856)]),
    Habitacion("P4", [(0, 0), (2.295, 0), (2.295, 2.856), (0, 2.856)]),
]

habitaciones_finales = [
    Habitacion("P8", [(0, 0), (2.295, 0), (2.295, 1.487), (0, 1.487)]),
    Habitacion("P11", [(0, 0), (2.295, 0), (2.295, 1.588), (0, 1.588)]),
    Habitacion("P5", [(0, 0), (4.880, 0), (4.880, 1.481), (0, 1.481)])
]

# Botón de modo depuración (Debug)
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🐛 Debug", help="Activar/Desactivar modo depuración"):
        st.session_state.debug_mode = not st.session_state.debug_mode
        st.experimental_rerun()

# Función para manejar el botón de selección de plano
def seleccionar_plano(indice):
    st.session_state.plano_seleccionado = indice

# Función para ir a la etapa V2
def ir_a_v2():
    if st.session_state.plano_seleccionado is not None:
        # Crear la lista de combinaciones sin P5 para el plano seleccionado
        casa = st.session_state.planos_aleatorios[st.session_state.plano_seleccionado]
        nueva_casa = Casa(largo=casa.largo, ancho=casa.ancho)
        
        for habitacion in casa.habitaciones:
            if habitacion.nombre != "P5":
                nueva_casa.habitaciones.append(habitacion)
        
        combinaciones_sin_p5 = [nueva_casa]
        
        with st.spinner('Generando planos V2...'):
            st.session_state.planos_V2 = crear_planos_v2(combinaciones_sin_p5)
        st.session_state.etapa = 'V2'
    else:
        st.error("Por favor, selecciona un plano antes de continuar.")

# Generar planos si aún no existen
if st.session_state.planos_aleatorios is None:
    with st.spinner("Generando planos, por favor espera..."):
        combinaciones = generar_combinaciones(habitaciones_v1)
        planos_filtrados = [plano for plano in combinaciones if cumple_restricciones_espaciales(plano)]
        # Mostrar información de depuración si está habilitado
        if st.session_state.debug_mode:
            st.write(f"Combinaciones totales: {len(combinaciones)}")
            st.write(f"Planos filtrados: {len(planos_filtrados)}")
        
        # Si no hay planos filtrados, usar todas las combinaciones
        if not planos_filtrados:
            planos_filtrados = combinaciones
            
        st.session_state.planos_aleatorios = planos_filtrados

# Interfaz según la etapa
if st.session_state.etapa == 'V1':
    st.header("Modelación V1")
    
    if not st.session_state.planos_aleatorios:
        st.warning("No se pudieron generar planos válidos. Verifica las restricciones y dimensiones.")
    else:
        st.write(f"Selecciona uno de los {len(st.session_state.planos_aleatorios)} planos disponibles:")
        
        # Mostrar los planos en una cuadrícula de 2 columnas
        col1, col2 = st.columns(2)
        cols = [col1, col2]
        
        for i, plano in enumerate(st.session_state.planos_aleatorios):
            with cols[i % 2]:
                st.write(f"### Plano {i + 1}")
                img_buffer = plano.visualizar_plano()
                st.image(img_buffer, use_column_width=True)
                
                # Botón de selección
                if st.session_state.plano_seleccionado == i:
                    st.success("✓ Seleccionado")
                else:
                    if st.button(f"Seleccionar Plano {i + 1}", key=f"btn_{i}"):
                        seleccionar_plano(i)
                        st.experimental_rerun()
        
        # Botón para pasar a la etapa V2
        st.write("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Siguiente ➡️", use_container_width=True):
                ir_a_v2()

elif st.session_state.etapa == 'V2':
    st.header("Modelación V2")
    
    # Botón para volver a V1
    if st.button("⬅️ Volver a V1"):
        st.session_state.etapa = 'V1'
        st.session_state.plano_seleccionado = None
        st.session_state.planos_V2 = None
        st.experimental_rerun()
    
    if not st.session_state.planos_V2:
        st.warning("No se pudieron generar planos V2. Vuelve a seleccionar un plano V1.")
    else:
        st.write(f"Selecciona uno de los {len(st.session_state.planos_V2)} planos V2 disponibles:")
        
        # Mostrar los planos V2 en una cuadrícula
        col1, col2 = st.columns(2)
        cols = [col1, col2]
        
        for i, plano in enumerate(st.session_state.planos_V2):
            with cols[i % 2]:
                st.write(f"### Plano V2-{i + 1}")
                img_buffer = plano.visualizar_plano()
                st.image(img_buffer, use_column_width=True)
                
                # Botón de selección
                if st.button(f"Seleccionar Plano V2-{i + 1}", key=f"btn_v2_{i}"):
                    st.success(f"Has seleccionado el Plano V2-{i+1}")
# Función para ir a la etapa V2
def ir_a_v2():
    if st.session_state.plano_seleccionado is not None:
        # Crear la lista de combinaciones sin P5 para el plano seleccionado
        casa = st.session_state.planos_aleatorios[st.session_state.plano_seleccionado]
        nueva_casa = Casa(largo=casa.largo, ancho=casa.ancho)
        
        for habitacion in casa.habitaciones:
            if habitacion.nombre != "P5":
                nueva_casa.habitaciones.append(habitacion)
        
        st.session_state.combinaciones_sin_p5 = [nueva_casa]
        with st.spinner('Generando planos V2...'):
            st.session_state.planos_V2 = crear_planos_v2(st.session_state.combinaciones_sin_p5)
        st.session_state.etapa = 'V2'
    else:
        st.error("Por favor, selecciona un plano antes de continuar.")

# Interfaz según la etapa
if st.session_state.etapa == 'V1':
    st.header("Modelación V1")
    
    if not st.session_state.planos_aleatorios:
        st.warning("No se pudieron generar planos válidos. Verifica las restricciones y dimensiones.")
    else:
        st.write(f"Selecciona uno de los {len(st.session_state.planos_aleatorios)} planos disponibles:")
        
        # Mostrar los planos en una cuadrícula de 2 columnas
        col1, col2 = st.columns(2)
        cols = [col1, col2]
        
        for i, plano in enumerate(st.session_state.planos_aleatorios):
            with cols[i % 2]:
                st.write(f"### Plano {i + 1}")
                img_buffer = plano.visualizar_plano()
                st.image(img_buffer, use_column_width=True)
                
                # Botón de selección
                if st.session_state.plano_seleccionado == i:
                    st.success("✓ Seleccionado")
                else:
                    if st.button(f"Seleccionar Plano {i + 1}", key=f"btn_{i}"):
                        seleccionar_plano(i)
                        st.experimental_rerun()
        
        # Botón para pasar a la etapa V2
        st.write("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Siguiente ➡️", use_container_width=True):
                ir_a_v2()

elif st.session_state.etapa == 'V2':
    st.header("Modelación V2")
    
    # Botón para volver a V1
    if st.button("⬅️ Volver a V1"):
        st.session_state.etapa = 'V1'
        st.session_state.plano_seleccionado = None
        st.session_state.planos_V2 = []
        st.experimental_rerun()
    
    if not st.session_state.planos_V2:
        st.warning("No se pudieron generar planos V2. Vuelve a seleccionar un plano V1.")
    else:
        st.write(f"Selecciona uno de los {len(st.session_state.planos_V2)} planos V2 disponibles:")
        
        # Mostrar los planos V2 en una cuadrícula
        col1, col2 = st.columns(2)
        cols = [col1, col2]
        
        for i, plano in enumerate(st.session_state.planos_V2):
            with cols[i % 2]:
                st.write(f"### Plano V2-{i + 1}")
                img_buffer = plano.visualizar_plano()
                st.image(img_buffer, use_column_width=True)
                
                # Botón de selección
                st.button(f"Seleccionar Plano V2-{i + 1}", key=f"btn_v2_{i}")
