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
    st.write("Planos generados:")
    for i, casa in enumerate(planos_aleatorios):
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
                plt.show()
    
    
        # Lista de habitaciones estándar (excluyendo P5, P8 y P11)
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
    
        for i in range(3): #Da 3 combinaciones
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
                    plt.show()
    
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
            casa1.visualizar_plano()
    
            casa2.habitaciones.extend(combinaciones_sin_p5[i].habitaciones)
            casa2.visualizar_plano()
