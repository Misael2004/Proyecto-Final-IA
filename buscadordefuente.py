from serpapi import GoogleSearch
import openai
import requests
from bs4 import BeautifulSoup

# CLAVES API
serpapi_key = "7eecbebda96575f2199941b6372c52f9d38ba7f05fa8f4e4bb1be18c379662f1"
openai.api_key = "7eecbebda96575f2199941b6372c52f9d38ba7f05fa8f4e4bb1be18c379662f1face"

def buscar_con_serpapi(consulta, max_resultados=3):
    params = {
        "engine": "google",
        "q": consulta,
        "num": max_resultados,
        "api_key": serpapi_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    enlaces = []

    for resultado in results.get("organic_results", []):
        link = resultado.get("link")
        if link:
            enlaces.append(link)

    return enlaces

def extraer_contenido_de_url(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        parrafos = soup.find_all('p')
        texto = "\n".join(p.get_text() for p in parrafos if len(p.get_text()) > 50)
        return texto[:3000]  # Limitar a 3000 caracteres para ChatGPT
    except Exception as e:
        return f"Error accediendo a {url}: {e}"

def procesar_con_chatgpt(texto, pregunta="Resume el siguiente contenido:"):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en análisis de texto."},
                {"role": "user", "content": f"{pregunta}\n\n{texto}"}
            ]
        )
        return respuesta["choices"][0]["message"]["content"]
    except Exception as e:
        return f": {e}"

def main():
    consulta = input("🔎 ¿Qué quieres buscar?: ")
    enlaces = buscar_con_serpapi(consulta)

    if not enlaces:
        print("No se encontraron resultados.")
        return

    for i, url in enumerate(enlaces, 1):
        print(f"\n🔗 Enlace #{i}: {url}")
        contenido = extraer_contenido_de_url(url)
        if "Error" in contenido:
            print(contenido)
            continue

        print("Buscando...")
        resultado = procesar_con_chatgpt(contenido)
        print(f"\nAqui estan tus resultados:\n{resultado}\n")

if __name__ == "__main__":
    main()
