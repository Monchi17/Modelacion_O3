import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import json
import numpy as np
import os
from datetime import datetime

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

# Inicializar estado para las rondas de selección de v4
if 'v4_grupo_actual' not in st.session_state:
    st.session_state.v4_grupo_actual = 1  # Grupo 1, 2, 3, o 4 (final)

if 'v4_seleccionados_por_grupo' not in st.session_state:
    st.session_state.v4_seleccionados_por_grupo = {}  # {grupo: plano_id}

# Inicializar estado para las rondas de selección de v5
if 'v5_grupo_actual' not in st.session_state:
    st.session_state.v5_grupo_actual = 1  # Grupo 1, 2, 3, 4, 5, 6, o 7 (final)

if 'v5_seleccionados_por_grupo' not in st.session_state:
    st.session_state.v5_seleccionados_por_grupo = {}  # {grupo: plano_id}

def mostrar_bienvenida():
    """Página de bienvenida con formulario de usuario"""
    # Título centrado y estilizado
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #2E86AB; font-size: 3rem; margin-bottom: 1rem;'>
            Visualizador de Planos
        </h1>
        <p style='font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
            Sistema de visualización y selección de planos arquitectónicos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulario de información del usuario
    st.markdown("### Por favor, ingresa tu información antes de continuar:")
    
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
        if st.button("Continuar", 
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
    """Función helper para obtener datos de forma segura"""
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
            ax.set_xlim(0, largo_casa)
            ax.set_ylim(0, ancho_casa)
        elif version == "v2":
            ax.set_xlim(0, largo_casa)
            ax.set_ylim(0, ancho_casa)
        elif version == "v3":
            ax.set_xlim(0, largo_casa)
            ax.set_ylim(0, ancho_casa)
        elif version == "v4":
            ax.set_xlim(-2.440, 2.440*2)
            ax.set_ylim(0, ancho_casa)
        elif version == "v5":
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
        st.success(f"¡Plano {plano_id} seleccionado como ganador de v3!")

def seleccionar_plano_v4(plano_id, datos_plano, grupo):
    """Función especial para manejar la selección de planos v4 con sistema de grupos"""
    if grupo <= 3:  # Grupos 1, 2, 3
        st.session_state.v4_seleccionados_por_grupo[grupo] = {
            'plano_id': plano_id,
            'datos': datos_plano
        }
        st.success(f"Plano {plano_id} seleccionado del Grupo {grupo}")
        
        # Avanzar al siguiente grupo automáticamente
        if grupo < 3:
            st.session_state.v4_grupo_actual = grupo + 1
            st.info(f"Pasando al Grupo {grupo + 1}")
        else:
            st.session_state.v4_grupo_actual = 4  # Ir a la ronda final
            st.info("¡Todos los grupos completados! Ahora elige el plano ganador.")
    
    elif grupo == 4:  # Ronda final
        st.session_state.planos_seleccionados['v4'] = {
            'plano_id': plano_id,
            'datos': datos_plano
        }
        st.success(f"¡Plano {plano_id} seleccionado como ganador de v4!")

def seleccionar_plano_v5(plano_id, datos_plano, grupo):
    """Función especial para manejar la selección de planos v5 con sistema de grupos"""
    if grupo <= 6:  # Grupos 1, 2, 3, 4, 5, 6
        st.session_state.v5_seleccionados_por_grupo[grupo] = {
            'plano_id': plano_id,
            'datos': datos_plano
        }
        st.success(f"Plano {plano_id} seleccionado del Grupo {grupo}")
        
        # Avanzar al siguiente grupo automáticamente
        if grupo < 6:
            st.session_state.v5_grupo_actual = grupo + 1
            st.info(f"Pasando al Grupo {grupo + 1}")
        else:
            st.session_state.v5_grupo_actual = 7  # Ir a la ronda final
            st.info("¡Todos los grupos completados! Ahora elige el plano ganador.")
    
    elif grupo == 7:  # Ronda final
        st.session_state.planos_seleccionados['v5'] = {
            'plano_id': plano_id,
            'datos': datos_plano
        }
        st.success(f"¡Plano {plano_id} seleccionado como ganador de v5!")

def reiniciar_seleccion_v3():
    """Reiniciar la selección de v3 para empezar de nuevo"""
    st.session_state.v3_grupo_actual = 1
    st.session_state.v3_seleccionados_por_grupo = {}
    if 'v3' in st.session_state.planos_seleccionados:
        del st.session_state.planos_seleccionados['v3']

def reiniciar_seleccion_v4():
    """Reiniciar la selección de v4 para empezar de nuevo"""
    st.session_state.v4_grupo_actual = 1
    st.session_state.v4_seleccionados_por_grupo = {}
    if 'v4' in st.session_state.planos_seleccionados:
        del st.session_state.planos_seleccionados['v4']

def reiniciar_seleccion_v5():
    """Reiniciar la selección de v5 para empezar de nuevo"""
    st.session_state.v5_grupo_actual = 1
    st.session_state.v5_seleccionados_por_grupo = {}
    if 'v5' in st.session_state.planos_seleccionados:
        del st.session_state.planos_seleccionados['v5']

def ir_grupo_anterior_v3():
    """Ir al grupo anterior en v3"""
    if st.session_state.v3_grupo_actual > 1:
        st.session_state.v3_grupo_actual -= 1
        # Si volvemos de la ronda final, no eliminar las selecciones previas
        if st.session_state.v3_grupo_actual == 3:
            # Solo eliminar la selección final si existe
            if 'v3' in st.session_state.planos_seleccionados:
                del st.session_state.planos_seleccionados['v3']

def ir_grupo_anterior_v4():
    """Ir al grupo anterior en v4"""
    if st.session_state.v4_grupo_actual > 1:
        st.session_state.v4_grupo_actual -= 1
        # Si volvemos de la ronda final, no eliminar las selecciones previas
        if st.session_state.v4_grupo_actual == 3:
            # Solo eliminar la selección final si existe
            if 'v4' in st.session_state.planos_seleccionados:
                del st.session_state.planos_seleccionados['v4']

def ir_grupo_anterior_v5():
    """Ir al grupo anterior en v5"""
    if st.session_state.v5_grupo_actual > 1:
        st.session_state.v5_grupo_actual -= 1
        # Si volvemos de la ronda final, no eliminar las selecciones previas
        if st.session_state.v5_grupo_actual == 6:
            # Solo eliminar la selección final si existe
            if 'v5' in st.session_state.planos_seleccionados:
                del st.session_state.planos_seleccionados['v5']

def seleccionar_plano(version, plano_id, datos_plano):
    """Función para manejar la selección de un plano (para versiones diferentes a v3)"""
    # Guardar el plano seleccionado para esta versión
    st.session_state.planos_seleccionados[version] = {
        'plano_id': plano_id,
        'datos': datos_plano
    }
    st.success(f"Plano {plano_id} de la versión {version} seleccionado correctamente")


def verificar_selecciones_completas():
    """Verifica si el usuario ha seleccionado planos de todas las versiones disponibles"""
    versiones_requeridas = ['v1', 'v2', 'v3', 'v4', 'v5']
    selecciones_completas = True
    versiones_faltantes = []
    
    for version in versiones_requeridas:
        if version not in st.session_state.planos_seleccionados:
            selecciones_completas = False
            versiones_faltantes.append(version.upper())
    
    return selecciones_completas, versiones_faltantes

def guardar_datos_usuario_excel(datos_usuario, selecciones):
    """
    Guarda los datos del usuario y sus selecciones en un archivo Excel llamado 'Respuestas.xlsx'.
    Crea el archivo si no existe, o agrega los datos si ya existe.
    """
    archivo_resultados = "Respuestas.xlsx"
    
    try:
        # Obtener timestamp para el registro
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Obtener el siguiente número de usuario
        numero_usuario = 1
        if os.path.exists(archivo_resultados):
            try:
                df_existente = pd.read_excel(archivo_resultados)
                numero_usuario = len(df_existente) + 1
            except:
                numero_usuario = 1
        
        # Crear el registro del usuario según el formato solicitado
        registro = {
            'Timestamp': timestamp,
            'Numero': numero_usuario,
            'Nombre_completo': datos_usuario.get('nombre', ''),
            'Profesion': datos_usuario.get('profesion', ''),
            'Anos_experiencia': datos_usuario.get('experiencia', 0),
            'Institucion': datos_usuario.get('institucion', ''),
            'Correo_electronico': datos_usuario.get('correo', ''),
            'Telefono': datos_usuario.get('telefono', ''),
            'V1': selecciones.get('v1', {}).get('plano_id', 'No seleccionado'),
            'V2': selecciones.get('v2', {}).get('plano_id', 'No seleccionado'),
            'V3': selecciones.get('v3', {}).get('plano_id', 'No seleccionado'),
            'V4': selecciones.get('v4', {}).get('plano_id', 'No seleccionado'),
            'V5': selecciones.get('v5', {}).get('plano_id', 'No seleccionado')
        }
        
        # Convertir a DataFrame
        df_nuevo = pd.DataFrame([registro])
        
        # Verificar si el archivo ya existe
        if os.path.exists(archivo_resultados):
            # Leer el archivo existente y agregar los nuevos datos
            try:
                df_existente = pd.read_excel(archivo_resultados)
                df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
            except Exception as e:
                # Si hay error leyendo el archivo existente, crear uno nuevo
                st.warning(f"Error leyendo archivo existente: {e}. Creando archivo nuevo.")
                df_final = df_nuevo
        else:
            # Crear archivo nuevo
            df_final = df_nuevo
        
        # Guardar el archivo (corregir la línea problemática)
        df_final.to_excel(archivo_resultados, index=False)
        
        return True, f"Datos guardados exitosamente. Usuario #{numero_usuario} registrado."
        
    except Exception as e:
        return False, f"Error al guardar los datos: {str(e)}"

def mostrar_boton_finalizar():
    """Muestra el botón finalizar si todas las versiones han sido seleccionadas"""
    selecciones_completas, versiones_faltantes = verificar_selecciones_completas()
    
    st.markdown("---")
    st.subheader("📋 Estado de las Selecciones")
    
    # Mostrar estado de cada versión
    versiones = ['v1', 'v2', 'v3', 'v4', 'v5']
    cols = st.columns(5)
    
    for i, version in enumerate(versiones):
        with cols[i]:
            if version in st.session_state.planos_seleccionados:
                plano_id = st.session_state.planos_seleccionados[version]['plano_id']
                st.success(f"{version.upper()}\nPlano {plano_id}")
            else:
                st.error(f"{version.upper()}\nNo seleccionado")
    
    # Mostrar versiones faltantes si las hay
    if not selecciones_completas:
        st.warning(f"⚠️ Faltan selecciones en: {', '.join(versiones_faltantes)}")
        st.info("Completa todas las selecciones para poder finalizar.")
    
    # Mostrar botón finalizar solo si están completas todas las selecciones
    if selecciones_completas:
        # Centrar el botón finalizar
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("FINALIZAR", 
                    use_container_width=True,
                    type="primary",
                    help="Guardar todas las selecciones y finalizar la evaluación"):
                
                # Verificar que tenemos los datos del usuario
                if 'datos_usuario' in st.session_state:
                    with st.spinner("Guardando respuestas..."):
                        exito, mensaje = guardar_datos_usuario_excel(
                            st.session_state.datos_usuario, 
                            st.session_state.planos_seleccionados
                        )
                        
                        if exito:
                            st.success("✅ " + mensaje)
                            st.balloons()
                            
                            # Mostrar resumen final
                            st.markdown("### 📊 Resumen de tus selecciones:")
                            for version in ['v1', 'v2', 'v3', 'v4', 'v5']:
                                if version in st.session_state.planos_seleccionados:
                                    plano_id = st.session_state.planos_seleccionados[version]['plano_id']
                                    st.write(f"- **{version.upper()}**: Plano {plano_id}")
                            
                            st.info("¡Gracias por tu participación! Puedes cerrar la aplicación.")
                            
                            # Opcional: Limpiar session state para una nueva sesión
                            if st.button("Iniciar Nueva Evaluación"):
                                for key in list(st.session_state.keys()):
                                    del st.session_state[key]
                                st.rerun()
                        else:
                            st.error("❌ " + mensaje)
                            st.error("No se pudieron guardar los datos. Intenta nuevamente.")
                else:
                    st.error("❌ Error: No se encontraron los datos del usuario.")
                    st.error("Por favor, regresa a la página de bienvenida y completa la información.")

def guardar_backup_json(datos_usuario, selecciones):
    """Guardar backup detallado en JSON (opcional)"""
    try:
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'usuario': datos_usuario,
            'selecciones_finales': selecciones,
            'proceso_v3': st.session_state.get('v3_seleccionados_por_grupo', {}),
            'proceso_v4': st.session_state.get('v4_seleccionados_por_grupo', {}),
            'proceso_v5': st.session_state.get('v5_seleccionados_por_grupo', {})
        }
        
        timestamp_file = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_usuario_{timestamp_file}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
        return True, f"Backup guardado en {filename}"
    except Exception as e:
        return False, f"Error en backup: {str(e)}"

