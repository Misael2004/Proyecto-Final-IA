import streamlit as st
import openai
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
SERPAPI_KEY = "7eecbebda96575f2199941b6372c52f9d38ba7f05fa8f4e4bb1be18c379662f1"
OPENAI_KEY = "7eecbebda96575f2199941b6372c52f9d38ba7f05fa8f4e4bb1be18c379662f1"
openai.api_key = OPENAI_KEY

# --- FUNCIONES ---
def buscar_fuentes(texto, max_resultados=3):
    params = {
        "engine": "google",
        "q": texto,
        "num": max_resultados,
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return [r["link"] for r in results.get("organic_results", []) if "link" in r]

def extraer_texto_de_url(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        parrafos = soup.find_all('p')
        texto = "\n".join(p.get_text() for p in parrafos if len(p.get_text()) > 50)
        return texto[:3000]
    except Exception as e:
        return f"[ERROR] {e}"

def generar_informe(texto_original, fuentes_texto):
    prompt = f"""
Texto a verificar:

\"\"\"{texto_original}\"\"\"

Fuentes encontradas:

\"\"\"{fuentes_texto}\"\"\"

¿Es verdadero o falso? Justifica con base en las fuentes.
"""
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un verificador de hechos."},
                {"role": "user", "content": prompt}
            ]
        )
        return respuesta['choices'][0]['message']['content']
    except Exception as e:
        return f"[ERROR ChatGPT] {e}"

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Buscador y Verificador de Fuentes", layout="centered")
st.title("🔍 Buscador y Verificador de Fuentes")

texto = st.text_area("Ingresa un texto o afirmación para verificar su veracidad:", height=200)

if st.button("Verificar"):
    if not texto.strip():
        st.warning("Por favor, ingresa un texto.")
    else:
        with st.spinner("Buscando fuentes en la web..."):
            enlaces = buscar_fuentes(texto)
        
        if not enlaces:
            st.error("No se encontraron fuentes.")
        else:
            fuentes_texto = ""
            for i, url in enumerate(enlaces, 1):
                st.markdown(f"🔗 **Fuente #{i}:** {url}")
                contenido = extraer_texto_de_url(url)
                if "[ERROR]" not in contenido:
                    fuentes_texto += f"\n--- Fuente #{i} ---\n{contenido}\n"

            with st.spinner("Analizando veracidad con IA..."):
                informe = generar_informe(texto, fuentes_texto)

            st.subheader("📋 Informe de Veracidad")
            st.write(informe)

            st.markdown("---")
            st.subheader("🔗 Enlaces usados")
            for url in enlaces:
                st.markdown(f"- {url}")
