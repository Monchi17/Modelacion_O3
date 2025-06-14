import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from itertools import permutations
import random
import numpy as np
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Modelación de Planos", layout="wide")

# Inicializar variables de estado
if 'plano_seleccionado' not in st.session_state:
    st.session_state.plano_seleccionado = None
if 'etapa' not in st.session_state:
    st.session_state.etapa = 'V1'
if 'planos_v2_generados' not in st.session_state:
    st.session_state.planos_v2_generados = False

# Dimensiones de la casa para V1
largo_casa_v1 = 2.440 * 2
ancho_casa_v1 = 2.440 * 3

# Dimensiones de la casa para V2
largo_casa_v2 = 2 * 2.440
ancho_casa_v2 = 4 * 2.440
        
# Clasificación por rangos de ancho y altura para V1
CLASIFICACIONES_V1 = [
    {"nombre": "Baño", "ancho_min": 0.0, "ancho_max": 1.351, "largo_min": 0.0, "largo_max": 2.983},
    {"nombre": "Dor", "ancho_min": 3.5, "ancho_max": 3.6, "largo_min": 3.9, "largo_max": 4.0},
    {"nombre": "Cocina - Comedor", "ancho_min": 2.5, "ancho_max": 2.6, "largo_min": 2.8, "largo_max": 2.9},
    {"nombre": "Estar", "ancho_min": 2.2, "ancho_max": 2.4, "largo_min": 2.4, "largo_max": 4.0},
    {"nombre": "Recibidor", "ancho_min": 2.2, "ancho_max": 4.9, "largo_min": 1.4, "largo_max": 1.6}]

RESTRICCIONES_ESPACIALES_V1 = {
    ("Baño", "Dor"),
    ("Estar", "Recibidor"),
    ("Recibidor", "Cocina - Comedor"),
    ("Estar", "Cocina - Comedor"),}

# Clasificación para V2
CLASIFICACIONES_V2 = [
    {"nombre": "Baño", "ancho_min": 0.0, "ancho_max": 1.351, "largo_min": 0.0, "largo_max": 2.983},
    {"nombre": "Dor", "ancho_min": 3.5, "ancho_max": 3.6, "largo_min": 3.9, "largo_max": 4.0},
    {"nombre": "Cocina", "ancho_min": 2.5, "ancho_max": 2.6, "largo_min": 2.8, "largo_max": 2.9},
    {"nombre": "Comedor", "ancho_min": 2.2, "ancho_max": 2.4, "largo_min": 2.8, "largo_max": 2.9},
    {"nombre": "Estar", "ancho_min": 2.2, "ancho_max": 2.4, "largo_min": 2.4, "largo_max": 4.0},
    {"nombre": "Recibidor", "ancho_min": 2.2, "ancho_max": 4.9, "largo_min": 1.4, "largo_max": 1.6},
]

