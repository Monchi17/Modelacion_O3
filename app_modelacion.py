import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import json
import numpy as np
import os

# IMPORTANTE: st.set_page_config debe estar al inicio
st.set_page_config(page_title="Visualizador de Planos", layout="wide")

# Estado de sesión para controlar la navegación
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'bienvenida'

# Inicializar estado de sesión para planos seleccionados
if 'planos_seleccionados' not in st.session_state:
    st.session_state.planos_seleccionados = {}

# Inicializar estado para las rondas de selección de v2
if 'v2_ronda' not in st.session_state:
    st.session_state.v2_ronda = 1  # Ronda 1: seleccionar 3 de 12, Ronda 2: seleccionar 1 de 3

if 'v2_semifinalistas' not in st.session_state:
    st.session_state.v2_semifinalistas = []

def mostrar_bienvenida():
    """Página de bienvenida con formulario de usuario"""
    # Título centrado y estilizado
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #2E86AB; font-size: 3rem; margin-bottom: 1rem;'>
            🏗️ Visualizador de Planos
        </h1>
        <p style='font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
            Sistema de visualización y selección de planos arquitectónicos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulario de información del usuario
    st.markdown("### 📋 Por favor, ingresa tu información antes de continuar:")
    
    # Crear columnas para mejor diseño
    col1, col2 = st.columns(2)
    
    with col1:
        nombre = st.text_input("👤 Nombre completo", placeholder="Ingrese su nombre completo")
        profesion = st.text_input("💼 Profesión", placeholder="Ej: Arquitecto, Ingeniero Civil")
        experiencia = st.number_input("📅 Años de experiencia", min_value=0, max_value=100, step=1, value=0)
    
    with col2:
        institucion = st.text_input("🏢 Institución", placeholder="Universidad o empresa")
        correo = st.text_input("📧 Correo electrónico", placeholder="ejemplo@correo.com")
        telefono = st.text_input("📱 Teléfono (opcional)", placeholder="+56 9 XXXX XXXX")
    
    # Guardar datos en session state
    st.session_state.datos_usuario = {
        "nombre": nombre.strip(),
        "profesion": profesion.strip(),
        "experiencia": experiencia,
        "institucion": institucion.strip(),
        "correo": correo.strip(),
        "telefono": telefono.strip()
    }
    
    # Validación básica
    campos_requeridos = [nombre, profesion, institucion, correo]
    campos_validos = all(campo.strip() for campo in campos_requeridos)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Centrar el botón
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🚀 Continuar", 
                    disabled=not campos_validos,
                    use_container_width=False,
                    help="Complete todos los campos requeridos para continuar" if not campos_validos else ""):
            if campos_validos:
                st.session_state.pagina = 'planos'
                st.rerun()
            else:
                st.error("Por favor, complete todos los campos requeridos.")

def mostrar_info_usuario():
    """Mostrar información del usuario en la parte superior"""
    if 'datos_usuario' in st.session_state:
        datos = st.session_state.datos_usuario
        st.sidebar.markdown("### 👤 Información del Usuario")
        st.sidebar.write(f"**Nombre:** {datos['nombre']}")
        st.sidebar.write(f"**Profesión:** {datos['profesion']}")
        st.sidebar.write(f"**Experiencia:** {datos['experiencia']} años")
        st.sidebar.write(f"**Institución:** {datos['institucion']}")
        
        # Botón para volver a la página de bienvenida
        if st.sidebar.button("🔄 Cambiar información"):
            st.session_state.pagina = 'bienvenida'
            st.rerun()

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
            'Cocina - Comedor': 'lightyellow',
            'Estar': 'lightyellow',
            'Recibidor': 'lightyellow',
            'Cocina': 'lightyellow',
            'Comedor': 'lightyellow'
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
        ax.set_xlabel('Largo (m)', fontsize=8)
        ax.set_ylabel('Ancho (m)', fontsize=8)
        ax.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        
        return fig
    except Exception as e:
        st.error(f"Error al visualizar el plano: {e}")
        return None

