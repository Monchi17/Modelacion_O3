
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import json
import numpy as np
import os

st.set_page_config(page_title="Visualizador de Planos", layout="wide")
st.title("Visualizador de Planos")

# Inicializar estado de sesión para planos seleccionados
if 'planos_seleccionados' not in st.session_state:
    st.session_state.planos_seleccionados = {}

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
        
        # Crear figura con tamaño reducido
        fig, ax = plt.subplots(figsize=(5, 4))  # Tamaño más reducido para v3/v4/v5 con más columnas
        
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
            
            # Añadir etiqueta con nombre y tipo (fuente más pequeña)
            # Ajustar tamaño de fuente según la versión
            font_size = 6 if version in ["v3", "v4", "v5"] else 8
            ax.text(cx, cy, f"{nombre}\n{tipo}", ha='center', va='center', 
                   fontsize=font_size, fontweight='bold')

        # Configurar límites y aspecto
        if version == "v1":
            largo_casa = 2.440 * 2
            ancho_casa = 2.440 * 3
            ax.set_xlim(0, largo_casa)
            ax.set_ylim(0, ancho_casa)
        
        elif version == "v2":
            largo_casa = 2 * 2.440
            ancho_casa = 4 * 2.440
            ax.set_xlim(0, largo_casa)
            ax.set_ylim(0, ancho_casa)
            
        elif version == "v3":
            largo_casa = 2.440 * 2
            ancho_casa = 2.440 * 6
            ax.set_xlim(0, largo_casa)
            ax.set_ylim(0, ancho_casa)
            
        elif version == "v4":
            largo_casa = 2.440 * 3
            ancho_casa = 2.440 * 6
            ax.set_xlim(-2.440, 2.440*2)
            ax.set_ylim(0, ancho_casa)
        elif version == "v5":
            largo_casa = 2.440 * 4
            ancho_casa = 2.440 * 6
            ax.set_xlim(-2.440*2, 2.440*2)
            ax.set_ylim(0, ancho_casa)
       
        ax.set_aspect('equal')
        ax.set_title(titulo, fontsize=10)  # Título más pequeño
        ax.set_xlabel('Largo (m)', fontsize=8)  # Etiqueta más pequeña
        ax.set_ylabel('Ancho (m)', fontsize=8)  # Etiqueta más pequeña
        ax.grid(True, linestyle='--', alpha=0.5)  # Grid menos prominente
        plt.tight_layout()
        
        return fig
    except Exception as e:
        st.error(f"Error al visualizar el plano: {e}")
        return None

def seleccionar_plano(version, plano_id, datos_plano):
    """Función para manejar la selección de un plano"""
    # Guardar el plano seleccionado para esta versión
    st.session_state.planos_seleccionados[version] = {
        'plano_id': plano_id,
        'datos': datos_plano
    }
    st.success(f"Plano {plano_id} de la versión {version} seleccionado correctamente")

# Cargar los datos
df = cargar_datos_excel()

if df is not None:
    # Extraer versiones disponibles
    if 'Version' in df.columns:
        versiones = sorted(df['Version'].unique())
        
        # Mostrar planos seleccionados (si hay alguno)
        if any(st.session_state.planos_seleccionados):
            st.subheader("Planos seleccionados")
            cols_seleccionados = st.columns(len(versiones))
            
            for i, version in enumerate(versiones):
                if version in st.session_state.planos_seleccionados:
                    with cols_seleccionados[i]:
                        plano_data = st.session_state.planos_seleccionados[version]
                        st.write(f"### {version} - Plano {plano_data['plano_id']}")
                        fig = visualizar_plano(plano_data['datos'], f"{version} - Plano {plano_data['plano_id']}", version)
                        if fig:
                            st.pyplot(fig, use_container_width=True)
        
        # Selector de versión
        version_seleccionada = st.selectbox("Seleccionar versión:", versiones)
        
        # Filtrar datos para la versión seleccionada
        df_filtrado = df[df['Version'] == version_seleccionada]
        
        # Mostrar todos los planos de la versión seleccionada
        st.subheader(f"Todos los planos de la versión {version_seleccionada}")
        
        # Obtener todos los planos de esta versión
        planos_ids = sorted(df_filtrado['Plano_ID'].unique())
        total_planos = len(planos_ids)
        
        # Determinar el número de columnas basado en la versión
        if version_seleccionada == "v1" or version_seleccionada == "v2":
            num_columnas = 4
            num_filas = 1  # Una fila para v1 y v2
        elif version_seleccionada == "v3":
            num_columnas = 6
            num_filas = (total_planos + num_columnas - 1) // num_columnas  # Redondear hacia arriba
        elif version_seleccionada == "v4":
            num_columnas = 4
            num_filas = 3  # 3 filas para v4
        elif version_seleccionada == "v5":
            num_columnas = 4
            num_filas = 6  # 6 filas para v5
        else:
            num_columnas = 2
            num_filas = (total_planos + num_columnas - 1) // num_columnas
        
        # Mostrar los planos en filas según el número de columnas definido
        for fila in range(num_filas):
            # Crear columnas para esta fila
            cols = st.columns(num_columnas)
            
            # Mostrar los planos de esta fila
            for col in range(num_columnas):
                idx_plano = fila * num_columnas + col
                
                # Verificar que no nos pasemos de la cantidad de planos
                if idx_plano < total_planos:
                    plano_id = planos_ids[idx_plano]
                    datos_plano = df_filtrado[df_filtrado['Plano_ID'] == plano_id].iloc[0]
                    
                    with cols[col]:
                        # Para versiones con muchos planos, hacer encabezados más compactos
                        if version_seleccionada in ["v3", "v4", "v5"]:
                            st.write(f"#### Plano {plano_id}")
                        else:
                            st.write(f"### Plano {plano_id}")
                        
                        # Visualizar plano
                        titulo = f"Plano {plano_id}"
                        fig = visualizar_plano(datos_plano, titulo, version_seleccionada)
                        if fig:
                            st.pyplot(fig, use_container_width=True)
                        
                        # Resaltar si este plano está seleccionado
                        is_selected = (version_seleccionada in st.session_state.planos_seleccionados and 
                                      st.session_state.planos_seleccionados[version_seleccionada]['plano_id'] == plano_id)
                        
                        # Botones más compactos para versiones con muchos planos
                        col1, col2 = st.columns(2)
                        
                        # Botón para seleccionar este plano
                        if is_selected:
                            st.success("✅ SELECCIONADO")
                            with col1:
                                if st.button(f"Deseleccionar", key=f"deselect_{version_seleccionada}_{plano_id}"):
                                    if version_seleccionada in st.session_state.planos_seleccionados:
                                        del st.session_state.planos_seleccionados[version_seleccionada]
                                    st.rerun()
                        else:
                            with col1:
                                if st.button(f"Seleccionar", key=f"select_{version_seleccionada}_{plano_id}"):
                                    seleccionar_plano(version_seleccionada, plano_id, datos_plano.to_dict())
                                    st.rerun()
    else:
        st.error("El Excel no contiene una columna 'Version'. Asegúrate de que el formato sea correcto.")
else:
    st.error("No se pudo cargar el archivo de planos.")
    st.info("""
    Esta aplicación requiere un archivo llamado 'planos_ploteo.xlsx' en el mismo directorio.
    Asegúrate de que el archivo esté correctamente formateado con columnas para 'Version', 'Plano_ID', etc.
    """)
