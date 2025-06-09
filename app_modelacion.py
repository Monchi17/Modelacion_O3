import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from itertools import permutations
import random
import matplotlib
matplotlib.use('Agg')  # Necesario para Streamlit

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

# Definición de habitaciones
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

# Inicialización del estado de la aplicación
if 'etapa' not in st.session_state:
    st.session_state.etapa = 'V1'
if 'plano_seleccionado' not in st.session_state:
    st.session_state.plano_seleccionado = None
if 'planos_v1' not in st.session_state:
    st.session_state.planos_v1 = []
if 'combinaciones_sin_p5' not in st.session_state:
    st.session_state.combinaciones_sin_p5 = []

def mostrar_v1():
    st.header("Modelación V1")
    
    # Generar planos si no se han generado antes
    if not st.session_state.planos_v1:
        with st.spinner("Generando planos..."):
            combinaciones = generar_combinaciones(habitaciones_v1)
            planos_filtrados = [plano for plano in combinaciones if cumple_restricciones_espaciales(plano)]
            num_planos_mostrar = min(4, len(planos_filtrados))
            st.session_state.planos_v1 = random.sample(planos_filtrados, num_planos_mostrar)
    
    # Crear una cuadrícula de planos con detección de clics
    st.write("### Haz clic en un plano para seleccionarlo:")
    
    # Crear dos filas de planos para mejor visualización
    row1 = st.columns(4)
    
    # Primera fila
    for i in range(min(4, len(st.session_state.planos_v1))):
        with row1[i]:
            fig, ax = plt.subplots(figsize=(6, 6))
            st.session_state.planos_v1[i].visualizar_plano(ax)
            ax.set_title(f"Plano {i + 1}", fontsize=15)
            
            # Área de figura con detección de clics
            clicked = st.button(f"Seleccionar Plano {i+1}", key=f"select_plan_{i}")
            st.pyplot(fig)
    
    
    # Mostrar información de selección
    if st.session_state.plano_seleccionado is not None:
        st.info(f"🏠 ✅Plano seleccionado: Plano {st.session_state.plano_seleccionado + 1}")
    
    # Botón de navegación en la esquina inferior izquierda
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Siguiente", key="btn_siguiente_v1"):
            if st.session_state.plano_seleccionado is not None:
                # Preparar el plano seleccionado para V2
                plano_seleccionado = st.session_state.planos_v1[st.session_state.plano_seleccionado]
                
                # Crear una copia sin P5 para V2
                casa_sin_p5 = Casa(largo=plano_seleccionado.largo, ancho=plano_seleccionado.ancho)
                for hab in plano_seleccionado.habitaciones:
                    if hab.nombre != "P5":
                        casa_sin_p5.habitaciones.append(hab)
                
                # Guardar para V2
                st.session_state.plano_v1_seleccionado = plano_seleccionado
                st.session_state.combinaciones_sin_p5 = [casa_sin_p5]
                st.session_state.etapa = 'V2'
            else:
                st.error("⚠️ Debes seleccionar un plano antes de continuar.")

def reflejar_habitacion(habitacion, largo_casa):
    """Refleja una habitación respecto al eje Y"""
    vertices_reflejados = []
    for x, y in habitacion.vertices:
        x_reflejado = largo_casa - x
        vertices_reflejados.append((x_reflejado, y))
    
    vertices_reflejados.reverse()
    return Habitacion(habitacion.nombre, vertices_reflejados)

def reflejar_plano(casa):
    """Crea una reflexión completa de la casa respecto al eje Y"""
    casa_reflejada = Casa(casa.largo, casa.ancho)
    for habitacion in casa.habitaciones:
        casa_reflejada.agregar_habitacion(reflejar_habitacion(habitacion, casa.largo))
    return casa_reflejada

