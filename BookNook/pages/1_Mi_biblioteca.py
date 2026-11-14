import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Mi Biblioteca | BookNook", page_icon="📚", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    .stApp { background: radial-gradient(circle at top, #FBF7F2 0%, #F3EAE0 60%, #EADBC8 100%); color: #4A332D; font-family: 'Plus Jakarta Sans', sans-serif; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #4A332D 0%, #36221C 100%) !important; border-right: 3px solid #B5838D; }
    section[data-testid="stSidebar"] * { color: #FBF7F2 !important; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #4A332D !important; }
    .book-card {
        background: #FFFDF9;
        border: 1.5px solid #E2D0BE;
        border-top: 4px solid #B5838D;
        border-radius: 20px;
        padding: 18px;
        box-shadow: 0 8px 20px rgba(74, 51, 45, 0.06);
        margin-bottom: 16px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #B5838D 0%, #8E5B66 100%) !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        border: 1px solid #D4AF37 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 Mi Biblioteca & Reto del Año")
st.markdown("*Subes cada libro con su nombre o una foto de la portada, y la app lleva la cuenta: minutos, libros leídos y tu reto del año.*")

if not os.path.exists("data/libros.csv"):
    st.warning("Ve primero a la página de Inicio para inicializar tu base de datos.")
    st.stop()

df_libros = pd.read_csv("data/libros.csv")
df_sesiones = pd.read_csv("data/sesiones.csv")

# --- BARRA DE PROGRESO DEL RETO ANUAL (RF11 y CU6) ---
leidos_total = len(df_libros[df_libros["estante"] == "Leídos"])
minutos_totales = int(df_sesiones["minutos"].sum())

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("📖 Reto Anual 2026", f"{leidos_total} de 12 libros", "+1 este mes")
    st.progress(min(leidos_total / 12, 1.0))
with m2:
    st.metric("⏱️ Minutos Totales Leídos", f"{minutos_totales} min", "Meta diaria: 30 min")
with m3:
    est_perilla = st.session_state.get('estrellas_perilla', 5)
    st.metric("🎛️ Calificación en Perilla Wokwi", "⭐" * int(est_perilla), f"{est_perilla} estrellas")

st.write("---")

# --- CU1 y RF1: AGREGAR UN LIBRO CON FOTO DE PORTADA ---
with st.expander("➕ Subir nuevo libro o portada (Caso de Uso CU1 - Ej: María de Jorge Isaacs)", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        titulo = st.text_input("Nombre del libro", placeholder="Ej: María")
        autor = st.text_input("Autor(a)", placeholder="Ej: Jorge Isaacs")
        genero = st.selectbox("Género literario", ["Romance", "Ciencia ficción", "Misterio y terror", "Fantasía"])
    with col_b:
        estante = st.selectbox("Estante (RF2)", ["Leyendo", "Quiero leer", "Leídos"])
        estrellas = st.slider("Calificación (o usa la perilla física de Wokwi)", 1, 5, int(st.session_state.get('estrellas_perilla', 5)))
        foto_portada = st.file_uploader("Subir foto de la portada (opcional)", type=["png", "jpg", "jpeg"])
    
    if st.button("🌸 Guardar libro en Mi Biblioteca"):
        if titulo:
            os.makedirs("data/portadas", exist_ok=True)
            ruta_img = "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"
            if foto_portada is not None:
                ruta_local = f"data/portadas/{foto_portada.name}"
                with open(ruta_local, "wb") as f:
                    f.write(foto_portada.getbuffer())
                ruta_img = ruta_local
            
            nuevo_df = pd.DataFrame([{
                "titulo": titulo, "autor": autor or "Autor clásico", "genero": genero,
                "estante": estante, "estrellas": estrellas, "portada": ruta_img
            }])
            df_libros = pd.concat([nuevo_df, df_libros], ignore_index=True)
            df_libros.to_csv("data/libros.csv", index=False)
            st.success(f"✨ ¡'{titulo}' agregado al estante '{estante}'!")
            st.rerun()

# --- RF2: ORGANIZAR EN ESTANTES (LEYENDO, QUIERO LEER, LEÍDOS) ---
tab1, tab2, tab3, tab4 = st.tabs(["📖 Leyendo ahora", "✅ Leídos (Reto 2026)", "💭 Quiero leer", "📊 Gráficas de Hábito"])

def mostrar_estante(df_filtrado, clave_tab):
    cols = st.columns(3)
    for i, (_, row) in enumerate(df_filtrado.iterrows()):
        with cols[i % 3]:
            estrellas_str = "⭐" * int(row["estrellas"])
            st.markdown(f"""
            <div class="book-card">
                <span style="background:#F3EAE0; color:#B5838D; padding:4px 12px; border-radius:15px; font-size:0.78rem; font-weight:700;">
                    {row['genero']} · {row['estante']}
                </span>
                <h3 style="margin-top:10px; margin-bottom:2px;">{row['titulo']}</h3>
                <p style="color:#7A5C52; font-size:0.88rem; margin-bottom:8px;">{row['autor']}</p>
                <div style="margin-bottom:10px;">{estrellas_str}</div>
            </div>
            """, unsafe_allow_html=True)
            if str(row["portada"]).startswith("http"):
                st.image(row["portada"], use_container_width=True)
            elif os.path.exists(str(row["portada"])):
                st.image(str(row["portada"]), use_container_width=True)
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button(f"📟 Enviar al LCD", key=f"lcd_{clave_tab}_{i}"):
                    st.session_state['libro_actual'] = row['titulo']
                    if 'mqtt_client' in st.session_state:
                        st.session_state['mqtt_client'].publish("booknook/app", json.dumps({"libro": row['titulo'][:15]}))
                    st.toast(f"LCD Wokwi ahora muestra: {row['titulo']}")
            with c_btn2:
                if row["estante"] != "Leídos":
                    if st.button(f"🏆 Terminar (CU5)", key=f"fin_{clave_tab}_{i}"):
                        df_libros.loc[df_libros["titulo"] == row["titulo"], "estante"] = "Leídos"
                        df_libros.loc[df_libros["titulo"] == row["titulo"], "estrellas"] = int(st.session_state.get('estrellas_perilla', 5))
                        df_libros.to_csv("data/libros.csv", index=False)
                        st.balloons()
                        st.rerun()

with tab1:
    mostrar_estante(df_libros[df_libros["estante"] == "Leyendo"], "ley")
with tab2:
    mostrar_estante(df_libros[df_libros["estante"] == "Leídos"], "lei")
with tab3:
    mostrar_estante(df_libros[df_libros["estante"] == "Quiero leer"], "qui")
with tab4:
    st.subheader("📈 Tus minutos de lectura por día (Plotly)")
    fig = px.bar(
        df_sesiones, x="fecha", y="minutos", color="libro",
        color_discrete_sequence=["#B5838D", "#6D4C41", "#D4AF37"],
        labels={"fecha": "Día", "minutos": "Minutos leídos"}
    )
    fig.add_hline(y=30, line_dash="dash", line_color="#4A332D", annotation_text="Meta diaria (30 min)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
