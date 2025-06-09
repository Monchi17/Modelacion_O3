import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from itertools import permutations
import random
import numpy as np


# Configuración de la página
st.set_page_config(page_title="Modelación O3 Libre Crecimiento", layout="wide")

# Título de la aplicación
st.title("Modelación planos de casa")

# Inicializar variables de estado
if 'fase_actual' not in st.session_state:
    st.session_state['fase_actual'] = 'V1'
if 'planos_generados' not in st.session_state:
    st.session_state['planos_generados'] = False
if 'plano_seleccionado' not in st.session_state:
    st.session_state['plano_seleccionado'] = None
if 'planos_filtrados' not in st.session_state:
    st.session_state['planos_filtrados'] = None
if 'combinaciones_sin_p5' not in st.session_state:
    st.session_state['combinaciones_sin_p5'] = None
if 'planos_v2' not in st.session_state:
    st.session_state['planos_v2'] = None
if 'mostrar_siguiente' not in st.session_state:  # Añade esta línea
    st.session_state['mostrar_siguiente'] = False  # Inicializada como False

# Función para cambiar a la fase V2
def ir_a_v2():
    # Crear una lista que excluya la habitación "P5" del plano seleccionado
    idx = st.session_state.plano_seleccionado
    plano = st.session_state.planos_filtrados[idx]
    
    # Crear una nueva instancia de Casa para almacenar la combinación sin "P5"
    nueva_casa = Casa(largo=plano.largo, ancho=plano.ancho)
    
    # Agregar todas las habitaciones excepto la que corresponde a "P5"
    for habitacion in plano.habitaciones:
        if habitacion.nombre != "P5":
            nueva_casa.habitaciones.append(habitacion)
    
    # Copiar el área usada y otras variables necesarias
    nueva_casa.area_usada = sum(hab.area() for hab in nueva_casa.habitaciones)
    nueva_casa.posicion_x = plano.posicion_x
    nueva_casa.posicion_y = plano.posicion_y
    nueva_casa.altura_fila_actual = plano.altura_fila_actual

    # Guardar en el estado
    st.session_state['combinaciones_sin_p5'] = [nueva_casa]
    
    # Cambiar a la fase V2
    st.session_state['fase_actual'] = 'V2'
    st.session_state['planos_v2'] = None  # Reiniciar planos_v2 para regenerarlos

def mostrar_fase_v1():
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
            return (self.area_usada <= self.area_total and self.posicion_y + self.altura_fila_actual <= self.ancho)

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

    def seleccionar_plano(idx):
        st.session_state['plano_seleccionado'] = idx
        st.session_state['mostrar_siguiente'] = True


    # Botón para generar planos
    if st.button("Generar Planos V1") or st.session_state.planos_generados:
        if not st.session_state.planos_generados:
            with st.spinner("Generando planos, por favor espere..."):
                # Generar todas las combinaciones válidas
                combinaciones = generar_combinaciones(habitaciones_v1)
                planos_filtrados = [plano for plano in combinaciones if cumple_restricciones_espaciales(plano)]
                st.session_state.planos_filtrados = planos_filtrados
                st.session_state.planos_generados = True
    
    # Mostrar los planos en una figura con 4 subplots
        planos = st.session_state.planos_filtrados
    
    # Calcular número de columnas y filas
        num_cols = min(4, len(planos))
        num_filas = (len(planos) + num_cols - 1) // num_cols
    
    # Crear una figura para todos los planos
        fig, axs = plt.subplots(num_filas, num_cols, figsize=(20, 20))
    
    # Asegurar que axs sea un array iterable incluso con un solo plano
        axs = axs.flatten() if len(planos) > 1 else [axs]
    
    # Visualizar cada plano
        for i, casa in enumerate(planos):
            casa.visualizar_plano(axs[i])
            axs[i].set_title(f"Plano {i + 1}", fontsize=30)
    
    # Ocultar ejes vacíos
        for j in range(len(planos), len(axs)):
            axs[j].set_visible(False)
    
    # Mostrar la figura en Streamlit
        plt.tight_layout()
        st.pyplot(fig)
    
    # Columnas para los botones de selección
        cols = st.columns(num_cols)
        for i in range(len(planos)):
            col_idx = i % num_cols
            with cols[col_idx]:
                if st.button(f"Seleccionar Plano {i+1}", key=f"select_{i}"):
                    seleccionar_plano(i)
    
    # Mostrar mensaje de selección y botón de siguiente
        if st.session_state.mostrar_siguiente:
            idx = st.session_state.plano_seleccionado
            st.success(f"Has seleccionado el Plano {idx+1}")
        
            if st.button("Siguiente - Continuar a V2", type="primary"):
                ir_a_v2()
                st.experimental_rerun()  # Recargar la app con la nueva fase