RESTRICCIONES_ESPACIALES_V2 = {
    ("Baño", "Dor"),
    ("Cocina", "Comedor"),
    ("Estar", "Recibidor"),
    ("Estar", "Comedor"),
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

    # Versión para Streamlit de V1
    def visualizar_plano_v1(self):
        fig, ax = plt.subplots(figsize=(6, 6))
        contador_dormitorios = 1

        for hab in self.habitaciones:
            poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
            ax.add_patch(poligono)
            cx = sum([v[0] for v in hab.vertices]) / len(hab.vertices)
            cy = sum([v[1] for v in hab.vertices]) / len(hab.vertices)
            nombre_funcional = obtener_nombre_funcional_por_rango(hab.ancho, hab.altura, CLASIFICACIONES_V1)
            
            if nombre_funcional == "Dor":
                texto = f"{hab.nombre}\nDor {contador_dormitorios}"
                contador_dormitorios += 1
            else:
                texto = f"{hab.nombre}\n{nombre_funcional}"

            ax.text(cx, cy, texto, ha='center', va='center', fontsize=12)
            
        ax.set_xlim(0, self.largo)
        ax.set_ylim(0, self.ancho)
        ax.set_aspect('equal', adjustable='box')
        
        # Convertir el gráfico a una imagen para Streamlit
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    # Versión para Streamlit de V2
    def visualizar_plano_v2(self):
        fig, ax = plt.subplots(figsize=(6, 6))
        for hab in self.habitaciones:
            poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
            ax.add_patch(poligono)
            cx = sum([v[0] for v in hab.vertices]) / len(hab.vertices)
            cy = sum([v[1] for v in hab.vertices]) / len(hab.vertices)

            nombre_funcional = obtener_nombre_funcional_por_rango(hab.ancho, hab.altura, CLASIFICACIONES_V2)

            ax.text(cx, cy, f"{hab.nombre}\n{nombre_funcional}", ha='center', va='center', fontsize=8)

        ax.set_xlim(0, self.largo)
        ax.set_ylim(0, self.ancho)
        ax.set_aspect('equal', adjustable='box')
        
        # Convertir el gráfico a una imagen para Streamlit
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf
        
    def reflejar_habitacion(habitacion, largo_casa):
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
            casa_reflejada.agregar_habitacion(reflejar_habitacion(habitacion, casa.largo))
        return casa_reflejada
    todos_los_planos = []

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

def obtener_nombre_funcional_por_rango(ancho, largo, clasificaciones):
    for clasificacion in clasificaciones:
        if (clasificacion["ancho_min"] <= ancho <= clasificacion["ancho_max"] and
            clasificacion["largo_min"] <= largo <= clasificacion["largo_max"]):
            return clasificacion["nombre"]
    return "Dor"

def cumple_restricciones_espaciales(casa, clasificaciones, restricciones):
    tipos_presentes = {obtener_nombre_funcional_por_rango(h.ancho, h.altura, clasificaciones) for h in casa.habitaciones}
    
    for tipo_a, tipo_b in restricciones:
        if tipo_a in tipos_presentes and tipo_b in tipos_presentes:
            encontrados_adyacentes = False
            for i in range(len(casa.habitaciones)):
                for j in range(i + 1, len(casa.habitaciones)):
                    hab1 = casa.habitaciones[i]
                    hab2 = casa.habitaciones[j]
                    tipo1 = obtener_nombre_funcional_por_rango(hab1.ancho, hab1.altura, clasificaciones)
                    tipo2 = obtener_nombre_funcional_por_rango(hab2.ancho, hab2.altura, clasificaciones)
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
            casa = Casa(largo=largo_casa_v1, ancho=ancho_casa_v1)
            es_valido = True
            for habitacion in permutacion:
                if not casa.agregar_habitacion(habitacion):
                    es_valido = False
                    break
            if es_valido and casa.es_valida() and casa.agregar_habitacion_inferior(habitacion_final):
                if casa.cumple_dimensiones_exactas():
                    combinaciones_validas.append(casa)
    return combinaciones_validas

def reflejar_habitacion(habitacion, largo_casa):
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
    casa_reflejada = Casa(casa.largo, casa.ancho, casa.tipo)  # Mismo tipo que el original
    for habitacion in casa.habitaciones:
        casa_reflejada.agregar_habitacion(reflejar_habitacion(habitacion, casa.largo))
    return casa_reflejada

def seleccionar_plano(index):
    st.session_state.plano_seleccionado = index

def generar_planos_v1():
    # Generar combinaciones válidas para V1
    if 'planos_generados' not in st.session_state:
        with st.spinner("Generando planos V1..."):
            combinaciones = generar_combinaciones(habitaciones_v1)
            planos_filtrados = [plano for plano in combinaciones if cumple_restricciones_espaciales(plano, CLASIFICACIONES_V1, RESTRICCIONES_ESPACIALES_V1)]
            
            # Si no hay planos válidos, usar planos predefinidos
            if not planos_filtrados:
                st.warning("No se pudieron generar planos con las restricciones actuales. Mostrando planos predefinidos.")
                planos_filtrados = generar_planos_predefinidos()

            st.session_state.planos_generados = planos_filtrados
            
    return st.session_state.planos_generados

def quitar_p5_de_planos(planos_v1):
    combinaciones_sin_p5 = []
    for casa in planos_v1:
        nueva_casa = Casa(largo=casa.largo, ancho=casa.ancho)
        for habitacion in casa.habitaciones:
            if habitacion.nombre != "P5":
                nueva_casa.habitaciones.append(habitacion)
        nueva_casa.area_usada = sum(hab.area() for hab in nueva_casa.habitaciones)
        nueva_casa.posicion_x = casa.posicion_x
        nueva_casa.posicion_y = casa.posicion_y
        nueva_casa.altura_fila_actual = casa.altura_fila_actual
        combinaciones_sin_p5.append(nueva_casa)
    return combinaciones_sin_p5

def generar_planos_v2_desde_v1_sin_p5(combinaciones_sin_p5, largo_casa, ancho_casa):
    todos_los_planos = []
    
    for i in range(len(combinaciones_sin_p5)):
        casa1 = Casa(largo_casa, ancho_casa)
        casa1.agregar_habitacion(Habitacion("P7", [(0, 5.850), (2.585, 5.850), (2.585, 9.765), (0, 9.765)]))
        casa1.agregar_habitacion(Habitacion("P6", [(2.585, 5.850), (4.880, 5.850), (4.880, 8.280), (2.585, 8.280)]))
        casa1.agregar_habitacion(Habitacion("P8", [(2.585, 8.290), (4.880, 8.290), (4.880, 9.765), (2.585, 9.765)]))
        casa1.habitaciones.extend(combinaciones_sin_p5[i].habitaciones)
        todos_los_planos.append(casa1)
    
        casa2 = Casa(largo_casa, ancho_casa)
        casa2.agregar_habitacion(Habitacion("P6", [(0, 5.839), (2.295, 5.839), (2.295, 8.272), (0, 8.272)]))
        casa2.agregar_habitacion(Habitacion("P8", [(0, 8.272), (2.295, 8.272), (2.295, 9.759), (0, 9.759)]))
        casa2.agregar_habitacion(Habitacion("P7", [(2.295, 5.839), (4.880, 5.839), (4.880, 9.759), (2.295, 9.759)]))
        casa2.habitaciones.extend(combinaciones_sin_p5[i].habitaciones)
        todos_los_planos.append(casa2)

    return todos_los_planos

def generar_planos_v2():
    if not st.session_state.planos_v2_generados:
        with st.spinner("Generando planos V2..."):
            plano_v1_seleccionado = st.session_state.plano_v1_seleccionado

            # Paso 1: quitar habitación P5
            combinaciones_sin_p5 = []
            planos_aleatorios = st.session_state.planos_generados

            for casa in planos_aleatorios:  # Cambiar combinaciones por planos_aleatorios
                # Crear una nueva instancia de Casa para almacenar la combinación sin "P5"
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
            
                # Añadir la nueva casa a la lista
                combinaciones_sin_p5.append(nueva_casa)

            # Paso 2: generar planos V2
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
                    casa_reflejada.agregar_habitacion(reflejar_habitacion(habitacion, casa.largo))
                return casa_reflejada
            
            todos_los_planos = []
            for i in range(len(combinaciones_sin_p5)):
                casa1 = Casa(largo_casa, ancho_casa)
                casa1.agregar_habitacion(Habitacion("P7", [(0, 5.850), (2.585, 5.850), (2.585, 9.765), (0, 9.765)]))
                casa1.agregar_habitacion(Habitacion("P6", [(2.585, 5.850), (4.880, 5.850), (4.880, 8.280), (2.585, 8.280)]))
                casa1.agregar_habitacion(Habitacion("P8", [(2.585, 8.290), (4.880, 8.290), (4.880, 9.765), (2.585, 9.765)]))
                casa1.habitaciones.extend(combinaciones_sin_p5[i].habitaciones)
                todos_los_planos.append(casa1)
                
                casa2 = Casa(largo_casa, ancho_casa)
                casa2.agregar_habitacion(Habitacion("P6", [(0, 5.839), (2.295, 5.839), (2.295, 8.272), (0, 8.272)]))
                casa2.agregar_habitacion(Habitacion("P8", [(0, 8.272), (2.295, 8.272), (2.295, 9.759), (0, 9.759)]))
                casa2.agregar_habitacion(Habitacion("P7", [(2.295, 5.839), (4.880, 5.839), (4.880, 9.759), (2.295, 9.759)]))
                casa2.habitaciones.extend(combinaciones_sin_p5[i].habitaciones)
                todos_los_planos.append(casa2)
            
            planos_filtrados = [plano for plano in todos_los_planos if cumple_restricciones_espaciales(plano)]
            planos_seleccionados = planos_filtrados.copy()

            # todos_los_planos = generar_planos_v2_desde_v1_sin_p5(combinaciones_sin_p5, largo_casa_v2, ancho_casa_v2)

            # # Paso 3: aplicar restricciones
            # planos_filtrados = [plano for plano in todos_los_planos if cumple_restricciones_espaciales(
            #     plano, CLASIFICACIONES_V2, RESTRICCIONES_ESPACIALES_V2)]
            # if not planos_filtrados:
            #     st.warning("Ningún plano V2 cumple con las restricciones. Mostrando todos los disponibles.")
            #     planos_filtrados = todos_los_planos

            # planos_seleccionados = planos_filtrados.copy()
            # planos_V2 =[]
            
            # Paso 4: generar visualización con subplots (como en matplotlib original)
            num_planos_total = len(planos_seleccionados) * 2  # Original + reflejado
            num_cols = min(2, num_planos_total)
            num_filas = (num_planos_total + num_cols - 1) // num_cols

            fig, axs = plt.subplots(num_filas, num_cols, figsize=(20, 20))
            axs = axs.flatten() if num_planos_total > 1 else [axs]

            for i, plano in enumerate(planos_seleccionados):
                for reflejado, label in [(plano, "original"), (reflejar_plano(plano), "reflejado")]:
                    idx = i * 2 if label == "original" else i * 2 + 1
                    dormitorios, baños, otras = [], [], []

                    for hab in reflejado.habitaciones:
                        cx = sum(x for x, _ in hab.vertices) / len(hab.vertices)
                        cy = sum(y for _, y in hab.vertices) / len(hab.vertices)
                        nombre_funcional = obtener_nombre_funcional_por_rango(hab.ancho, hab.altura, CLASIFICACIONES_V2)

                        if nombre_funcional == "Dor":
                            dormitorios.append((hab, cx, cy))
                        elif nombre_funcional == "Baño":
                            baños.append((hab, cx, cy))
                        else:
                            otras.append((hab, cx, cy, nombre_funcional))

                    dormitorios.sort(key=lambda x: (x[2], x[1]))
                    baños.sort(key=lambda x: (x[2], x[1]))

                    for idx_hab, (hab, cx, cy) in enumerate(dormitorios, 1):
                        axs[idx].add_patch(Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5))
                        axs[idx].text(cx, cy, f"{hab.nombre}\nDor {idx_hab}", ha='center', va='center', fontsize=12)

                    for idx_hab, (hab, cx, cy) in enumerate(baños, 1):
                        axs[idx].add_patch(Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5))
                        axs[idx].text(cx, cy, f"{hab.nombre}\nBaño {idx_hab}", ha='center', va='center', fontsize=12)

                    for hab, cx, cy, nombre_funcional in otras:
                        axs[idx].add_patch(Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5))
                        axs[idx].text(cx, cy, f"{hab.nombre}\n{nombre_funcional}", ha='center', va='center', fontsize=12)

                    axs[idx].set_xlim(0, plano.largo)
                    axs[idx].set_ylim(0, plano.ancho)
                    axs[idx].set_title(f"Plano {idx + 1}", fontsize=14)
                    axs[idx].set_aspect('equal', adjustable='box')

                    planos_V2.append(reflejado if label == "reflejado" else plano)

            # Ocultar subplots vacíos
            for j in range(len(planos_V2), len(axs)):
                axs[j].axis('off')

            plt.tight_layout()
            st.pyplot(fig)

            # Guardar para uso posterior
            st.session_state.planos_v2 = planos_V2
            st.session_state.planos_v2_generados = True

    return st.session_state.planos_v2

