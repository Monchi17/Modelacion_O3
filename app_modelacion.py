import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import json
import numpy as np
import os

st.set_page_config(page_title="Visualizador de Planos", layout="wide")
st.title("Visualizador de Planos")

# Ruta al archivo Excel
EXCEL_PATH = "planos_ploteo.xlsx"

def cargar_datos_excel():
    """Carga los datos directamente desde el archivo planos_ploteo.xlsx"""
    if os.path.exists(EXCEL_PATH):
        try:
            return pd.read_excel(EXCEL_PATH)
        except Exception as e:
            st.error(f"Error al leer el archivo {EXCEL_PATH}: {e}")
            return None
    else:
        st.error(f"No se encontró el archivo {EXCEL_PATH}. Asegúrate de que esté en el mismo directorio que la aplicación.")
        return None

def get_safe(data, key, default="N/A"):
    try:
        if key in data and pd.notna(data[key]):
            return f"{data[key]:.2f} m"
        return default
    except:
        return default

def visualizar_plano(datos_plano, titulo, version):
    """
    Visualiza un plano a partir de sus datos, con dimensiones específicas según la versión
    """
    try:
        # Establecer dimensiones según la versión
        if version == "v1":
            largo_casa = 2.440 * 2
            ancho_casa = 2.440 * 3
        elif version == "v2":
            largo_casa = 2 * 2.440
            ancho_casa = 4 * 2.440
        elif version == "v3":
            largo_casa = 2.440 * 2
            ancho_casa = 2.440 * 6
        elif version == "v4":
            largo_casa = 2.440 * 3
            ancho_casa = 2.440 * 6
        elif version == "v5":
            largo_casa = 2.440 * 4
            ancho_casa = 2.440 * 6
        else:
            # Si no coincide con ninguna versión conocida, usar valores del Excel o valores por defecto
            ancho_casa = datos_plano.get('Ancho_Casa', datos_plano.get('ancho_casa', 7.32))
            largo_casa = datos_plano.get('Largo_Casa', datos_plano.get('largo_casa', 4.88))
        
        # Extraer información de habitaciones (como JSON)
        habitaciones_json = datos_plano.get('Datos_Habitaciones', '[]')
        habitaciones = json.loads(habitaciones_json)
        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Colores para diferentes tipos de habitaciones
        colores = {
            'Baño': 'lightblue',
            'Dor': 'lightgreen',
            'Cocina - Comedor': 'lightsalmon',
            'Estar': 'lightyellow',
            'Recibidor': 'lightpink',
            'Cocina': 'lightsalmon',
            'Comedor': 'lightsalmon'
            }
        
        # Añadir cada habitación al plano
        for hab in habitaciones:
            nombre = hab.get('Nombre', 'Sin nombre')
            tipo = hab.get('Tipo_Funcional', 'Desconocido')
            vertices = hab.get('Vertices', [])
            
            # Si no hay vértices, continuar al siguiente
            if not vertices:
                continue
                
            # Obtener color según el tipo funcional o usar un color por defecto
            color = colores.get(tipo, 'lightgray')
            
            # Crear polígono para la habitación
            poligono = Polygon(vertices, closed=True, fill=True, facecolor=color, 
                              edgecolor='black', linewidth=1.5, alpha=0.7)
            ax.add_patch(poligono)
            
            # Calcular centro para el texto
            vertices_array = np.array(vertices)
            cx = np.mean(vertices_array[:, 0])
            cy = np.mean(vertices_array[:, 1])
            
            # Añadir etiqueta con nombre y tipo
            ax.text(cx, cy, f"{nombre}\n{tipo}", ha='center', va='center', 
                   fontsize=10, fontweight='bold')
        
        # # Configurar límites y aspecto
        # if version == "v1":
        #     largo_casa = 2.440 * 2
        #     ancho_casa = 2.440 * 3
        # elif version == "v2":
        #     largo_casa = 2 * 2.440
        #     ancho_casa = 4 * 2.440
        # elif version == "v3":
        #     largo_casa = 2.440 * 2
        #     ancho_casa = 2.440 * 6
        # elif version == "v4":
        #     largo_casa = 2.440 * 3
        #     ancho_casa = 2.440 * 6
        # elif version == "v5":
        #     largo_casa = 2.440 * 4
        #     ancho_casa = 2.440 * 6
        # else:
        #     # Si no coincide con ninguna versión conocida, usar valores del Excel o valores por defecto
        #     ancho_casa = datos_plano.get('Ancho_Casa', datos_plano.get('ancho_casa', 7.32))
        #     largo_casa = datos_plano.get('Largo_Casa', datos_plano.get('largo_casa', 4.88))
            
        ax.set_xlim(0, largo_casa)
        ax.set_ylim(0, ancho_casa)
        ax.set_aspect('equal')
        ax.set_title(titulo, fontsize=16)
        ax.set_xlabel('Largo (m)')
        ax.set_ylabel('Ancho (m)')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        return fig
    except Exception as e:
        st.error(f"Error al visualizar el plano: {e}")
        return None

# Cargar los datos
df = cargar_datos_excel()

if df is not None:
    # Mostrar columnas para depuración
    st.write("Columnas disponibles en el Excel:", list(df.columns))
    
    # Extraer versiones disponibles
    if 'Version' in df.columns:
        versiones = sorted(df['Version'].unique())
        version_seleccionada = st.selectbox("Seleccionar versión:", versiones)
        
        # Filtrar datos para la versión seleccionada
        df_filtrado = df[df['Version'] == version_seleccionada]
        
        # Mostrar todos los planos de la versión seleccionada
        st.subheader(f"Todos los planos de la versión {version_seleccionada}")
        
        # Obtener todos los planos de esta versión
        planos_ids = sorted(df_filtrado['Plano_ID'].unique())
        
        # Mostrar los planos en filas de 2 columnas
        for i in range(0, len(planos_ids), 2):
            cols = st.columns(2)
            
            for j in range(2):
                if i+j < len(planos_ids):
                    plano_id = planos_ids[i+j]
                    datos_plano = df_filtrado[df_filtrado['Plano_ID'] == plano_id].iloc[0]
                    
                    with cols[j]:
                        st.write(f"### Plano {plano_id}")
                        
                        # # Mostrar información básica utilizando get_safe
                        # col1, col2, col3 = st.columns(3)
                        # with col1:
                        #     ancho_valor = get_safe(datos_plano, 'Ancho_Casa', get_safe(datos_plano, 'ancho_casa'))
                        #     st.metric("Ancho", ancho_valor)
                        # with col2:
                        #     largo_valor = get_safe(datos_plano, 'Largo_Casa', get_safe(datos_plano, 'largo_casa'))
                        #     st.metric("Largo", largo_valor)
                        # with col3:
                        #     num_hab = datos_plano.get('Num_Habitaciones', "N/A")
                        #     st.metric("Habitaciones", num_hab)
                        
                        # Visualizar plano
                        titulo = f"Plano {plano_id}"
                        fig = visualizar_plano(datos_plano, titulo,version_seleccionada)
                        if fig:
                            st.pyplot(fig)
    else:
        st.error("El Excel no contiene una columna 'Version'. Asegúrate de que el formato sea correcto.")
else:
    st.error("No se pudo cargar el archivo de planos.")
    st.info("""
    Esta aplicación requiere un archivo llamado 'planos_ploteo.xlsx' en el mismo directorio.
    Asegúrate de que el archivo esté correctamente formateado con columnas para 'Version', 'Plano_ID', etc.
    """)