def mostrar_fase_v2():
    # Generar planos V2 si no existen
    if st.session_state.planos_v2 is None:
        with st.spinner("Generando planos V2, por favor espere..."):
            # Actualizar las clasificaciones para V2
            # Crear una nueva lista que excluya la habitación "P5" solo de los planos seleccionados en planos_aleatorios
            combinaciones_sin_p5 = []
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
                
            CLASIFICACIONES_V2 = [
                {"nombre": "Baño", "ancho_min": 0.0, "ancho_max": 1.351, "largo_min": 0.0, "largo_max": 2.983},
                {"nombre": "Dor", "ancho_min": 3.5, "ancho_max": 3.6, "largo_min": 3.9, "largo_max": 4.0},
                {"nombre": "Cocina", "ancho_min": 2.5, "ancho_max": 2.6, "largo_min": 2.8, "largo_max": 2.9},
                {"nombre": "Comedor", "ancho_min": 2.2, "ancho_max": 2.4, "largo_min": 2.8, "largo_max": 2.9},
                {"nombre": "Estar", "ancho_min": 2.2, "ancho_max": 2.4, "largo_min": 2.4, "largo_max": 4.0},
                {"nombre": "Recibidor", "ancho_min": 2.2, "ancho_max": 4.9, "largo_min": 1.4, "largo_max": 1.6},]
            
            # Dimensiones para V2
            largo_casa_v2 = 2 * 2.440
            ancho_casa_v2 = 4 * 2.440
             # Actualizar restricciones espaciales para V2
            
            RESTRICCIONES_ESPACIALES_V2 = {
                ("Baño", "Dor"),
                ("Cocina", "Comedor"),
                ("Estar", "Recibidor"),
                ("Estar", "Comedor"),
            }
            
            class Casa:
                def __init__(self, largo, ancho, tipo=""):
                    self.largo = largo
                    self.ancho = ancho
                    self.habitaciones = []
                    self.tipo = tipo  

                def agregar_habitacion(self, habitacion):
                    self.habitaciones.append(habitacion)

                def visualizar_plano(self):
                    fig, ax = plt.subplots(figsize=(10, 8))
                    for hab in self.habitaciones:
                        poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
                        ax.add_patch(poligono)
                        cx = sum([v[0] for v in hab.vertices]) / len(hab.vertices)
                        cy = sum([v[1] for v in hab.vertices]) / len(hab.vertices)

                        nombre_funcional = obtener_nombre_funcional_por_rango(hab.ancho, hab.altura)
                        ax.text(cx, cy, f"{hab.nombre}\n{nombre_funcional}", ha='center', va='center', fontsize=8)

                    ax.set_xlim(0, self.largo)
                    ax.set_ylim(0, self.ancho)
                    plt.title(f"Plano {self.tipo}", fontsize=14)
                    plt.gca().set_aspect('equal', adjustable='box')
                    plt.show()

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

            # Calcular el número total de planos (originales + reflejados)
            num_planos_total = len(planos_seleccionados) * 2  # Cada plano tiene un original y un reflejado

            # Calcular un layout adecuado para los subplots
            num_cols = min(2, num_planos_total)  # Máximo 2 columnas
            num_filas = (num_planos_total + num_cols - 1) // num_cols  # Redondeo hacia arriba

            # Crear una única figura con subplots para todos los planos
            fig, axs = plt.subplots(1,4, figsize=(40, 40))
            axs = axs.flatten() if num_planos_total > 1 else [axs]  # Convertir a array 1D

            # Iterar sobre los planos y sus reflexiones
            for i, plano in enumerate(planos_seleccionados):
                # Índice para el plano original
                idx_original = i * 2
    
                # Recopilar y clasificar habitaciones para el plano original
                dormitorios = []
                baños = []
                otras_habitaciones = []
    
                for hab in plano.habitaciones:
                    cx = sum([v[0] for v in hab.vertices]) / len(hab.vertices)
                    cy = sum([v[1] for v in hab.vertices]) / len(hab.vertices)
                    nombre_funcional = obtener_nombre_funcional_por_rango(hab.ancho, hab.altura)
        
                    if nombre_funcional == "Dor":
                        dormitorios.append((hab, cx, cy))
                    elif nombre_funcional == "Baño":
                        baños.append((hab, cx, cy))
                    else:
                        otras_habitaciones.append((hab, cx, cy, nombre_funcional))
    
                # Ordenar dormitorios de abajo hacia arriba, luego de izquierda a derecha
                dormitorios.sort(key=lambda x: (x[2], x[1]))  # y para orden ascendente (abajo hacia arriba)
    
                # Ordenar baños de abajo hacia arriba, luego de izquierda a derecha
                baños.sort(key=lambda x: (x[2], x[1]))
    
                # Dibujar dormitorios numerados
                for idx, (hab, cx, cy) in enumerate(dormitorios, 1):
                    poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
                    axs[idx_original].add_patch(poligono)
                    axs[idx_original].text(cx, cy, f"{hab.nombre}\nDor {idx}", ha='center', va='center', fontsize=30)
    
                # Dibujar baños numerados
                for idx, (hab, cx, cy) in enumerate(baños, 1):
                    poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
                    axs[idx_original].add_patch(poligono)
                    axs[idx_original].text(cx, cy, f"{hab.nombre}\nBaño {idx}", ha='center', va='center', fontsize=30)
    
                # Dibujar otras habitaciones
                for hab, cx, cy, nombre_funcional in otras_habitaciones:
                    poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
                    axs[idx_original].add_patch(poligono)
                    axs[idx_original].text(cx, cy, f"{hab.nombre}\n{nombre_funcional}", ha='center', va='center', fontsize=30)
    
                axs[idx_original].set_xlim(0, plano.largo)
                axs[idx_original].set_ylim(0, plano.ancho)
                axs[idx_original].set_title(f"Plano {2*i + 1}", fontsize=40)
                axs[idx_original].set_aspect('equal', adjustable='box')
    
                # Índice para el plano reflejado
                idx_reflejado = i * 2 + 1
    
                # Crear el plano reflejado
                plano_reflejado = reflejar_plano(plano)
    
                # Recopilar y clasificar habitaciones para el plano reflejado
                dormitorios_ref = []
                baños_ref = []
                otras_habitaciones_ref = []
    
                for hab in plano_reflejado.habitaciones:
                    cx = sum([v[0] for v in hab.vertices]) / len(hab.vertices)
                    cy = sum([v[1] for v in hab.vertices]) / len(hab.vertices)
                    nombre_funcional = obtener_nombre_funcional_por_rango(hab.ancho, hab.altura)
        
                    if nombre_funcional == "Dor":
                        dormitorios_ref.append((hab, cx, cy))
                    elif nombre_funcional == "Baño":
                        baños_ref.append((hab, cx, cy))
                    else:
                        otras_habitaciones_ref.append((hab, cx, cy, nombre_funcional))
    
    # Ordenar dormitorios reflejados de abajo hacia arriba, luego de izquierda a derecha
                dormitorios_ref.sort(key=lambda x: (x[2], x[1]))
    
    # Ordenar baños reflejados de abajo hacia arriba, luego de izquierda a derecha
                baños_ref.sort(key=lambda x: (x[2], x[1]))
    
    # Dibujar dormitorios numerados
                for idx, (hab, cx, cy) in enumerate(dormitorios_ref, 1):
                    poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
                    axs[idx_reflejado].add_patch(poligono)
                    axs[idx_reflejado].text(cx, cy, f"{hab.nombre}\nDor {idx}", ha='center', va='center', fontsize=30)
    
    # Dibujar baños numerados
                for idx, (hab, cx, cy) in enumerate(baños_ref, 1):
                    poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
                    axs[idx_reflejado].add_patch(poligono)
                    axs[idx_reflejado].text(cx, cy, f"{hab.nombre}\nBaño {idx}", ha='center', va='center', fontsize=30)
    
    # Dibujar otras habitaciones
                for hab, cx, cy, nombre_funcional in otras_habitaciones_ref:
                    poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
                    axs[idx_reflejado].add_patch(poligono)
                    axs[idx_reflejado].text(cx, cy, f"{hab.nombre}\n{nombre_funcional}", ha='center', va='center', fontsize=30)
    
                axs[idx_reflejado].set_xlim(0, plano_reflejado.largo)
                axs[idx_reflejado].set_ylim(0, plano_reflejado.ancho)
                axs[idx_reflejado].set_title(f"Plano {2*i + 2}", fontsize=40)
                axs[idx_reflejado].set_aspect('equal', adjustable='box')

            # Ocultar ejes vacíos si hay más subplots que planos
            for j in range(num_planos_total, len(axs)):
                axs[j].set_visible(False)

            # Ajustar la distribución de los subplots
            plt.tight_layout()
            st.pysplot(fig)

           # Botones de selección para planos V2
            cols = st.columns(min(4, len(planos_v2)))
            for i in range(len(planos_v2)):
                col_idx = i % len(cols)
                with cols[col_idx]:
                    if st.button(f"Seleccionar Plano {i+1}", key=f"select_v2_{i}"):
                        st.session_state['plano_v2_seleccionado'] = i
                        st.success(f"Has seleccionado el Plano {i+1}")
    
            # Mostrar botón para continuar a V3 si se ha seleccionado un plano
            if 'plano_v2_seleccionado' in st.session_state and st.session_state.plano_v2_seleccionado is not None:
                if st.button("Continuar a V3", type="primary"):
                    # Aquí pondrías la lógica para pasar a V3
                    st.session_state['fase_actual'] = 'V3'
                    st.experimental_rerun()
            
# Estructura condicional para mostrar contenido según la fase
if st.session_state.fase_actual == 'V1':
    # Código de la fase V1
    mostrar_fase_v1()
elif st.session_state.fase_actual == 'V2':
    # Código de la fase V2
    mostrar_fase_v2()
    
