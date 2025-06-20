import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import json
import numpy as np
import os

st.set_page_config(page_title="Visualizador de Planos", layout="wide")
st.title("Visualizador de Planos desde Excel")

# Ruta al archivo Excel (asumiendo que está en el mismo directorio que la app)
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

def visualizar_plano(datos_plano, titulo):
    """Visualiza un plano a partir de sus datos"""
    # Extraer dimensiones
    ancho_casa = datos_plano['Ancho_Casa']
    largo_casa = datos_plano['Largo_Casa']
    
    # Extraer información de habitaciones (como JSON)
    habitaciones_json = datos_plano['Datos_Habitaciones']
    habitaciones = json.loads(habitaciones_json)
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Colores para diferentes tipos de habitaciones
    colores = {
        'Baño': 'lightblue',
        'Dor': 'lightgreen',
        'Cocina - Comedor': 'lightsalmon',
        'Estar': 'lightyellow',
        'Recibidor': 'lightpink'
    }
    
    # Añadir cada habitación al plano
    for hab in habitaciones:
        nombre = hab['Nombre']
        tipo = hab['Tipo_Funcional']
        vertices = hab['Vertices']
        
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
    
    # Configurar límites y aspecto
    ax.set_xlim(0, largo_casa)
    ax.set_ylim(0, ancho_casa)
    ax.set_aspect('equal')
    ax.set_title(titulo, fontsize=16)
    ax.set_xlabel('Largo (m)')
    ax.set_ylabel('Ancho (m)')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    return fig

# Cargar los datos
df = cargar_datos_excel()

if df is not None:
    st.success(f"Archivo {EXCEL_PATH} cargado correctamente")
    
    # Extraer versiones disponibles
    if 'Version' in df.columns:
        versiones = df['Version'].unique()
        version_seleccionada = st.selectbox("Seleccionar versión:", versiones)
        df_filtrado = df[df['Version'] == version_seleccionada]
    else:
        df_filtrado = df
        version_seleccionada = "Única"
    
    # Seleccionar plano por ID
    planos_ids = sorted(df_filtrado['Plano_ID'].unique())
    plano_seleccionado = st.selectbox("Seleccionar plano:", planos_ids)
    
    # Filtrar para obtener los datos del plano seleccionado
    datos_plano = df_filtrado[df_filtrado['Plano_ID'] == plano_seleccionado].iloc[0]
    
    # Mostrar información básica del plano
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ancho", f"{datos_plano['Ancho_Casa']:.2f} m")
    with col2:
        st.metric("Largo", f"{datos_plano['Largo_Casa']:.2f} m")
    with col3:
        st.metric("Habitaciones", datos_plano['Num_Habitaciones'])
    
    # Visualizar plano
    titulo = f"Plano {plano_seleccionado} (Versión {version_seleccionada})"
    fig = visualizar_plano(datos_plano, titulo)
    st.pyplot(fig)
    
    # Mostrar datos de habitaciones
    with st.expander("Ver detalles de habitaciones"):
        habitaciones = json.loads(datos_plano['Datos_Habitaciones'])
        
        # Crear tabla de habitaciones
        tabla_data = []
        for hab in habitaciones:
            tabla_data.append({
                "Nombre": hab['Nombre'],
                "Tipo": hab['Tipo_Funcional'],
                "Ancho (m)": f"{hab['Ancho']:.2f}",
                "Altura (m)": f"{hab['Altura']:.2f}",
                "Área (m²)": f"{hab['Ancho'] * hab['Altura']:.2f}"
            })
        
        st.table(pd.DataFrame(tabla_data))
else:
    st.error("No se pudo cargar el archivo de planos.")
    st.info("""
    Esta aplicación requiere un archivo llamado 'planos_ploteo.xlsx' en el mismo directorio.
    El archivo debe contener la estructura de datos generada por la función 'guardar_multiples_versiones_planos'.
    """)
