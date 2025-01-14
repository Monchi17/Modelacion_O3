import streamlit as st
from itertools import permutations
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import random


# Título de la aplicación
st.title("Generador de Planos para Casas")

# Opciones predefinidas para las dimensiones de la casa
opciones = {
    "Ancho 2440*2, Largo 2440*3": (2.440 * 2, 2.440 * 3),
    "Ancho 2440*2, Largo 2440*4": (2.440 * 2, 2.440 * 4),
    "Ancho 2440*2, Largo 2440*6": (2.440 * 2, 2.440 * 6),
    "Ancho 2440*3, Largo 2440*6": (2.440 * 3, 2.440 * 6),
    "Ancho 2440*4, Largo 2440*6": (2.440 * 4, 2.440 * 6),
}

# Input para seleccionar la opción
opcion_seleccionada = st.selectbox(
    "Seleccione las dimensiones de la casa:",
    opciones.keys()
)

# Asignar las dimensiones según la selección
largo_casa, ancho_casa = opciones[opcion_seleccionada]


#st.write(f"Area del plano {largo_casa * ancho_casa} M^2")
#-----------------------------------V1------------------------------------
if largo_casa == 2.440*2 and ancho_casa == 2.440*3:
    # Clase Habitacion
    class Habitacion:
        def __init__(self, nombre, vertices):
            self.nombre = nombre
            self.vertices = vertices
            self.altura = max(y for x, y in vertices)
            self.ancho = max(x for x, y in vertices)
    
        def area(self):
            x, y = zip(*self.vertices)
            return 0.5 * abs(sum(x[i] * y[i+1] - x[i+1] * y[i] for i in range(-1, len(x)-1)))
    
    
    # Clase Casa
    class Casa:
        def __init__(self, largo, ancho):
            self.largo = largo
            self.ancho = ancho
            self.area_total = largo * ancho
            self.habitaciones = []
            self.area_usada = 0
            self.posicion_x = 0
            self.posicion_y = 0
            self.altura_fila_actual = 0  # Nueva variable para la altura de la fila actual
    
        def agregar_habitacion(self, habitacion):
            if self.area_usada + habitacion.area() <= self.area_total:
                # Verifica si la habitación cabe en el ancho disponible de la fila
                if self.posicion_x + habitacion.ancho > self.largo:
                    # Cambiar a una nueva fila si la habitación no cabe
                    self.posicion_x = 0
                    self.posicion_y += self.altura_fila_actual
                    self.altura_fila_actual = 0  # Restablecer la altura de la fila
    
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
                self.posicion_y += self.altura_fila_actual  # Mueve y a la siguiente fila para la habitación final
    
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
            return self.area_usada <= self.area_total and self.posicion_y + self.altura_fila_actual <= self.ancho
    
        def visualizar_plano(self):
            fig, ax = plt.subplots(dpi=30)
            
            for hab in self.habitaciones:
                poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
                ax.add_patch(poligono)
                cx = sum([v[0] for v in hab.vertices]) / len(hab.vertices)
                cy = sum([v[1] for v in hab.vertices]) / len(hab.vertices)
                ax.text(cx, cy, hab.nombre, ha='center', va='center')
    
            ax.set_xlim(0, self.largo)
            ax.set_ylim(0, self.ancho)
            plt.gca().set_aspect('equal', adjustable='box')
            st.pyplot(fig)
    
    
    # Definir habitaciones
    habitaciones_v1 = [
        Habitacion("P1", [(0, 0), (3.529, 0), (3.529, 2.983), (0, 2.983)]),
        Habitacion("P2", [(0, 0), (1.351, 0), (1.351, 2.983), (0, 2.983)]),
        Habitacion("P3", [(0, 0), (2.585, 0), (2.585, 2.856), (0, 2.856)]),
        Habitacion("P4", [(0, 0), (2.295, 0), (2.295, 2.856), (0, 2.856)]),
    ]
    
    habitaciones_finales = [
        Habitacion("P8", [(0, 0), (2.295, 0), (2.295, 1.487), (0, 1.487)]),
        Habitacion("P11", [(0, 0), (2.295, 0), (2.295, 1.588), (0, 1.588)]),
        Habitacion("P5", [(0, 0), (4.880, 0), (4.880, 1.481), (0, 1.481)]),
    ]
    
    
    # Generar combinaciones
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
    
    
    combinaciones = generar_combinaciones(habitaciones_v1)
    
    planos_aleatorios = random.sample(combinaciones, min(3, len(combinaciones)))  # Seleccionar 3 planos al azar
    
    # Mostrar los planos seleccionados

    cols = st.columns(3)  # 2 gráficos por fila

    for i, casa in enumerate(planos_aleatorios):
        with cols[i % 3]:  # Alternar entre las columnas
            st.write(f"Plano {i + 1}")
            casa.visualizar_plano()