def mostrar_visualizador():
    """Página principal del visualizador de planos"""
    st.title("Visualizador de Planos")
    
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
            elif version_seleccionada == "v4":
                mostrar_seleccion_v4(df_filtrado)
            elif version_seleccionada == "v5":
                mostrar_seleccion_v5(df_filtrado)
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
    
    # Mostrar el botón finalizar al final de la página
    mostrar_boton_finalizar()

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
        # Mostrar grupo actual (1, 2, o 3)
        st.subheader(f"Grupo {grupo_actual}: Selecciona 1 plano de este grupo")
        st.info(f"Planos del Grupo {grupo_actual}: {len(grupos_planos[grupo_actual])} planos")
        
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
                    if st.button(f"Cambiar Selección", key=f"change_v3_g{grupo_actual}_{plano_id}"):
                        # Eliminar la selección actual
                        if grupo_actual in st.session_state.v3_seleccionados_por_grupo:
                            del st.session_state.v3_seleccionados_por_grupo[grupo_actual]
                        st.rerun()
                else:
                    # Solo permitir seleccionar si no hay otro plano seleccionado en este grupo
                    puede_seleccionar = grupo_actual not in st.session_state.v3_seleccionados_por_grupo
                    
                    if st.button(f"Seleccionar", 
                                key=f"select_v3_g{grupo_actual}_{plano_id}",
                                disabled=not puede_seleccionar):
                        seleccionar_plano_v3(plano_id, datos_plano.to_dict(), grupo_actual)
                        st.rerun()
    
    else:  # grupo_actual == 4 (Ronda final)
        # Mostrar los 3 planos seleccionados
        planos_finalistas = []
        for grupo in [1, 2, 3]:
            if grupo in st.session_state.v3_seleccionados_por_grupo:
                plano_info = st.session_state.v3_seleccionados_por_grupo[grupo]
                planos_finalistas.append(f"Plano {plano_info['plano_id']} (Grupo {grupo})")
        
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
                        st.success("✅ SELECCIONADO")
                    else:
                        if st.button(f"Seleccionar", key=f"select_v3_final_{plano_id}"):
                            seleccionar_plano_v3(plano_id, datos_plano.to_dict(), 4)
                            st.rerun()