def mostrar_v2():
    st.header("Modelación V2")
    
    if not st.session_state.combinaciones_sin_p5:
        st.error("No hay planos disponibles para V2. Por favor regresa a V1.")
        if st.button("Volver a V1"):
            st.session_state.etapa = 'V1'
        return
    
    # Generar planos V2 basados en el plano V1 seleccionado
    casa1 = Casa(largo_casa, ancho_casa)
    casa1.agregar_habitacion(Habitacion("P7", [(0, 5.850), (2.585, 5.850), (2.585, 9.765), (0, 9.765)]))
    casa1.agregar_habitacion(Habitacion("P6", [(2.585, 5.850), (4.880, 5.850), (4.880, 8.280), (2.585, 8.280)]))
    casa1.agregar_habitacion(Habitacion("P8", [(2.585, 8.290), (4.880, 8.290), (4.880, 9.765), (2.585, 9.765)]))
    casa1.habitaciones.extend(st.session_state.combinaciones_sin_p5[0].habitaciones)
    
    casa2 = Casa(largo_casa, ancho_casa)
    casa2.agregar_habitacion(Habitacion("P6", [(0, 5.839), (2.295, 5.839), (2.295, 8.272), (0, 8.272)]))
    casa2.agregar_habitacion(Habitacion("P8", [(0, 8.272), (2.295, 8.272), (2.295, 9.759), (0, 9.759)]))
    casa2.agregar_habitacion(Habitacion("P7", [(2.295, 5.839), (4.880, 5.839), (4.880, 9.759), (2.295, 9.759)]))
    casa2.habitaciones.extend(st.session_state.combinaciones_sin_p5[0].habitaciones)
    
    # Filtrar planos que cumplan restricciones
    planos_v2 = [plano for plano in [casa1, casa2] if cumple_restricciones_espaciales(plano)]
    
    # Generar versiones reflejadas
    planos_completos = []
    for plano in planos_v2:
        planos_completos.append(plano)  # Original
        planos_completos.append(reflejar_plano(plano))  # Reflejado
    
    # Guardar planos V2
    st.session_state.planos_v2 = planos_completos
    
    # Mostrar planos V2 (originales y reflejados)
    st.write("### Selecciona un plano V2:")
    
    num_planos = len(planos_completos)
    
    # Distribuir en filas de 2 planos
    for i in range(0, num_planos, 2):
        row = st.columns(2)
        for j in range(2):
            if i+j < num_planos:
                with row[j]:
                    fig, ax = plt.subplots(figsize=(6, 6))
                    planos_completos[i+j].visualizar_plano(ax)
                    ax.set_title(f"Plano V2-{i+j+1}", fontsize=15)
                    
                    # Área de figura con detección de clics
                    clicked = st.button(f"Seleccionar Plano V2-{i+j+1}", key=f"select_v2_plan_{i+j}")
                    st.pyplot(fig)
                    
                    if clicked:
                        st.session_state.plano_v2_seleccionado = i+j
                        st.success(f"✅ Plano V2-{i+j+1} seleccionado")
    
    # Mostrar información de selección
    if 'plano_v2_seleccionado' in st.session_state and st.session_state.plano_v2_seleccionado is not None:
        st.info(f"🏠 Plano V2 seleccionado: Plano V2-{st.session_state.plano_v2_seleccionado + 1}")
    
    # Botones de navegación
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("⬅️ Volver a V1"):
            st.session_state.etapa = 'V1'
    with col2:
        if st.button("Siguiente ➡️"):
            if 'plano_v2_seleccionado' in st.session_state and st.session_state.plano_v2_seleccionado is not None:
                st.session_state.etapa = 'V3'
                st.experimental_rerun()
            else:
                st.error("⚠️ Debes seleccionar un plano V2 antes de continuar.")

def main():
    st.title("Modelación de Planos de Vivienda")
    
    # Navegación entre etapas
    if st.session_state.etapa == 'V1':
        mostrar_v1()
    elif st.session_state.etapa == 'V2':
        mostrar_v2()
    elif st.session_state.etapa == 'V3':
        st.header("Modelación V3 - En desarrollo")
        st.write("Esta etapa está en desarrollo.")
        if st.button("⬅️ Volver a V2"):
            st.session_state.etapa = 'V2'

if __name__ == "__main__":
    main()
