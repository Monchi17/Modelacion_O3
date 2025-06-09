import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from itertools import permutations
import random
import numpy as np
import hashlib
import time

# Configuración de la página
st.set_page_config(page_title="Modelación O3 Libre Crecimiento", layout="wide")

# Título de la aplicación
st.title("Modelación O3 Libre Crecimiento - V1")
st.write("Generación de planos base para modelación de crecimiento libre")

# Inicializar variables de estado
if 'planos_generados' not in st.session_state:
    st.session_state['planos_generados'] = False
if 'plano_seleccionado' not in st.session_state:
    st.session_state['plano_seleccionado'] = None
if 'planos_filtrados' not in st.session_state:
    st.session_state['planos_filtrados'] = None
if 'hash_planos' not in st.session_state:
    st.session_state['hash_planos'] = {}

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

            ax.text(cx, cy, texto, ha='center', va='center', fontsize=10)
            
        ax.set_xlim(0, self.largo)
        ax.set_ylim(0, self.ancho)
        ax.set_aspect('equal', adjustable='box')

# Definición de las habitaciones
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

def generar_hash_plano(casa):
    """Genera un hash único para un plano"""
    info_plano = []
    for hab in sorted(casa.habitaciones, key=lambda h: h.nombre):
        vertices_str = ";".join([f"{round(x,3)},{round(y,3)}" for x, y in hab.vertices])
        info_plano.append(f"{hab.nombre}:{vertices_str}")
    
    plano_str = "|".join(info_plano).encode()
    return hashlib.md5(plano_str).hexdigest()[:8]  # Usar primeros 8 caracteres del hash

def visualizar_todos_planos(planos):
    """Visualiza todos los planos en una cuadrícula"""
    num_planos = len(planos)
    num_cols = min(4, num_planos)  # Máximo 4 columnas
    num_filas = (num_planos + num_cols - 1) // num_cols  # Redondeo hacia arriba
    
    fig, axs = plt.subplots(num_filas, num_cols, figsize=(5*num_cols, 5*num_filas))
    
    # Asegurarse de que axs sea siempre un array 2D
    if num_planos == 1:
        axs = np.array([[axs]])
    elif num_filas == 1:
        axs = axs.reshape(1, -1)
    
    # Diccionario para almacenar hash de cada plano
    hash_planos = {}
    
    for i, plano in enumerate(planos):
        # Calcular fila y columna para el plano actual
        fila = i // num_cols
        col = i % num_cols
        
        # Generar hash para el plano
        plano_hash = generar_hash_plano(plano)
        hash_planos[i] = plano_hash
        
        # Visualizar plano
        plano.visualizar_plano(axs[fila, col])
        axs[fila, col].set_title(f"Plano {i + 1} (ID: {plano_hash})", fontsize=12)
    
    # Ocultar ejes vacíos si hay más subplots que planos
    for i in range(num_planos, num_filas * num_cols):
        fila = i // num_cols
        col = i % num_cols
        axs[fila, col].set_visible(False)
    
    # Ajustar la distribución de los subplots
    plt.tight_layout()
    
    # Almacenar los hashes para referencia
    st.session_state['hash_planos'] = hash_planos
    
    return fig

# Función para seleccionar un plano
def seleccionar_plano(idx):
    st.session_state['plano_seleccionado'] = idx
    st.success(f"Has seleccionado el Plano {idx + 1} (ID: {st.session_state['hash_planos'][idx]})")

# Interfaz de usuario con Streamlit
generar_planos = st.button("Generar Planos V1", use_container_width=True)

if generar_planos or st.session_state['planos_generados']:
    if not st.session_state['planos_generados']:
        with st.spinner("Generando planos, por favor espera..."):
            progress_bar = st.progress(0)
            
            # Paso 1: Generar todas las combinaciones válidas
            progress_bar.progress(10, text="Generando combinaciones básicas...")
            combinaciones = generar_combinaciones(habitaciones_v1)
            
            # Paso 2: Filtrar planos que cumplen restricciones
            progress_bar.progress(50, text="Aplicando restricciones espaciales...")
            planos_filtrados = [plano for plano in combinaciones if cumple_restricciones_espaciales(plano)]
            
            # Guardar los planos en session_state
            st.session_state['planos_filtrados'] = planos_filtrados
            st.session_state['planos_generados'] = True
            
            progress_bar.progress(100, text="¡Planos generados exitosamente!")
            time.sleep(0.5)
            progress_bar.empty()
    
    # Mostrar información sobre los planos generados
    planos = st.session_state['planos_filtrados']
    st.success(f"Se han generado {len(planos)} planos que cumplen todas las restricciones.")
    
    # Crear pestañas para Vista Completa y Vista Individual
    tab1, tab2 = st.tabs(["Vista Completa", "Vista Individual"])
    
    with tab1:
        # Visualizar todos los planos
        fig_todos = visualizar_todos_planos(planos)
        st.pyplot(fig_todos)
        
        # Crear botones para seleccionar plano (organizados en filas de 4)
        st.write("### Selecciona un plano:")
        
        # Organizar botones en filas de 4
        num_planos = len(planos)
        num_filas_botones = (num_planos + 3) // 4  # Redondeo hacia arriba
        
        for fila in range(num_filas_botones):
            cols = st.columns(4)
            for col in range(4):
                idx = fila * 4 + col
                if idx < num_planos:
                    with cols[col]:
                        if st.button(f"Plano {idx + 1}", key=f"btn_{idx}", use_container_width=True):
                            seleccionar_plano(idx)
    
    with tab2:
        if st.session_state['plano_seleccionado'] is not None:
            # Mostrar el plano seleccionado con más detalle
            idx = st.session_state['plano_seleccionado']
            st.write(f"### Plano {idx + 1} seleccionado")
            
            fig, ax = plt.subplots(figsize=(10, 8))
            planos[idx].visualizar_plano(ax)
            ax.set_title(f"Detalle de Plano {idx + 1}", fontsize=16)
            st.pyplot(fig)
            
            # Mostrar información adicional del plano
            st.write("#### Información de habitaciones:")
            
            # Crear tabla con información de las habitaciones
            data = []
            for hab in planos[idx].habitaciones:
                nombre_funcional = obtener_nombre_funcional_por_rango(hab.ancho, hab.altura)
                data.append({
                    "Nombre": hab.nombre,
                    "Tipo": nombre_funcional,
                    "Ancho": f"{hab.ancho:.2f} m",
                    "Altura": f"{hab.altura:.2f} m",
                    "Área": f"{hab.area():.2f} m²"
                })
            
            st.table(data)
        else:
            st.info("Por favor, selecciona un plano en la pestaña Vista Completa.")

# Botón para avanzar a V2 (solo visible cuando hay un plano seleccionado)
if st.session_state.plano_seleccionado is not None:
    st.divider()
    st.write("### Fase siguiente")
    if st.button("Continuar a fase V2", type="primary", use_container_width=True):
        st.success(f"Avanzando a la fase V2 con el Plano {st.session_state.plano_seleccionado + 1}")
        # Aquí se guardaría el plano seleccionado para V2
        # y se redireccionaría a la siguiente página