def mostrar_seleccion_v4(df_filtrado):
    """Lógica especial para v4 con sistema de grupos"""
    planos_ids = sorted(df_filtrado['Plano_ID'].unique())
    grupo_actual = st.session_state.v4_grupo_actual
    
    # Dividir los 12 planos en 3 grupos de 4
    grupos_planos = {
        1: planos_ids[0:4],   # Planos 1-4
        2: planos_ids[4:8],   # Planos 5-8
        3: planos_ids[8:12]   # Planos 9-12
    }
    
    if grupo_actual <= 3:
        # Mostrar grupo actual (1, 2, o 3)
        st.subheader(f"Grupo {grupo_actual}: Selecciona 1 plano de este grupo")
        
        # Mostrar los 4 planos del grupo actual
        planos_grupo = grupos_planos[grupo_actual]
        cols = st.columns(4)
        
        for i, plano_id in enumerate(planos_grupo):
            datos_plano = df_filtrado[df_filtrado['Plano_ID'] == plano_id].iloc[0]
            
            with cols[i]:
                st.write(f"### Plano {plano_id}")
                
                # Visualizar plano
                titulo = f"Plano {plano_id}"
                fig = visualizar_plano(datos_plano, titulo, "v4")
                if fig:
                    st.pyplot(fig, use_container_width=True)
                
                # Verificar si este plano está seleccionado para este grupo
                plano_seleccionado = st.session_state.v4_seleccionados_por_grupo.get(grupo_actual, {}).get('plano_id')
                is_selected = plano_seleccionado == plano_id
                
                if is_selected:
                    st.success("✅ SELECCIONADO")
                    if st.button(f"Cambiar Selección", key=f"change_v4_g{grupo_actual}_{plano_id}"):
                        # Eliminar la selección actual
                        if grupo_actual in st.session_state.v4_seleccionados_por_grupo:
                            del st.session_state.v4_seleccionados_por_grupo[grupo_actual]
                        st.rerun()
                else:
                    # Solo permitir seleccionar si no hay otro plano seleccionado en este grupo
                    puede_seleccionar = grupo_actual not in st.session_state.v4_seleccionados_por_grupo
                    
                    if st.button(f"Seleccionar", 
                                key=f"select_v4_g{grupo_actual}_{plano_id}",
                                disabled=not puede_seleccionar):
                        seleccionar_plano_v4(plano_id, datos_plano.to_dict(), grupo_actual)
                        st.rerun()
    
    else:  # grupo_actual == 4 (Ronda final)
        # Mostrar los 3 planos finalistas
        cols = st.columns(3)
        
        for i, grupo in enumerate([1, 2, 3]):
            if grupo in st.session_state.v4_seleccionados_por_grupo:
                plano_info = st.session_state.v4_seleccionados_por_grupo[grupo]
                plano_id = plano_info['plano_id']
                datos_plano = df_filtrado[df_filtrado['Plano_ID'] == plano_id].iloc[0]
                
                with cols[i]:
                    st.write(f"### Plano {plano_id}")
                    
                    # Visualizar plano
                    titulo = f"Plano {plano_id}"
                    fig = visualizar_plano(datos_plano, titulo, "v4")
                    if fig:
                        st.pyplot(fig, use_container_width=True)
                    
                    # Verificar si es el ganador final
                    is_winner = ('v4' in st.session_state.planos_seleccionados and 
                               st.session_state.planos_seleccionados['v4']['plano_id'] == plano_id)
                    
                    if is_winner:
                        st.success("✅ SELECCIONADO")
                    else:
                        if st.button(f"Seleccionar", key=f"select_v4_final_{plano_id}"):
                            seleccionar_plano_v4(plano_id, datos_plano.to_dict(), 4)
                            st.rerun()

