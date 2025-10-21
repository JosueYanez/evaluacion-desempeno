import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(layout="wide")

# ===========================================================
# CONFIGURACIÓN GOOGLE SHEETS
# ===========================================================
scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

import json
creds_dict = json.loads(st.secrets["general"]["gcp_service_account"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

client = gspread.authorize(creds)

# Abre el archivo y la hoja
spreadsheet = client.open("trabajadores")
hoja = spreadsheet.worksheet("trabajadores")

# Cargar datos de la hoja
datos = hoja.get_all_records()
if not datos:
    st.error("⚠️ La hoja 'trabajadores' está vacía o sin encabezados.")
    st.stop()

trabajadores = pd.DataFrame(datos)

# ===========================================================
# INTERFAZ PRINCIPAL
# ===========================================================
st.title("💼 Sistema de Evaluación del Desempeño")

modo = st.sidebar.radio("Selecciona el modo:", ("RH", "Administrador"))

# ===========================================================
# MODO ADMINISTRADOR
# ===========================================================
if modo == "Administrador":
    st.subheader("Modo Administrador: Información de la Base Maestra")
    st.info("La base maestra se carga automáticamente desde la hoja 'trabajadores'.")
    st.dataframe(trabajadores)

# ===========================================================
# MODO RH: EVALUACIÓN
# ===========================================================
elif modo == "RH":
    st.subheader("Modo Recursos Humanos: Evaluación del Desempeño")

    # Seleccionar trabajador
    lista_nombres = trabajadores["Nombre(s) y Apellidos:"].tolist()
    seleccionado = st.selectbox("Selecciona un trabajador:", lista_nombres)
    trab = trabajadores[trabajadores["Nombre(s) y Apellidos:"] == seleccionado].iloc[0]

    # -------------------------------------------------------
    # DATOS PERSONALES
    # -------------------------------------------------------
    st.subheader("Datos Personales")
    cols = st.columns(2)
    campos = [
        "Nombre(s) y Apellidos:", "C.U.R.P.", "R.F.C.", "Superior Jerárquico:", "Área de Adscripción:",
        "Puesto que desempeña:", "Nivel:", "Fecha del Nombramiento:", "Antigüedad en el Puesto:", "Antigüedad en Gobierno:"
    ]
    etiquetas = [
        "Nombre", "CURP", "RFC", "Superior", "Área", "Puesto", "Nivel",
        "Fecha de Nombramiento", "Antigüedad en Puesto", "Antigüedad en Gobierno"
    ]
    for i, campo in enumerate(campos):
        cols[i % 2].text_input(etiquetas[i], trab[campo], disabled=True)

    # -------------------------------------------------------
    # ACTIVIDADES PRINCIPALES
    # -------------------------------------------------------
    st.subheader("Actividades Principales")
    for i in range(1, 4):
        st.text_input(f"Actividad {i}", trab[f"Principal Funcion {i}"], disabled=True)

    # -------------------------------------------------------
    # METAS REALES
    # -------------------------------------------------------
    st.subheader("Metas Reales Cumplidas")
    meta_real = {}
    resultados = {}
    for i in range(1, 5):
        desc = trab[f"Meta {i} descripción"] or "Sin descripción"
        prog = float(trab[f"Meta {i} prog"] or 0)
        st.markdown(f"**Meta {i}:** {desc} (Programada: {prog})")
        meta_real[f"meta{i}_real"] = st.number_input(f"Cumplimiento real de Meta {i}", min_value=0.0, value=0.0, step=0.1, key=f"meta{i}_real")
        resultados[f"resultado{i}"] = round(meta_real[f"meta{i}_real"] / prog * 100, 2) if prog else 0
        st.write(f"Resultado: {resultados[f'resultado{i}']}%")

    # -------------------------------------------------------
    # FACTORES DE CALIDAD
    # -------------------------------------------------------
    st.subheader("Factores de Calidad")

    descripciones = {
        "CONOCIMIENTO DEL PUESTO": [
            "1️⃣ Posee mínimos conocimientos del puesto que tiene asignado, lo que le impide cumplir con la oportunidad y calidad establecidas.",
            "2️⃣ Posee conocimientos elementales del puesto, lo que provoca deficiencias en la oportunidad y calidad básicas establecidas.",
            "3️⃣ Posee un regular conocimiento del puesto, lo que le permite prestar servicios con oportunidad y calidad básicas.",
            "4️⃣ Posee amplios conocimientos del puesto que tiene asignado, lo que le permite prestar los servicios con oportunidad y calidad requeridas."
        ],
        "CRITERIO": [
            "1️⃣ Propone soluciones irrelevantes a los problemas de trabajo que se le presentan.",
            "2️⃣ Propone soluciones aceptables a los problemas de trabajo que se le presentan.",
            "3️⃣ Propone soluciones adecuadas a los problemas de trabajo que se le presentan.",
            "4️⃣ Propone soluciones óptimas a los problemas de trabajo que se le presentan."
        ],
        "CALIDAD DEL TRABAJO": [
            "1️⃣ Realiza trabajos con alto índice de errores en su confiabilidad, exactitud y presentación.",
            "2️⃣ Realiza trabajos regulares con algunos errores.",
            "3️⃣ Realiza buenos trabajos y excepcionalmente comete errores.",
            "4️⃣ Realiza trabajos excelentes sin errores en su confiabilidad, exactitud y presentación."
        ],
        "TÉCNICA Y ORGANIZACIÓN DEL TRABAJO": [
            "1️⃣ Aplica en grado mínimo las técnicas y organización establecidas.",
            "2️⃣ Aplica ocasionalmente las técnicas establecidas.",
            "3️⃣ Aplica la mayoría de las veces las técnicas establecidas.",
            "4️⃣ Aplica en grado óptimo las técnicas y organización establecidas."
        ],
        "NECESIDAD DE SUPERVISIÓN": [
            "1️⃣ Requiere permanente supervisión para realizar las funciones asignadas.",
            "2️⃣ Requiere ocasional supervisión para realizar las funciones asignadas.",
            "3️⃣ Requiere mínima supervisión para realizar las funciones asignadas.",
            "4️⃣ Requiere nula supervisión para realizar las funciones asignadas."
        ],
        "CAPACITACIÓN RECIBIDA": [
            "1️⃣ Aplica mínimamente los conocimientos adquiridos mediante la capacitación.",
            "2️⃣ Aplica limitadamente los conocimientos adquiridos.",
            "3️⃣ Aplica suficientemente los conocimientos adquiridos, elevando la eficiencia.",
            "4️⃣ Aplica ampliamente los conocimientos adquiridos, elevando la eficiencia al máximo."
        ],
        "INICIATIVA": [
            "1️⃣ Realiza nulas aportaciones para el mejoramiento del trabajo.",
            "2️⃣ Realiza aportaciones irrelevantes para el mejoramiento.",
            "3️⃣ Realiza aportaciones destacadas que mejoran calidad y tiempos.",
            "4️⃣ Realiza aportaciones óptimas y continuas para el mejoramiento."
        ],
        "COLABORACIÓN Y DISCRECIÓN": [
            "1️⃣ Muestra nula disposición para colaborar y provoca conflictos.",
            "2️⃣ Muestra regular disposición y comete indiscreciones involuntarias.",
            "3️⃣ Muestra buena disposición y prudencia en el manejo de información.",
            "4️⃣ Muestra notable disposición y utiliza positivamente la información."
        ],
        "RESPONSABILIDAD Y DISCIPLINA": [
            "1️⃣ Cumple mínimamente con las metas y evade disposiciones.",
            "2️⃣ Cumple ocasionalmente con las metas y objeta disposiciones.",
            "3️⃣ Cumple la mayoría de las veces con las metas y disposiciones.",
            "4️⃣ Cumple invariablemente con metas institucionales y disposiciones."
        ],
        "TRABAJO EN EQUIPO": [
            "1️⃣ Manifiesta nula disposición y entorpece el trabajo del equipo.",
            "2️⃣ Manifiesta regular disposición y ocasionalmente interfiere.",
            "3️⃣ Manifiesta buena disposición, contribuyendo al equipo.",
            "4️⃣ Manifiesta notable disposición, siendo un elemento clave del equipo."
        ],
        "RELACIONES INTERPERSONALES": [
            "1️⃣ Mantiene nulo grado de interacción con jefes, compañeros y público.",
            "2️⃣ Mantiene regular grado de interacción con jefes, compañeros y público.",
            "3️⃣ Mantiene buen grado de interacción con jefes, compañeros y público.",
            "4️⃣ Mantiene excelente grado de interacción con jefes, compañeros y público."
        ],
        "MEJORA CONTINUA": [
            "1️⃣ Demuestra mínimo compromiso para identificar áreas de oportunidad.",
            "2️⃣ Demuestra regular compromiso para proponer mejoras.",
            "3️⃣ Demuestra alto compromiso para identificar y proponer mejoras.",
            "4️⃣ Demuestra amplio compromiso para mejorar continuamente su desempeño."
        ]
    }

    st.markdown("""
        <style>
        .tooltip { position: relative; display: inline-block; cursor: help; color: #2c7be5; font-weight: bold; }
        .tooltip .tooltiptext {
            visibility: hidden; width: 420px; background-color: #f8f9fa; color: #000; text-align: left;
            border-radius: 8px; padding: 10px; position: absolute; z-index: 1;
            top: 125%; left: 50%; transform: translateX(-50%);
            box-shadow: 0px 0px 10px rgba(0,0,0,0.2); font-size: 13px; line-height: 1.4;
        }
        .tooltip:hover .tooltiptext { visibility: visible; }
        </style>
    """, unsafe_allow_html=True)

    calidad = {}
    for factor, niveles in descripciones.items():
        tooltip_html = f"<div class='tooltip'>ⓘ<div class='tooltiptext'><b>{factor}</b><br><br>{'<br>'.join(niveles)}</div></div>"
        st.markdown(f"### {factor} {tooltip_html}", unsafe_allow_html=True)
        calidad[factor] = st.slider("Selecciona nivel", 1, 4, 2, key=f"slider_{factor}")

    puntaje_total = sum(calidad.values())
    st.write(f"**Puntaje total:** {puntaje_total}/48")

    # -------------------------------------------------------
    # FECHA Y COMENTARIOS
    # -------------------------------------------------------
    st.subheader("Fecha y Comentarios")
    hoy = datetime.now()
    dia = st.number_input("Día", min_value=1, max_value=31, value=hoy.day, key="dia_eval")
    mes = st.number_input("Mes", min_value=1, max_value=12, value=hoy.month, key="mes_eval")
    anio = st.number_input("Año", min_value=2000, max_value=hoy.year, value=hoy.year, key="anio_eval")
    comentarios = st.text_area("Comentarios", key="comentarios_eval")

# -------------------------------------------------------
# GUARDAR EVALUACIÓN
# -------------------------------------------------------
if st.button("Guardar Evaluación"):
    # Crear la fila completa
    nueva_fila = [
        trab[c] for c in trabajadores.columns
    ] + [
        dia, mes, anio,
        meta_real["meta1_real"], meta_real["meta2_real"], meta_real["meta3_real"], meta_real["meta4_real"],
        resultados["resultado1"], resultados["resultado2"], resultados["resultado3"], resultados["resultado4"]
    ] + list(calidad.values()) + [puntaje_total, comentarios]

    # 🔹 Conversión segura a string
    nueva_fila = [str(x) for x in nueva_fila]

    # 🔹 Asegurar que la longitud coincide con la hoja
    encabezados = hoja.row_values(1)
    num_columnas = len(encabezados)
    if len(nueva_fila) < num_columnas:
        nueva_fila += [""] * (num_columnas - len(nueva_fila))  # Rellenar vacíos
    elif len(nueva_fila) > num_columnas:
        nueva_fila = nueva_fila[:num_columnas]  # Recortar si sobra

    # 🔹 Agregar fila de manera vertical
    hoja.append_row(nueva_fila)
    st.success("✅ Evaluación guardada correctamente en Google Sheets.")