def seleccionar_plano_v2(plano_id, datos_plano, ronda):
    """Función especial para manejar la selección de planos v2 con sistema de rondas"""
    if ronda == 1:  # Primera ronda: seleccionar 3 de 12
        if plano_id not in st.session_state.v2_semifinalistas:
            if len(st.session_state.v2_semifinalistas) < 3:
                st.session_state.v2_semifinalistas.append(plano_id)
                st.success(f"Plano {plano_id} seleccionado como semifinalista ({len(st.session_state.v2_semifinalistas)}/3)")
                
                # Si ya tenemos 3 semifinalistas, pasar a la ronda 2
                if len(st.session_state.v2_semifinalistas) == 3:
                    st.session_state.v2_ronda = 2
                    st.info("¡3 planos semifinalistas seleccionados! Ahora elige el plano final.")
            else:
                st.warning("Ya has seleccionado 3 planos semifinalistas.")
        else:
            # Deseleccionar
            st.session_state.v2_semifinalistas.remove(plano_id)
            st.info(f"Plano {plano_id} deseleccionado ({len(st.session_state.v2_semifinalistas)}/3)")
    
    elif ronda == 2:  # Segunda ronda: seleccionar 1 de 3
        st.session_state.planos_seleccionados['v2'] = {
            'plano_id': plano_id,
            'datos': datos_plano
        }
        st.success(f"¡Plano {plano_id} seleccionado como ganador de v2!")

def reiniciar_seleccion_v2():
    """Reiniciar la selección de v2 para empezar de nuevo"""
    st.session_state.v2_ronda = 1
    st.session_state.v2_semifinalistas = []
    if 'v2' in st.session_state.planos_seleccionados:
        del st.session_state.planos_seleccionados['v2']

def seleccionar_plano(version, plano_id, datos_plano):
    """Función para manejar la selección de un plano (para versiones diferentes a v2)"""
    # Guardar el plano seleccionado para esta versión
    st.session_state.planos_seleccionados[version] = {
        'plano_id': plano_id,
        'datos': datos_plano
    }
    st.success(f"Plano {plano_id} de la versión {version} seleccionado correctamente")

def mostrar_visualizador():
    """Página principal del visualizador de planos"""
    st.title("🏗️ Visualizador de Planos")
    
    # Mostrar información del usuario en la sidebar
    mostrar_info_usuario()
    
    # Cargar los datos
    df = cargar_datos_excel()
    
    if df is not None:
        # Extraer versiones disponibles
        if 'Version' in df.columns:
            versiones = sorted(df['Version'].unique())
            
            # Selector de versión
            version_seleccionada = st.selectbox("📐 Seleccionar versión:", versiones)
            
            # Filtrar datos para la versión seleccionada
            df_filtrado = df[df['Version'] == version_seleccionada]
            
            # Lógica especial para v2 con sistema de rondas
            if version_seleccionada == "v2":
                mostrar_seleccion_v2(df_filtrado)
            else:
                # Lógica normal para otras versiones
                mostrar_seleccion_normal(df_filtrado, version_seleccionada)
        else:
            st.error("El Excel no contiene una columna 'Version'. Asegúrate de que el formato sea correcto.")
    else:
        st.error("No se pudo cargar el archivo de planos.")
        st.info("""
        Esta aplicación requiere un archivo llamado 'planos_ploteo.xlsx' en el mismo directorio.
        Asegúrate de que el archivo esté correctamente formateado con columnas para 'Version', 'Plano_ID', etc.
        """)