def mostrar_seleccion_v5(df_filtrado):
    """Lógica especial para v5 con sistema de grupos"""
    planos_ids = sorted(df_filtrado['Plano_ID'].unique())
    grupo_actual = st.session_state.v5_grupo_actual
    
    # Dividir los 24 planos en 6 grupos de 4
    grupos_planos = {
        1: planos_ids[0:4],   # Planos 1-4
        2: planos_ids[4:8],   # Planos 5-8
        3: planos_ids[8:12],  # Planos 9-12
        4: planos_ids[12:16], # Planos 13-16
        5: planos_ids[16:20], # Planos 17-20
        6: planos_ids[20:24]  # Planos 21-24
    }
    
    if grupo_actual <= 6:
        # Mostrar grupo actual (1, 2, 3, 4, 5, o 6)
        st.subheader(f"Grupo {grupo_actual}: Selecciona 1 plano de este grupo")
        
        # Mostrar los 4 planos del grupo actual
        planos_grupo = grupos_planos[grupo_actual]
        cols = st.columns(4)
        
        for i, plano_id in enumerate(planos_grupo):
            datos_plano = df_filtrado[df_filtrado['Plano_ID'] == plano_id].iloc[0]
            
            with cols[i]:
                st.write(f"### Plano {plano_id}")
                
                # Visualizar plano
                titulo = f"Plano {plano_id}"
                fig = visualizar_plano(datos_plano, titulo, "v5")
                if fig:
                    st.pyplot(fig, use_container_width=True)
                
                # Verificar si este plano está seleccionado para este grupo
                plano_seleccionado = st.session_state.v5_seleccionados_por_grupo.get(grupo_actual, {}).get('plano_id')
                is_selected = plano_seleccionado == plano_id
                
                if is_selected:
                    st.success("✅ SELECCIONADO")
                    if st.button(f"Cambiar Selección", key=f"change_v5_g{grupo_actual}_{plano_id}"):
                        # Eliminar la selección actual
                        if grupo_actual in st.session_state.v5_seleccionados_por_grupo:
                            del st.session_state.v5_seleccionados_por_grupo[grupo_actual]
                        st.rerun()
                else:
                    # Solo permitir seleccionar si no hay otro plano seleccionado en este grupo
                    puede_seleccionar = grupo_actual not in st.session_state.v5_seleccionados_por_grupo
                    
                    if st.button(f"Seleccionar", 
                                key=f"select_v5_g{grupo_actual}_{plano_id}",
                                disabled=not puede_seleccionar):
                        seleccionar_plano_v5(plano_id, datos_plano.to_dict(), grupo_actual)
                        st.rerun()
    
    else:  # grupo_actual == 7 (Ronda final)
        # Mostrar los 6 planos finalistas en 2 filas de 3
        for fila in range(2):
            cols = st.columns(3)
            for col in range(3):
                grupo_idx = fila * 3 + col + 1
                if grupo_idx <= 6 and grupo_idx in st.session_state.v5_seleccionados_por_grupo:
                    plano_info = st.session_state.v5_seleccionados_por_grupo[grupo_idx]
                    plano_id = plano_info['plano_id']
                    datos_plano = df_filtrado[df_filtrado['Plano_ID'] == plano_id].iloc[0]
                    
                    with cols[col]:
                        st.write(f"### Plano {plano_id}")
                        
                        # Visualizar plano
                        titulo = f"Plano {plano_id}"
                        fig = visualizar_plano(datos_plano, titulo, "v5")
                        if fig:
                            st.pyplot(fig, use_container_width=True)
                        
                        # Verificar si es el ganador final
                        is_winner = ('v5' in st.session_state.planos_seleccionados and 
                                   st.session_state.planos_seleccionados['v5']['plano_id'] == plano_id)
                        
                        if is_winner:
                            st.success("✅ SELECCIONADO")
                        else:
                            if st.button(f"Seleccionar", key=f"select_v5_final_{plano_id}"):
                                seleccionar_plano_v5(plano_id, datos_plano.to_dict(), 7)
                                st.rerun()

def mostrar_seleccion_normal(df_filtrado, version_seleccionada):
    """Lógica normal para versiones diferentes a v3, v4 y v5"""
    st.subheader(f"Todos los planos de la versión {version_seleccionada}")
    
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