def mostrar_planos_v1(planos):
    # Crear 4 columnas para los planos
    cols = st.columns(4)
    
    # Para cada plano, mostrar en una columna
    for i, plano in enumerate(planos):
        with cols[i % 4]:
            st.subheader(f"Plano {i + 1}")
            img = plano.visualizar_plano_v1()
            st.image(img, use_column_width=True)
            
            # Botón de selección
            if st.session_state.plano_seleccionado == i:
                st.success("✓ Seleccionado")
                st.button("Seleccionar", key=f"btn_{i}", disabled=True)
            else:
                if st.button("Seleccionar", key=f"btn_{i}"):
                    seleccionar_plano(i)
                    st.rerun()

def mostrar_planos_v2(planos):
    # Crear 4 columnas para los planos
    cols = st.columns(4)
    
    # Para cada plano, mostrar en una columna
    for i, plano in enumerate(planos):
        with cols[i % 4]:
            st.subheader(f"Plano {i + 1}")
            img = plano.visualizar_plano_v2()
            st.image(img, use_column_width=True)
            
            # Botón de selección
            if 'plano_seleccionado_v2' not in st.session_state:
                st.session_state.plano_seleccionado_v2 = None
                
            if st.session_state.plano_seleccionado_v2 == i:
                st.success("✓ Seleccionado")
                st.button("Seleccionar", key=f"btn_v2_{i}", disabled=True)
            else:
                if st.button("Seleccionar", key=f"btn_v2_{i}"):
                    st.session_state.plano_seleccionado_v2 = i
                    st.rerun()