def mostrar_seleccion_v2(df_filtrado):
    """Lógica especial para v2 con sistema de rondas"""
    planos_ids = sorted(df_filtrado['Plano_ID'].unique())
    
    # Mostrar información de la ronda actual
    if st.session_state.v2_ronda == 1:
        st.subheader("🏠 Ronda 1: Selecciona 3 planos semifinalistas de v2")
        st.info(f"Planos seleccionados: {len(st.session_state.v2_semifinalistas)}/3")
        
        # Botón para reiniciar selección
        if len(st.session_state.v2_semifinalistas) > 0:
            if st.button("🔄 Reiniciar selección"):
                reiniciar_seleccion_v2()
                st.rerun()
        
        # Mostrar todos los planos (12 planos de 4 en 4)
        num_columnas = 4
        num_filas = 3  # 12 planos / 4 columnas = 3 filas
        planos_a_mostrar = planos_ids
        
    else:  # Ronda 2
        st.subheader("🏆 Ronda 2: Selecciona el plano ganador de v2")
        st.success(f"Semifinalistas: {', '.join([f'Plano {p}' for p in st.session_state.v2_semifinalistas])}")
        
        # Botón para volver a la ronda 1
        if st.button("⬅️ Volver a Ronda 1"):
            st.session_state.v2_ronda = 1
            st.rerun()
        
        # Mostrar solo los 3 semifinalistas
        num_columnas = 3
        num_filas = 1
        planos_a_mostrar = st.session_state.v2_semifinalistas
    
    # Mostrar los planos
    for fila in range(num_filas):
        cols = st.columns(num_columnas)
        
        for col in range(num_columnas):
            idx_plano = fila * num_columnas + col
            
            if idx_plano < len(planos_a_mostrar):
                plano_id = planos_a_mostrar[idx_plano]
                datos_plano = df_filtrado[df_filtrado['Plano_ID'] == plano_id].iloc[0]
                
                with cols[col]:
                    st.write(f"### Plano {plano_id}")
                    
                    # Visualizar plano
                    titulo = f"Plano {plano_id}"
                    fig = visualizar_plano(datos_plano, titulo, "v2")
                    if fig:
                        st.pyplot(fig, use_container_width=True)
                    
                    # Lógica de botones según la ronda
                    if st.session_state.v2_ronda == 1:
                        # Ronda 1: Seleccionar semifinalistas
                        is_selected = plano_id in st.session_state.v2_semifinalistas
                        
                        if is_selected:
                            st.success("✅ SEMIFINALISTA")
                            if st.button(f"Deseleccionar", key=f"deselect_v2_{plano_id}"):
                                seleccionar_plano_v2(plano_id, datos_plano.to_dict(), 1)
                                st.rerun()
                        else:
                            can_select = len(st.session_state.v2_semifinalistas) < 3
                            if st.button(f"Seleccionar", 
                                        key=f"select_v2_r1_{plano_id}",
                                        disabled=not can_select):
                                seleccionar_plano_v2(plano_id, datos_plano.to_dict(), 1)
                                st.rerun()
                    
                    else:
                        # Ronda 2: Seleccionar ganador
                        is_winner = ('v2' in st.session_state.planos_seleccionados and 
                                   st.session_state.planos_seleccionados['v2']['plano_id'] == plano_id)
                        
                        if is_winner:
                            st.success("🏆 GANADOR")
                        else:
                            if st.button(f"Seleccionar Ganador", key=f"select_v2_r2_{plano_id}"):
                                seleccionar_plano_v2(plano_id, datos_plano.to_dict(), 2)
                                st.rerun()

def mostrar_seleccion_normal(df_filtrado, version_seleccionada):
    """Lógica normal para versiones diferentes a v2"""
    st.subheader(f"🏠 Todos los planos de la versión {version_seleccionada}")
    
    # Obtener todos los planos de esta versión
    planos_ids = sorted(df_filtrado['Plano_ID'].unique())
    total_planos = len(planos_ids)
    
    # Determinar el número de columnas basado en la versión
    if version_seleccionada == "v1":
        num_columnas = 4
        num_filas = 1  # Una fila para v1
    elif version_seleccionada == "v3":
        num_columnas = 4
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
    
    # Mostrar los planos
    for fila in range(num_filas):
        cols = st.columns(num_columnas)
        
        for col in range(num_columnas):
            idx_plano = fila * num_columnas + col
            
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
                    
                    # Botón para seleccionar este plano
                    if is_selected:
                        st.success("✅ SELECCIONADO")
                    else:
                        if st.button(f"Seleccionar", key=f"select_{version_seleccionada}_{plano_id}"):
                            seleccionar_plano(version_seleccionada, plano_id, datos_plano.to_dict())
                            st.rerun()

# Control de flujo principal
if st.session_state.pagina == 'bienvenida':
    mostrar_bienvenida()
else:
    mostrar_visualizador()

