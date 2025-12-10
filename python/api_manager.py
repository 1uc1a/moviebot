## -- api_manager.py --

import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = "94f268df688ab16cc47bd74d1e5a2061" 
IDIOMA = "es-ES"
IMG_BASE_URL = "https://image.tmdb.org/t/p/w400"

def obtener_datos_tmdb():
    print(f"📡 API: Conectando a TMDB...")
    datos_generos = []
    datos_peliculas = []

    # 1. Traer Géneros
    try:
        url_gen = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language={IDIOMA}"
        resp = requests.get(url_gen)
        if resp.status_code == 200:
            for g in resp.json()['genres']:
                datos_generos.append((g['id'], g['name']))
    except Exception as e:
        print(f"❌ Error API Géneros: {e}")

    # 2. Traer Películas 
    print("📡 API: Descargando catálogo...")
    try:
        # Buscamos en las primeras 11 páginas (~200 películas)
        for page in range(1, 11): 
            url_mov = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language={IDIOMA}&page={page}"
            resp = requests.get(url_mov)
            if resp.status_code == 200:
                raw_movies = resp.json()['results']
                for p in raw_movies:
                    titulo = p.get('title', 'Sin título')
                    
                    # Guardamos TODOS los géneros
                    lista_generos = p.get('genre_ids', [])
                    if not lista_generos: lista_generos = [0]
                    
                    votos = str(p.get('vote_average', 0))
                    pop = int(p.get('popularity', 0))
                    overview = p.get('overview', 'Sin descripción.')
                    
                    poster_path = p.get('poster_path')
                    full_img_url = IMG_BASE_URL + poster_path if poster_path else "https://via.placeholder.com/300x450?text=No+Image"

                    p_id = p.get('id')
                    try:
                        # Hacemos una llamada extra para obtener la duración exacta
                        url_det = f"https://api.themoviedb.org/3/movie/{p_id}?api_key={API_KEY}&language={IDIOMA}"
                        r_det = requests.get(url_det)
                        duracion = 0
                        if r_det.status_code == 200:
                            duracion = r_det.json().get('runtime', 0)
                        if not duracion: duracion = 90 # Default por si falla
                    except:
                        duracion = 90

                    datos_peliculas.append((titulo, lista_generos, votos, pop, overview, full_img_url, duracion))

    except Exception as e:
        print(f"❌ Error conexión Películas: {e}")

    print(f"✅ API: {len(datos_peliculas)} películas listas para analizar.")
    return datos_generos, datos_peliculas