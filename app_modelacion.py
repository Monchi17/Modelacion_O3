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

# Inicializar estado para las rondas de selección de v3
if 'v3_grupo_actual' not in st.session_state:
    st.session_state.v3_grupo_actual = 1  # Grupo 1, 2, 3, o 4 (final)

if 'v3_seleccionados_por_grupo' not in st.session_state:
    st.session_state.v3_seleccionados_por_grupo = {}  # {grupo: plano_id}

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

def seleccionar_plano_v3(plano_id, datos_plano, grupo):
    """Función especial para manejar la selección de planos v3 con sistema de grupos"""
    if grupo <= 3:  # Grupos 1, 2, 3
        st.session_state.v3_seleccionados_por_grupo[grupo] = {
            'plano_id': plano_id,
            'datos': datos_plano
        }
        st.success(f"Plano {plano_id} seleccionado del Grupo {grupo}")
        
        # Avanzar al siguiente grupo automáticamente
        if grupo < 3:
            st.session_state.v3_grupo_actual = grupo + 1
            st.info(f"Pasando al Grupo {grupo + 1}")
        else:
            st.session_state.v3_grupo_actual = 4  # Ir a la ronda final
            st.info("¡Todos los grupos completados! Ahora elige el plano ganador.")
    
    elif grupo == 4:  # Ronda final
        st.session_state.planos_seleccionados['v3'] = {
            'plano_id': plano_id,
            'datos': datos_plano
        } 
        
        if is_selected:
            st.success("✅ SELECCIONADO")
        else:
            if st.button(f"Seleccionar", key=f"select_v3_g{grupo_actual}_{plano_id}"):
                seleccionar_plano_v3(plano_id, datos_plano.to_dict(), grupo_actual)
                st.rerun()

def reiniciar_seleccion_v3():
    """Reiniciar la selección de v3 para empezar de nuevo"""
    st.session_state.v3_grupo_actual = 1
    st.session_state.v3_seleccionados_por_grupo = {}
    if 'v3' in st.session_state.planos_seleccionados:
        del st.session_state.planos_seleccionados['v3']

def ir_grupo_anterior_v3():
    """Ir al grupo anterior en v3"""
    if st.session_state.v3_grupo_actual > 1:
        st.session_state.v3_grupo_actual -= 1
        # Si volvemos de la ronda final, no eliminar las selecciones previas
        if st.session_state.v3_grupo_actual == 3:
            # Solo eliminar la selección final si existe
            if 'v3' in st.session_state.planos_seleccionados:
                del st.session_state.planos_seleccionados['v3']

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
            
            # Lógica especial para v3 con sistema de rondas
            if version_seleccionada == "v3":
                mostrar_seleccion_v3(df_filtrado)
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

def mostrar_seleccion_v3(df_filtrado):
    """Lógica especial para v3 con sistema de grupos"""
    planos_ids = sorted(df_filtrado['Plano_ID'].unique())
    grupo_actual = st.session_state.v3_grupo_actual
    
    # Dividir los 12 planos en 3 grupos de 4
    grupos_planos = {
        1: planos_ids[0:4],   # Planos 1-4
        2: planos_ids[4:8],   # Planos 5-8
        3: planos_ids[8:12]   # Planos 9-12
    }
    
    if grupo_actual <= 3:
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if grupo_actual > 1:
                if st.button("⬅️ Grupo Anterior"):
                    ir_grupo_anterior_v3()
                    st.rerun()
        
        with col3:
            # Solo mostrar "Siguiente" si ya seleccionó un plano en este grupo
            if grupo_actual in st.session_state.v3_seleccionados_por_grupo and grupo_actual < 3:
                if st.button("➡️ Siguiente Grupo"):
                    st.session_state.v3_grupo_actual += 1
                    st.rerun()
        
        # Mostrar los 4 planos del grupo actual
        planos_grupo = grupos_planos[grupo_actual]
        cols = st.columns(4)
        
        for i, plano_id in enumerate(planos_grupo):
            datos_plano = df_filtrado[df_filtrado['Plano_ID'] == plano_id].iloc[0]
            
            with cols[i]:
                st.write(f"### Plano {plano_id}")
                
                # Visualizar plano
                titulo = f"Plano {plano_id}"
                fig = visualizar_plano(datos_plano, titulo, "v3")
                if fig:
                    st.pyplot(fig, use_container_width=True)
                
                # Verificar si este plano está seleccionado para este grupo
                plano_seleccionado = st.session_state.v3_seleccionados_por_grupo.get(grupo_actual, {}).get('plano_id')
                is_selected = plano_seleccionado == plano_id
                
                if is_selected:
                    st.success("✅ SELECCIONADO")
                else:
                    if st.button(f"Seleccionar", key=f"select_v3_g{grupo_actual}_{plano_id}"):
                        seleccionar_plano_v3(plano_id, datos_plano.to_dict(), grupo_actual)
                        st.rerun()
    
    else:  # grupo_actual == 4 (Ronda final)
        # Mostrar los 3 planos seleccionados
        planos_finalistas = []
        for grupo in [1, 2, 3]:
            if grupo in st.session_state.v3_seleccionados_por_grupo:
                plano_info = st.session_state.v3_seleccionados_por_grupo[grupo]
                planos_finalistas.append(f"Plano {plano_info['plano_id']} (Grupo {grupo})")
        
        #st.success(f"Finalistas: {', '.join(planos_finalistas)}")
        
        # Botón para volver al grupo anterior
        if st.button("⬅️ Volver al Grupo 3"):
            ir_grupo_anterior_v3()
            st.rerun()
        
        # Mostrar los 3 planos finalistas
        cols = st.columns(3)
        
        for i, grupo in enumerate([1, 2, 3]):
            if grupo in st.session_state.v3_seleccionados_por_grupo:
                plano_info = st.session_state.v3_seleccionados_por_grupo[grupo]
                plano_id = plano_info['plano_id']
                datos_plano = df_filtrado[df_filtrado['Plano_ID'] == plano_id].iloc[0]
                    
                with cols[i]:
                    st.write(f"### Plano {plano_id}")
                    
                    # Visualizar plano
                    titulo = f"Plano {plano_id}"
                    fig = visualizar_plano(datos_plano, titulo, "v3")
                    if fig:
                        st.pyplot(fig, use_container_width=True)
                    
                    # Verificar si es el ganador final
                    is_winner = ('v3' in st.session_state.planos_seleccionados and 
                               st.session_state.planos_seleccionados['v3']['plano_id'] == plano_id)
                    
                    if is_winner:
                        st.success("🏆 GANADOR FINAL")
                    else:
                        if st.button(f"Seleccionar", key=f"select_v3_final_{plano_id}"):
                            seleccionar_plano_v3(plano_id, datos_plano.to_dict(), 4)
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
    elif version_seleccionada == "v2":
        num_columnas = 4
        num_filas = 3  # 3 filas para v2 (12 planos)
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
                    if version_seleccionada in ["v4", "v5"]:
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