def siguiente_paso():
    if st.session_state.plano_seleccionado is not None:
        st.session_state.etapa = 'V2'
        st.success("¡Avanzando a la modelación V2!")
    else:
        st.error("Por favor, selecciona un plano antes de continuar")

if st.session_state.etapa == 'V1':
    st.title("Modelación de Planos - V1")
    
    # Generar planos V1
    planos_v1 = generar_planos_v1()
    
    # Mostrar los planos
    st.write("Selecciona uno de los planos disponibles:")
    mostrar_planos_v1(planos_v1)
    
    # Botón para continuar
    st.write("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Siguiente", use_container_width=True):
            if st.session_state.plano_seleccionado is not None:
                # Guardar el plano seleccionado antes de cambiar de etapa
                if 'plano_v1_seleccionado' not in st.session_state:
                    st.session_state.plano_v1_seleccionado = st.session_state.planos_generados[st.session_state.plano_seleccionado]
                
                # Cambiar a la etapa V2
                st.session_state.etapa = 'V2'
                st.rerun()
            else:
                st.error("Por favor, selecciona un plano antes de continuar")

elif st.session_state.etapa == 'V2':
    st.title("Modelación de Planos - V2")
    
    # Verificar que tenemos un plano seleccionado de V1
    if 'plano_v1_seleccionado' not in st.session_state:
        st.error("No hay plano seleccionado de la etapa V1. Volviendo a la selección...")
        st.session_state.etapa = 'V1'
        st.rerun()
        
    planos_v2 = generar_planos_v2()

    # Mostrar los planos V2
    if planos_v2:
        st.write("Selecciona uno de los planos disponibles:")
        mostrar_planos_v2(planos_v2)
        
        # Botón para volver a V1
        st.write("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("Volver a V1", use_container_width=True):
                st.session_state.etapa = 'V1'
                if 'plano_seleccionado_v2' in st.session_state:
                    del st.session_state.plano_seleccionado_v2
                st.rerun()
        
        # Botón para finalizar
        with col3:
            if st.button("Finalizar", use_container_width=True):
                if 'plano_seleccionado_v2' in st.session_state and st.session_state.plano_seleccionado_v2 is not None:
                    st.session_state.etapa = 'final'
                    st.rerun()
                else:
                    st.error("Por favor, selecciona un plano antes de finalizar")
    else:
        st.error("No se pudieron generar planos V2. Volviendo a V1...")
        st.session_state.etapa = 'V1'
        time.sleep(2)  # Dar tiempo para leer el mensaje
        st.rerun()
