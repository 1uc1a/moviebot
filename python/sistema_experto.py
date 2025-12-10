## --- sistema_experto.py --

import os
from pathlib import Path
from pyswip import Prolog
from api_manager import obtener_datos_tmdb
import random

class MovieBot:
    def __init__(self):
        self.prolog = Prolog()
        ruta = Path(__file__).parent.parent / "prolog" / "movies.pl"
        ruta_str = str(ruta).replace("\\", "/")
        try:
            self.prolog.consult(ruta_str)
            print("✅ CEREBRO: Prolog cargado.")
        except Exception as e:
            print(f"❌ Error Prolog: {e}")
        
        self.peliculas_cache = [] 
        self.mapa_generos = {} 

    def clean_text(self, text):
        if not text: return ""
        return text.replace("'", "''").replace('"', '')

    def iniciar(self):
        print("🔄 Inicializando sistema...")
        generos, peliculas = obtener_datos_tmdb()
        if not peliculas: return False

        self.prolog.retractall("genero(_,_)")
        # Limpiamos hechos con 8 argumentos
        self.prolog.retractall("pelicula(_,_,_,_,_,_,_,_)")
        self.mapa_generos = {} 

        for gid, name in generos:
            clean = name.lower().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace(" ", "_")
            if "ciencia_ficcion" in clean: clean = "ciencia_ficcion"
            if "belica" in clean: clean = "guerra"
            self.prolog.assertz(f"genero({gid}, {clean})")
            self.mapa_generos[clean] = gid 

        self.peliculas_cache = []
        for tit, lista_gids, vot, pop, desc, img, dur in peliculas:
            
            # Cache Python
            peli_obj = {
                'tit': tit, 'gids': lista_gids, 'votos': vot, 'pop': pop, 
                'desc': desc, 'img': img, 'dur': dur
            }
            self.peliculas_cache.append(peli_obj)

            # Base Prolog (Ahora pasamos la lista completa de GIDs como ultimo argumento)
            c_tit = self.clean_text(tit)
            c_desc = self.clean_text(desc)
            c_img = self.clean_text(img)
            gid_primario = lista_gids[0] if lista_gids else 0
            
            # Convertimos la lista de Python a string formato Prolog: [12, 35, ...]
            str_gids = str(lista_gids) 

            # HECHO DE 8 ARGUMENTOS
            self.prolog.assertz(f"pelicula('{c_tit}', {gid_primario}, {vot}, {pop}, '{c_desc}', '{c_img}', {dur}, {str_gids})")
        
        print(f"✅ Sistema listo. {len(self.peliculas_cache)} películas en memoria.")
        return True

    def responder_pregunta(self, nivel, opcion):
        self.prolog.assertz(f"respuesta({nivel}, {opcion})")

    def reiniciar_encuesta(self):
        self.prolog.retractall("respuesta(_,_)")

    def decode(self, data):
        if isinstance(data, bytes): return data.decode('utf-8')
        return str(data)

    def dame_nombre_genero(self, gid):
        try:
            q = list(self.prolog.query(f"genero({gid}, N)"))
            if q: return str(q[0]['N']).replace("_", " ").title()
        except: pass
        return "General"

    # --- NUEVA LÓGICA TSP USANDO PROLOG (BLINDADA) ---
    def ordenar_por_tsp(self, peliculas):
        """
        Envía los títulos del TOP 5 a Prolog para que los ordene.
        Incluye protección contra pérdida de datos por caracteres especiales.
        """
        if len(peliculas) <= 1: return peliculas

        # 1. Preparar datos para Prolog
        titulos_input = []
        mapa_obj = {} # Mapa: "TituloLimpio" -> ObjetoPelicula

        for p in peliculas:
            # Limpiamos el título para que Prolog no tire error de sintaxis
            t_clean = self.clean_text(p['tit'])
            # Guardamos en el mapa usando el título LIMPIO como clave
            mapa_obj[t_clean] = p
            # Agregamos a la lista que enviaremos a Prolog
            titulos_input.append(f"'{t_clean}'")
        
        # Creamos el string de la lista: ['Titanic', 'Avatar', ...]
        lista_prolog = "[" + ", ".join(titulos_input) + "]"

        print(f"🧠 Consultando TSP a Prolog con: {lista_prolog}")
        
        lista_ordenada = []

        try:
            # 2. Consultamos optimizar_maraton
            q = list(self.prolog.query(f"optimizar_maraton({lista_prolog}, RutaOrdenada)"))
            
            if q:
                ruta_raw = q[0]['RutaOrdenada']
                
                for atom_titulo in ruta_raw:
                    t_str = self.decode(atom_titulo)
                    # Intentamos recuperar la película del mapa
                    if t_str in mapa_obj:
                        lista_ordenada.append(mapa_obj[t_str])
                    else:
                        print(f"⚠️ Alerta: No se encontró coincidencia exacta para '{t_str}'")
            else:
                print("⚠️ Prolog no encontró ruta, usando orden original.")
                lista_ordenada = list(peliculas)

        except Exception as e:
            print(f"❌ Error en TSP Prolog: {e}")
            lista_ordenada = list(peliculas)

        # =======================================================
        # 🛡️ BLOQUE DE SEGURIDAD (ANTI-DESAPARICIÓN)
        # Si por algún error de caracteres falta alguna película,
        # la agregamos al final para que NUNCA devuelva menos de 5.
        # =======================================================
        if len(lista_ordenada) < len(peliculas):
            print("🔧 Reparando lista (recuperando películas perdidas)...")
            titulos_ya_en_lista = {p['tit'] for p in lista_ordenada}
            
            for p in peliculas:
                if p['tit'] not in titulos_ya_en_lista:
                    lista_ordenada.append(p)
                    print(f"   + Recuperada: {p['tit']}")
        
        return lista_ordenada
    
    # --- MOTOR DE RECOMENDACIÓN ---
    def obtener_top_5_recomendaciones(self):
        try:
            genre_scores = {}
            # 1. Consultar Puntos a Prolog
            try:
                res = list(self.prolog.query("obtener_puntajes_totales(L)"))
                
                if res and res[0]['L']:
                    scores_raw = res[0]['L']
                    print("📊 Puntajes detectados:")
                    
                    for item in scores_raw:
                        puntaje = item[0]
                        nombre_gen = str(item[1])
                        
                        gid = self.mapa_generos.get(nombre_gen)
                        if gid:
                            genre_scores[gid] = puntaje
                            print(f"   - {nombre_gen} ({gid}): {puntaje} pts")
            except Exception as e:
                print(f"⚠️ Error leyendo puntos de Prolog: {e}")

            # 2. Calcular Match
            ranking_peliculas = []
            
            for p in self.peliculas_cache:
                score_peli = 0
                match_found = False
                
                # Sumar puntos si la peli tiene el género
                for g_id in p['gids']:
                    if g_id in genre_scores:
                        score_peli += genre_scores[g_id]
                        match_found = True
                
                try:
                    duracion = p['dur']
                    q_time = list(self.prolog.query(f"puntos_extra_tiempo({duracion}, P)"))
                    if q_time:
                        bonus = q_time[0]['P']
                        score_peli += bonus
                        if bonus > 0: match_found = True
                except: pass
                
                # Desempate por popularidad
                score_peli += (p['pop'] / 10000.0) 

                if match_found:
                    ranking_peliculas.append((score_peli, p))

            # 3. Ordenar
            ranking_peliculas.sort(key=lambda x: x[0], reverse=True)
            
            final_top_5 = []
            titulos_usados = set()
            
            for score, p in ranking_peliculas:
                if p['tit'] not in titulos_usados:
                    p_export = p.copy()
                    p_export['gid'] = p['gids'][0] if p['gids'] else 0 
                    final_top_5.append(p_export)
                    titulos_usados.add(p['tit'])
                    if len(final_top_5) >= 5: break
            
            # 4. Relleno de seguridad
            if len(final_top_5) < 5:
                print("⚠️ Rellenando lista...")
                sorted_pop = sorted(self.peliculas_cache, key=lambda x: x['pop'], reverse=True)
                for p in sorted_pop:
                    if p['tit'] not in titulos_usados:
                        p_export = p.copy()
                        p_export['gid'] = p['gids'][0] if p['gids'] else 0
                        final_top_5.append(p_export)
                        titulos_usados.add(p['tit'])
                    if len(final_top_5) >= 5: break

            return final_top_5

        except Exception as e: 
            print(f"❌ Error crítico recomendación: {e}")
            return [p.copy() for p in self.peliculas_cache[:5]]

    # --- HISTORIAL ---
    def obtener_historial(self):
        historial = []
        try:
            vistos = list(self.prolog.query("visto(Titulo)"))
            for v in vistos:
                raw_title = v.get('Titulo')
                if not raw_title: continue
                titulo_buscado = self.decode(raw_title)
                
                # Buscamos en caché Python (más seguro)
                encontrado = False
                for p in self.peliculas_cache:
                    if p['tit'] == titulo_buscado:
                        p_export = p.copy()
                        p_export['gid'] = p['gids'][0] if p['gids'] else 0
                        historial.append(p_export)
                        encontrado = True
                        break
                
                # Fallback a Prolog (Actualizado para 8 argumentos)
                if not encontrado:
                    clean = self.clean_text(titulo_buscado)
                    # Usamos _ para ignorar argumentos extra
                    q = list(self.prolog.query(f"pelicula('{clean}', G, V, P, D, I, _, _)"))
                    if q:
                        row = q[0]
                        historial.append({
                            'tit': titulo_buscado,
                            'gid': row['G'], 'votos': row['V'], 'pop': row['P'],
                            'desc': self.decode(row['D']), 'img': self.decode(row['I'])
                        })
        except: pass
        return historial

    def obtener_top_global(self):
        try:
            sorted_votos = sorted(self.peliculas_cache, key=lambda x: x['votos'], reverse=True)
            top = []
            for p in sorted_votos[:10]:
                p_ex = p.copy()
                p_ex['gid'] = p['gids'][0] if p['gids'] else 0
                top.append(p_ex)
            return top
        except: return []

    def guardar_review(self, peli, stars, comm):
        c_peli = self.clean_text(peli)
        c_comm = self.clean_text(comm)
        self.prolog.assertz(f"review('{c_peli}', 'Antonio', {stars}, '{c_comm}')")

    def leer_reviews_usuario(self):
        lista = []
        try:
            q = list(self.prolog.query("review(P, U, S, C)"))
            for r in q:
                lista.append({
                    "peli": self.decode(r["P"]), "user": self.decode(r["U"]),
                    "stars": r["S"], "comentario": self.decode(r["C"])
                })
        except: pass
        return lista
    
    def marcar_como_vista(self, peli):
        c_peli = self.clean_text(peli)
        if not list(self.prolog.query(f"visto('{c_peli}')")):
            self.prolog.assertz(f"visto('{c_peli}')")
            print(f"👁️ Visto guardado: {c_peli}")