#-----------------------------------------------------v2---------------------------------------------------
elif largo_casa == 2.440*2 and ancho_casa == 2.440*4:
    
    largo_casa = 2.440 * 2
    ancho_casa = 2.440 * 3
    class Habitacion:
            def __init__(self, nombre, vertices):
                self.nombre = nombre
                self.vertices = vertices
                self.altura = max(y for x, y in vertices)
                self.ancho = max(x for x, y in vertices)
    
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
                self.altura_fila_actual = 0  # Nueva variable para la altura de la fila actual
    
            def agregar_habitacion(self, habitacion):
                if self.area_usada + habitacion.area() <= self.area_total:
                    # Verifica si la habitación cabe en el ancho disponible de la fila
                    if self.posicion_x + habitacion.ancho > self.largo:
                        # Cambiar a una nueva fila si la habitación no cabe
                        self.posicion_x = 0
                        self.posicion_y += self.altura_fila_actual
                        self.altura_fila_actual = 0  # Restablecer la altura de la fila
    
                    # Desplazar los vértices de la habitación actual
                    vertices_desplazados = [(x + self.posicion_x, y + self.posicion_y) for x, y in habitacion.vertices]
                    habitacion_desplazada = Habitacion(habitacion.nombre, vertices_desplazados)
                    self.habitaciones.append(habitacion_desplazada)
                    self.area_usada += habitacion.area()
    
                    # Actualiza la posición y la altura de la fila actual
                    self.posicion_x += habitacion.ancho
                    self.altura_fila_actual = max(self.altura_fila_actual, habitacion.altura)
    
                    # Verificación temprana para detener si se excede el ancho o alto de la casa
                    if self.posicion_y + self.altura_fila_actual > self.ancho:
                        return False
                    return True
                return False
    
            def agregar_habitacion_inferior(self, habitacion_final):
                # Coloca la habitación en la última fila (parte inferior del plano)
                if self.posicion_y + self.altura_fila_actual + habitacion_final.altura <= self.ancho:
                    self.posicion_x = 0
                    self.posicion_y += self.altura_fila_actual  # Mueve y a la siguiente fila para la habitación final
    
                    vertices_desplazados = [(x + self.posicion_x, y + self.posicion_y) for x, y in habitacion_final.vertices]
                    habitacion_desplazada = Habitacion(habitacion_final.nombre, vertices_desplazados)
                    self.habitaciones.append(habitacion_desplazada)
                    self.area_usada += habitacion_final.area()
    
                    # Ajusta posicion_x y altura_fila_actual para verificar al final
                    self.posicion_x += habitacion_final.ancho
                    self.altura_fila_actual = habitacion_final.altura
                    return True
                return False
    
            def cumple_dimensiones_exactas(self):
                # Verifica que el último plano cubre todo el ancho y alto de la casa
                return self.posicion_x == self.largo and self.posicion_y + self.altura_fila_actual == self.ancho
    
            def es_valida(self):
                # Verifica que la disposición cumple con las dimensiones de la casa
                return (self.area_usada <= self.area_total and 
                        self.posicion_y + self.altura_fila_actual <= self.ancho)
    
            def visualizar_plano(self):
                fig, ax = plt.subplots()
                for hab in self.habitaciones:
                    poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
                    ax.add_patch(poligono)
                    cx = sum([v[0] for v in hab.vertices]) / len(hab.vertices)
                    cy = sum([v[1] for v in hab.vertices]) / len(hab.vertices)
                    ax.text(cx, cy, hab.nombre, ha='center', va='center')
                
                ax.set_xlim(0, self.largo)
                ax.set_ylim(0, self.ancho)
                plt.gca().set_aspect('equal', adjustable='box')
                st.pyplot(fig)
    
    
        # Lista de habitaciones estándar (excluyendo P5, P8 y P11)
    habitaciones_v1 = [
        Habitacion("P1", [(0, 0), (3.529, 0), (3.529, 2.983), (0, 2.983)]),
        Habitacion("P2", [(0, 0), (1.351, 0), (1.351, 2.983), (0, 2.983)]),
        Habitacion("P3", [(0, 0), (2.585, 0), (2.585, 2.856), (0, 2.856)]),
        Habitacion("P4", [(0, 0), (2.295, 0), (2.295, 2.856), (0, 2.856)]),]
    
    habitaciones_finales = [
        Habitacion("P8", [(0, 0), (2.295, 0), (2.295, 1.487), (0, 1.487)]),
        Habitacion("P11", [(0, 0), (2.295, 0), (2.295, 1.588), (0, 1.588)]),
        Habitacion("P5", [(0, 0), (4.880, 0), (4.880, 1.481), (0, 1.481)])]
    
    
    # Generar combinaciones válidas con una sola habitación final por plano
    def generar_combinaciones(habitaciones):
        combinaciones_validas = []
        for habitacion_final in habitaciones_finales:
            # Generar permutaciones de la lista de habitaciones
            for permutacion in permutations(habitaciones):
                casa = Casa(largo=largo_casa, ancho=ancho_casa)
                
                # Colocar las habitaciones estándar primero
                es_valido = True
                for habitacion in permutacion:
                    if not casa.agregar_habitacion(habitacion):
                        es_valido = False
                        break
                
                # Colocar la habitación inferior al final si es válida
                if es_valido and casa.es_valida() and casa.agregar_habitacion_inferior(habitacion_final):
                    # Verificar que el plano cumple con los requisitos exactos de ancho y alto
                    if casa.cumple_dimensiones_exactas():
                        combinaciones_validas.append(casa)
        return combinaciones_validas


    # Generar todas las combinaciones válidas
    combinaciones = generar_combinaciones(habitaciones_v1)

    # Crear una nueva lista que excluya la habitación "P5" de cada combinación existente
    combinaciones_sin_p5 = []

    for casa in combinaciones:
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
    cols = st.columns(3)
    for i in range(2): #Da 3 combinaciones
        class Habitacion:
            def __init__(self, nombre, vertices):
                self.nombre = nombre
                self.vertices = vertices

            def area(self):
                x, y = zip(*self.vertices)
                return 0.5 * abs(sum(x[i] * y[i+1] - x[i+1] * y[i] for i in range(-1, len(x)-1)))

        class Casa:
            def __init__(self, largo, ancho):
                self.largo = largo
                self.ancho = ancho
                self.habitaciones = []

            def agregar_habitacion(self, habitacion):
                self.habitaciones.append(habitacion)

            def visualizar_plano(self):
                fig, ax = plt.subplots()
                for hab in self.habitaciones:
                    poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
                    ax.add_patch(poligono)
                    cx = sum([v[0] for v in hab.vertices]) / len(hab.vertices)
                    cy = sum([v[1] for v in hab.vertices]) / len(hab.vertices)
                    ax.text(cx, cy, hab.nombre, ha='center', va='center')

                ax.set_xlim(0, self.largo)
                ax.set_ylim(0, self.ancho)
                plt.gca().set_aspect('equal', adjustable='box')
                st.pyplot(fig)

        # Dimensiones de la casa
        largo_casa = 2*2.440
        ancho_casa = 4*2.440 #9.759

        # Crear las dos combinaciones de planos
        # Plano 1: P8 en esquina superior derecha, P7 y P6 en la primera configuración
        casa1 = Casa(largo_casa, ancho_casa)
        casa1.agregar_habitacion(Habitacion("P7", [(0, 5.850), (2.585, 5.850), (2.585, 9.765), (0, 9.765)])),
        casa1.agregar_habitacion(Habitacion("P6", [(2.585, 5.850), (4.880, 5.850), (4.880, 8.280), (2.585, 8.280)]))
        casa1.agregar_habitacion(Habitacion("P8", [(2.585, 8.290), (4.880, 8.290), (4.880, 9.765), (2.585, 9.765)]))

        # Plano 2: P8 en esquina superior izquierda, P7 y P6 en la segunda configuración
        casa2 = Casa(largo_casa, ancho_casa)
        casa2.agregar_habitacion(Habitacion("P7", [(2.295, 5.839), (4.880, 5.839), (4.880, 9.759), (2.295, 9.759)]))
        casa2.agregar_habitacion(Habitacion("P6", [(0, 5.839), (2.295, 5.839), (2.295, 8.272), (0, 8.272)]))
        casa2.agregar_habitacion(Habitacion("P8", [(0, 8.272), (2.295, 8.272), (2.295, 9.759), (0, 9.759)]))

        # Visualizar los dos planos
        casa1.habitaciones.extend(combinaciones_sin_p5[i].habitaciones)
        #casa1.visualizar_plano()

        casa2.habitaciones.extend(combinaciones_sin_p5[i].habitaciones)
        #casa2.visualizar_plano()

           # Lista de planos
        planos = [casa1, casa2]
    
        # Visualizar los planos en las columnas
        for j, plano in enumerate(planos):
            col = cols[j % 3]  # Seleccionar la columna correspondiente
            with col:
                st.write(f"Plano {i * 2 + j + 1}")  # Título del plano
                
                # Crear la figura y visualizar el plano
                fig, ax = plt.subplots()
                for hab in plano.habitaciones:
                    poligono = Polygon(hab.vertices, closed=True, fill=True, edgecolor='black', alpha=0.5)
                    ax.add_patch(poligono)
                    cx = sum([v[0] for v in hab.vertices]) / len(hab.vertices)
                    cy = sum([v[1] for v in hab.vertices]) / len(hab.vertices)
                    ax.text(cx, cy, hab.nombre, ha='center', va='center')
    
                ax.set_xlim(0, plano.largo)
                ax.set_ylim(0, plano.ancho)
                ax.set_aspect('equal', adjustable='box')
    
                # Pasar explícitamente la figura a st.pyplot()
                st.pyplot(fig)

#------------------------V3--------------------

elif largo_casa == 2.440*2 and ancho_casa == 2.440*6:

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
        st.pyplot(fig)

    # Habitaciones opcionales y finales
    habitaciones_opcionales_sin_P8_P11 = [
        Habitacion("P6", [(0, 0), (2.295, 0), (2.295, 2.433), (0, 2.433)]),
        Habitacion("P7", [(0, 0), (2.585, 0), (2.585, 3.921), (0, 3.921)]),
        Habitacion("P9", [(0, 0), (2.295, 0), (2.295, 4.779), (0, 4.779)]),
        Habitacion("P10", [(0, 0), (2.585, 0), (2.585, 4.880), (0, 4.880)])
    ]
    habitaciones_finales = [
        Habitacion("P8", [(0, 0), (2.295, 0), (2.295, 1.488), (0, 1.488)]),
        Habitacion("P11", [(0, 0), (2.295, 0), (2.295, 1.588), (0, 1.588)]),
        Habitacion("P5", [(0, 0), (4.880, 0), (4.880, 1.480), (0, 1.480)]),
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
    contador_combinaciones = 0
    
    for combinacion in combinaciones_sin_P8_P11:  # Primer ciclo: todas las combinaciones de habitaciones opcionales
        for final in habitaciones_finales:  # Segundo ciclo: agrega P8 o P11 a cada combinación
            contador_combinaciones += 1
            combinacion_completa = list(combinacion) + [final]
            habitaciones_colocadas_opcionales, _ = colocar_habitaciones(
                combinacion_completa, largo_casa, ancho_casa, espacios_actualizados[:]
            )
            plano = habitaciones_colocadas_fijas + habitaciones_colocadas_opcionales
    
            # Filtrar planos con exactamente 9 habitaciones
            if len(plano) != 9:
                continue
    
            plano_tupla = tuple((h.nombre, tuple(h.vertices)) for h in plano)
            if plano_tupla not in planos_unicos:
                planos_unicos.add(plano_tupla)
                planos_guardados.append(plano)
    
    planos_generados = planos_guardados
    
    # Seleccionar tres planos al azar de los generados
    if len(planos_guardados) >= 3:
        planos_seleccionados = random.sample(planos_guardados, 3)
    else:
        st.warning("Menos de tres planos generados. Mostrando todos los disponibles.")
        planos_seleccionados = planos_guardados
    
    # Crear tres columnas en Streamlit
    cols = st.columns(3)
    
    # Plotear los tres planos seleccionados
    for i, plano in enumerate(planos_seleccionados):
        with cols[i]:  # Alternar entre las columnas
            st.write(f"Plano {i + 1}")  # Título del plano
    
            # Crear la figura y graficar
            fig, ax = plt.subplots()
            for habitacion in plano:
                polygon = Polygon(habitacion.vertices, closed=True, edgecolor='black', alpha=0.5)
                ax.add_patch(polygon)
                x_coords = [v[0] for v in habitacion.vertices]
                y_coords = [v[1] for v in habitacion.vertices]
                ax.text(
                    sum(x_coords) / len(x_coords),
                    sum(y_coords) / len(y_coords),
                    habitacion.nombre, ha="center", va="center", color="black"
                )
            ax.set_xlim(-largo_casa, largo_casa)  # Ajustado para doble ancho (izquierda + derecha)
            ax.set_ylim(0, ancho_casa)
            ax.set_aspect("equal")
            plt.title(f"Plano {i + 1}")
            st.pyplot(fig)


#------------------------V4--------------------------

elif largo_casa == 2.440*3 and ancho_casa == 2.440*6:
    # Dimensiones de la casa
    largo_casa = 2.440 * 2
    ancho_casa = 2.440 * 6

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
        st.pyplot(fig)

    # Habitaciones opcionales y finales
    habitaciones_opcionales_sin_P8_P11 = [
        Habitacion("P6", [(0, 0), (2.295, 0), (2.295, 2.433), (0, 2.433)]),
        Habitacion("P7", [(0, 0), (2.585, 0), (2.585, 3.921), (0, 3.921)]),
        Habitacion("P9", [(0, 0), (2.295, 0), (2.295, 4.779), (0, 4.779)]),
        Habitacion("P10", [(0, 0), (2.585, 0), (2.585, 4.880), (0, 4.880)])
    ]
    habitaciones_finales = [
        Habitacion("P8", [(0, 0), (2.295, 0), (2.295, 1.488), (0, 1.488)]),
        Habitacion("P11", [(0, 0), (2.295, 0), (2.295, 1.588), (0, 1.588)]),
        Habitacion("P5", [(0, 0), (4.880, 0), (4.880, 1.480), (0, 1.480)]),
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
                numero_plano += 1


    planos_generados = planos_guardados

    largo_casa=2.440*3
    ancho_casa=2.440*6
    # Función para guardar y plotear habitaciones
    # Función para guardar y plotear habitaciones
    def guardar_y_plotear_habitaciones(habitaciones, largo_casa, ancho_casa, numero_plano):
        # Crear el gráfico del plano
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
        ax.set_xlim(-largo_casa, largo_casa)  # Ajustado para doble ancho (izquierda + derecha)
        ax.set_ylim(0, ancho_casa)
        ax.set_aspect("equal")
        plt.title(f"Plano {numero_plano}")
        return fig
    
    # Dimensiones de la casa
    largo_casa = 2.440 * 3
    ancho_casa = 2.440 * 6
    
    # Habitaciones a la izquierda
    habitaciones_izquierda = [
        Habitacion("P14", [(0, 0), (2.440, 0), (2.440, 4.211), (0, 4.211)]),
        Habitacion("P15", [(0, 0), (2.440, 0), (2.440, 4.007), (0, 4.007)]),
        Habitacion("P16", [(0, 0), (2.440, 0), (2.440, 4.194), (0, 4.194)]),
        Habitacion("P17", [(0, 0), (2.440, 0), (2.440, 2.228), (0, 2.228)])
    ]
    
    # Seleccionar un plano al azar (simulado aquí con un ejemplo)
    plano_aleatorio = random.choice(planos_generados)
    
    # Lista para guardar todos los planos generados
    planos_guardados = []
    
    # Generar combinaciones para las habitaciones a la izquierda
    combinaciones_izquierda = permutations(habitaciones_izquierda)
    
    # Probar todas las combinaciones de habitaciones a la izquierda
    numero_plano = 1
    for combinacion in combinaciones_izquierda:
        # Ajustar la colocación en una sola columna
        espacios_restantes_izquierda = [(-2.440, 0, 2.440, ancho_casa)]  # Solo una columna de ancho 2.440
        habitaciones_colocadas_izquierda = []
        y_offset = 0  # Para apilar las habitaciones verticalmente
    
        for habitacion in combinacion:
            # Ajustar los vértices para la columna izquierda
            vertices_desplazados = [(-2.440 + x, y + y_offset) for x, y in habitacion.vertices]
            habitaciones_colocadas_izquierda.append(Habitacion(habitacion.nombre, vertices_desplazados))
            y_offset += habitacion.largo  # Incrementar el desplazamiento vertical
    
        # Verificar que no exceda el alto de la casa
        if y_offset > ancho_casa:
            continue
    
        # Crear el nuevo plano combinando las habitaciones a la izquierda y el plano aleatorio
        nuevo_plano = habitaciones_colocadas_izquierda + plano_aleatorio
    
        # Guardar el nuevo plano
        planos_guardados.append(nuevo_plano)
        numero_plano += 1
    
    # Seleccionar y plotear 3 planos guardados al azar
    planos_seleccionados = random.sample(planos_guardados, min(3, len(planos_guardados)))  # Selecciona hasta 3 planos si hay suficientes
    
    # Usar Streamlit para mostrar los planos
    st.title("Planos Seleccionados")
    
    cols = st.columns(3)  # Crear tres columnas
    for i, plano in enumerate(planos_seleccionados):
        with cols[i]:
            st.write(f"Plano {i + 1}")
            fig = guardar_y_plotear_habitaciones(plano, largo_casa, ancho_casa, f"Seleccionado {i + 1}")
            st.pyplot(fig)



#-------------------------V5------------------
elif largo_casa == 2.440*4 and ancho_casa == 2.440*6:

    # Dimensiones de la casa
    largo_casa = 2.440 * 2
    ancho_casa = 2.440 * 6

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
        st.pyplot(fig)

    # Habitaciones opcionales y finales
    habitaciones_opcionales_sin_P8_P11 = [
        Habitacion("P6", [(0, 0), (2.295, 0), (2.295, 2.433), (0, 2.433)]),
        Habitacion("P7", [(0, 0), (2.585, 0), (2.585, 3.921), (0, 3.921)]),
        Habitacion("P9", [(0, 0), (2.295, 0), (2.295, 4.779), (0, 4.779)]),
        Habitacion("P10", [(0, 0), (2.585, 0), (2.585, 4.880), (0, 4.880)])
    ]
    habitaciones_finales = [
        Habitacion("P8", [(0, 0), (2.295, 0), (2.295, 1.488), (0, 1.488)]),
        Habitacion("P11", [(0, 0), (2.295, 0), (2.295, 1.588), (0, 1.588)]),
        Habitacion("P5", [(0, 0), (4.880, 0), (4.880, 1.480), (0, 1.480)]),
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
                numero_plano += 1


    planos_generados = planos_guardados

    largo_casa=2.440*3
    ancho_casa=2.440*6

        # Función para guardar y plotear habitaciones
    def guardar_y_plotear_habitaciones(habitaciones, largo_casa, ancho_casa, numero_plano, planos_guardados):
        # Guardar el plano actual
        planos_guardados.append(habitaciones)

    

    # Habitaciones a la izquierda
    habitaciones_izquierda = [
        Habitacion("P14", [(0, 0), (2.440, 0), (2.440, 4.211), (0, 4.211)]),
        Habitacion("P15", [(0, 0), (2.440, 0), (2.440, 4.007), (0, 4.007)]),
        Habitacion("P16", [(0, 0), (2.440, 0), (2.440, 4.194), (0, 4.194)]),
        Habitacion("P17", [(0, 0), (2.440, 0), (2.440, 2.228), (0, 2.228)])
    ]

    # Seleccionar un plano al azar
    plano_aleatorio = random.choice(planos_generados)

    # Lista para guardar todos los planos generados
    planos_guardados = []

    # Generar combinaciones para las habitaciones a la izquierda
    combinaciones_izquierda = permutations(habitaciones_izquierda)

    # Probar todas las combinaciones de habitaciones a la izquierda
    numero_plano = 1
    for combinacion in combinaciones_izquierda:
        # Ajustar la colocación en una sola columna
        espacios_restantes_izquierda = [(-2.440, 0, 2.440, ancho_casa)]  # Solo una columna de ancho 2.440
        habitaciones_colocadas_izquierda = []
        y_offset = 0  # Para apilar las habitaciones verticalmente

        for habitacion in combinacion:
            # Ajustar los vértices para la columna izquierda
            vertices_desplazados = [(-2.440 + x, y + y_offset) for x, y in habitacion.vertices]
            habitaciones_colocadas_izquierda.append(Habitacion(habitacion.nombre, vertices_desplazados))
            y_offset += habitacion.largo  # Incrementar el desplazamiento vertical

        # Verificar que no exceda el alto de la casa
        if y_offset > ancho_casa:
            print(f"Combinación {numero_plano} excede el alto de la casa. Se omite.")
            continue
        
        # Crear el nuevo plano combinando las habitaciones a la izquierda y el plano aleatorio
        nuevo_plano = habitaciones_colocadas_izquierda + plano_aleatorio
        
        # Guardar y plotear el nuevo plano
        guardar_y_plotear_habitaciones(nuevo_plano, largo_casa, ancho_casa, numero_plano, planos_guardados)
        numero_plano += 1

        # Habitaciones a la izquierda (nuevas)
    habitaciones_izquierda_2 = [
        Habitacion("P18", [(0, 0), (2.440, 0), (2.440, 4.211), (0, 4.211)]),
        Habitacion("P19", [(0, 0), (2.440, 0), (2.440, 1.428), (0, 1.428)]),
        Habitacion("P20", [(0, 0), (2.440, 0), (2.440, 9.001), (0, 9.001)]),
    ]

    # Seleccionar un plano generado al azar
    plano_aleatorio_derecha = random.choice(planos_guardados)

    # Generar combinaciones para las habitaciones a la izquierda
    combinaciones_izquierda_2 = permutations(habitaciones_izquierda_2)

    nuevos_planos=[]
    # Probar todas las combinaciones de habitaciones a la izquierda con el plano seleccionado a la derecha
    numero_plano = 1
    for combinacion in combinaciones_izquierda_2:
        # Ajustar la colocación en una sola columna
        espacios_restantes_izquierda = [(-2.440, 0, 2.440, ancho_casa)]  # Solo una columna de ancho 2.440
        habitaciones_colocadas_izquierda = []
        y_offset = 0  # Para apilar las habitaciones verticalmente

        for habitacion in combinacion:  # Iteramos directamente sobre los objetos Habitacion
            # Ajustar los vértices para la columna izquierda
            vertices_desplazados = [(-2.440*2 + x, y + y_offset) for x, y in habitacion.vertices]
            habitaciones_colocadas_izquierda.append(Habitacion(habitacion.nombre, vertices_desplazados))
            y_offset += habitacion.largo  # Incrementar el desplazamiento vertical basado en la altura de la habitación

        #Verificar que no exceda el alto de la casa
        if y_offset > ancho_casa:
            print(f"Combinación {numero_plano} excede el alto de la casa. Se omite.")
            continue
        
        #Crear el nuevo plano combinando las habitaciones a la izquierda y el plano aleatorio a la derecha
        nuevo_plano = habitaciones_colocadas_izquierda + plano_aleatorio_derecha
        nuevos_planos.append(nuevo_plano)
        numero_plano += 1

    # Seleccionar 3 planos al azar de los nuevos planos generados
    planos_a_plotear = random.sample(nuevos_planos, min(3, len(nuevos_planos)))

    # Plotear los 3 planos seleccionados
    for i, plano in enumerate(planos_a_plotear):
        plotear_habitaciones(plano, largo_casa, ancho_casa, i + 1)



