### --- app_alegre.py --

import flet as ft
from sistema_experto import MovieBot
import traceback

bot = MovieBot()

def main(page: ft.Page):
    page.title = "MovieBot Pro Fixed v2"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#111111"
    page.padding = 0
    page.window_width = 1100
    page.window_height = 900

    NEON_CYAN = "#00E5FF" 
    NEON_PINK = "#FF4081"
    NEON_YELLOW = "#FFD600"
    CARD_BG = "#1F1F1F"

    # Estado global
    estado = {"paso": 1}

    print("⏳ Iniciando aplicación...")
    try: bot.iniciar()
    except: pass

    contenido_principal = ft.Container(expand=True)

    # --- NAVEGACIÓN INTELIGENTE ---
    def cambiar_vista(vista):
        contenido_principal.content = None
        
        if vista == "home":
            mostrar_bienvenida()
        elif vista == "test":
            # Si el test ya empezó, lo resumimos. Si no, empieza de 0.
            if estado["paso"] > 1: resumir_cuestionario()
            else: iniciar_cuestionario()
        elif vista == "reviews": 
            mostrar_muro_reviews()
        elif vista == "historial": 
            mostrar_historial()
        elif vista == "top": 
            mostrar_top_global()
        
        page.update()

    def resumir_cuestionario():
        if estado["paso"] > 6: mostrar_lista_resultados()
        else: mostrar_paso_actual()

    def reiniciar_totalmente():
        bot.reiniciar_encuesta()
        estado["paso"] = 1
        mostrar_paso_actual()

    # =========================================
    #  NUEVA PANTALLA: BIENVENIDA (HOME) 🏠
    # =========================================
    def mostrar_bienvenida():
        contenido_principal.content = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.MOVIE_FILTER, size=100, color=NEON_PINK),
                ft.Text("¡Bienvenido, Antonio! 👋", size=45, weight="black", color="white"),
                ft.Container(height=10),
                ft.Text(
                    "Soy tu asistente experto en cine. Utilizo Inteligencia Artificial\n"
                    "y una base de datos en tiempo real para encontrar tu película ideal.",
                    size=18, color="grey", text_align="center"
                ),
                ft.Container(height=40),
                
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
        page.update()

    # --- PANTALLAS ---
    def mostrar_historial():
        historial = bot.obtener_historial()
        lista_items = [ft.Text("Tu Historial de Vistas 👁️", size=30, weight="bold", color=NEON_CYAN), ft.Divider(color="grey")]
        if not historial: lista_items.append(ft.Text("Aún no has marcado películas como vistas.", color="grey"))
        for p in historial: lista_items.append(crear_tarjeta_lista(p))
        contenido_principal.content = ft.Container(content=ft.ListView(lista_items, expand=True, spacing=15, padding=30), padding=0)
        page.update()

    def mostrar_maraton():
        peliculas_top = bot.obtener_top_5_recomendaciones()
        peliculas_ordenadas = bot.ordenar_por_tsp(peliculas_top)

        header = ft.Column([
            ft.Text("🎬 Modo Maratón – Orden Óptimo", size=35, weight="black", color=NEON_CYAN),
            ft.Text("Ordenadas usando Problema del Viajante", color="grey"),
            ft.Divider(color="grey")
        ])

        lista = []
        for i, p in enumerate(peliculas_ordenadas):
            lista.append(crear_tarjeta_lista(p, ranking=i+1, color_rank=NEON_PINK))

        btn_volver = ft.ElevatedButton(
            "Volver al Top 5",
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda e: mostrar_lista_resultados()
        )

        contenido_principal.content = ft.Container(
            content=ft.Column([header] + lista + [btn_volver], scroll=ft.ScrollMode.AUTO),
            padding=40
        )
        page.update()

    def mostrar_top_global():
        top = bot.obtener_top_global()
        lista_items = [ft.Text("🏆 Top 10 Global", size=30, weight="bold", color=NEON_YELLOW), ft.Divider(color="grey")]
        for i, p in enumerate(top): lista_items.append(crear_tarjeta_lista(p, ranking=i+1, color_rank=NEON_YELLOW))
        contenido_principal.content = ft.Container(content=ft.ListView(lista_items, expand=True, spacing=15, padding=30), padding=0)
        page.update()

    def mostrar_muro_reviews():
        data = bot.leer_reviews_usuario()
        lista_items = [ft.Text("Muro de la Comunidad 💬", size=30, weight="bold", color="white")]
        if not data: lista_items.append(ft.Text("Sin reviews aún.", color="grey"))
        for r in data:
            stars = ft.Row([ft.Icon(ft.Icons.STAR, color="amber", size=16) for _ in range(r['stars'])])
            card = ft.Container(content=ft.Column([ft.Row([ft.CircleAvatar(content=ft.Text(r['user'][:1].upper()), bgcolor=NEON_PINK), ft.Text(r['user'], weight="bold"), ft.Text(f"vio {r['peli']}", color="grey", italic=True), ft.Container(expand=True), stars]), ft.Text(f'"{r["comentario"]}"', size=16)]), padding=20, bgcolor=CARD_BG, border_radius=10)
            lista_items.append(card)
        contenido_principal.content = ft.Container(content=ft.ListView(lista_items, expand=True, spacing=15, padding=30), padding=0)
        page.update()

    def crear_tarjeta_lista(p, ranking=None, color_rank=NEON_PINK):
        tit = p['tit']
        lead = ft.Text(f"#{ranking}", size=40, weight="bold", color=color_rank) if ranking else ft.Icon(ft.Icons.CHECK_CIRCLE, color="green", size=30)
        def click_card(e): ver_detalle(p)
        return ft.Container(content=ft.Row([lead, ft.Image(src=p['img'], width=60, height=90, border_radius=5, fit=ft.ImageFit.COVER), ft.Column([ft.Text(tit, size=20, weight="bold"), ft.Row([ft.Icon(ft.Icons.STAR, color="amber", size=14), ft.Text(f"{p['votos']}/10", size=12, color="grey")])]), ft.Container(expand=True), ft.ElevatedButton("Ver Ficha ➤", color="black", bgcolor="white", on_click=click_card)], alignment=ft.MainAxisAlignment.CENTER), bgcolor=CARD_BG, padding=15, border_radius=10, ink=True, on_click=click_card)

    def ver_detalle(peli_data):
        try:
            titulo = peli_data['tit']
            desc = peli_data.get('desc', 'Sin descripción.')
            img_url = peli_data.get('img', 'https://via.placeholder.com/300')
            votos = peli_data.get('votos', 0)
            duracion = peli_data.get('dur', 0)
            
            # --- CAMBIO: Obtener LISTA de géneros ---
            lista_ids = peli_data.get('gids', [])
            # Si la lista está vacía, intentamos usar el gid único
            if not lista_ids and 'gid' in peli_data: 
                lista_ids = [peli_data['gid']]
                
            # Convertimos IDs a Nombres
            nombres_generos = [bot.dame_nombre_genero(x) for x in lista_ids]
            # ----------------------------------------

            slider = ft.Slider(min=1, max=5, divisions=4, label="{value} ⭐", active_color="amber")
            txt = ft.TextField(hint_text="Tu reseña...", bgcolor="#222")

            def guardar(e):
                bot.guardar_review(titulo, int(slider.value), txt.value)
                page.snack_bar = ft.SnackBar(ft.Text("¡Guardado!"))
                page.snack_bar.open = True
                page.update()

            panel = ft.Container(content=ft.Column([ft.Divider(), ft.Text("Calificar:", color="amber"), slider, txt, ft.ElevatedButton("Publicar", bgcolor=NEON_CYAN, color="black", on_click=guardar)]), visible=False)
            lbl = ft.Text("No vista", color="grey")

            def toggle(e):
                if e.control.value:
                    bot.marcar_como_vista(titulo)
                    lbl.value = "✅ VISTA"; lbl.color = "green"; panel.visible = True
                else:
                    lbl.value = "No vista"; lbl.color = "grey"; panel.visible = False
                page.update()

            switch = ft.Switch(active_color="green", on_change=toggle)

            # --- CONSTRUCCIÓN DE ETIQUETAS DINÁMICAS ---
            # 1. Creamos las etiquetas de géneros
            lista_controles = []
            for nom in nombres_generos:
                chip = ft.Container(
                    content=ft.Text(str(nom).upper(), size=12, weight="bold"), 
                    bgcolor=NEON_PINK, 
                    padding=10, 
                    border_radius=5
                )
                lista_controles.append(chip)
            
            # 2. Agregamos Votos
            lista_controles.append(
                ft.Container(content=ft.Row([ft.Icon(ft.Icons.STAR, color="yellow"), ft.Text(f"{votos}/10")]), bgcolor="#333", padding=10, border_radius=5)
            )
            
            # 3. Agregamos Duración
            lista_controles.append(
                ft.Container(content=ft.Row([ft.Icon(ft.Icons.ACCESS_TIME_FILLED, color=NEON_CYAN, size=16), ft.Text(f"{duracion} min", weight="bold")]), bgcolor="#333", padding=10, border_radius=5)
            )
            # -------------------------------------------

            contenido_principal.content = ft.Column([
                ft.Container(content=ft.TextButton("Volver", icon=ft.Icons.ARROW_BACK, icon_color="white", style=ft.ButtonStyle(color="white"), on_click=lambda e: mostrar_lista_resultados()), padding=20),
                ft.Container(content=ft.Row([
                    ft.Container(content=ft.Image(src=img_url, width=350, height=520, fit=ft.ImageFit.COVER, border_radius=20), shadow=ft.BoxShadow(blur_radius=50, color="black"), border_radius=20),
                    ft.Container(content=ft.Column([
                        ft.Text(titulo, size=45, weight="black"),
                        
                        # Usamos la lista dinámica y activamos WRAP para que baje de línea si hay muchos
                        ft.Row(controls=lista_controles, wrap=True),

                        ft.Container(height=20), ft.Text("SINOPSIS", color="grey", weight="bold"), ft.Text(desc, size=16, color="#DDDDDD", selectable=True),
                        ft.Container(height=30), ft.Divider(),
                        ft.Row([ft.Icon(ft.Icons.VISIBILITY), ft.Text("¿Ya la viste?", size=18, weight="bold"), switch, lbl]),
                        panel
                    ], scroll=ft.ScrollMode.AUTO), expand=True, padding=ft.padding.only(left=30))
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START), padding=40, expand=True)
            ], expand=True)
            page.update()
        except: traceback.print_exc()


    def mostrar_lista_resultados():
        peliculas_data = bot.obtener_top_5_recomendaciones()
        header = ft.Column([ft.Text("Tus Resultados", size=35, weight="black", color=NEON_CYAN), ft.Divider(color="grey")])
        lista = []
        if not peliculas_data: lista.append(ft.Text("Sin resultados.", color="red"))
        for i, p in enumerate(peliculas_data): lista.append(crear_tarjeta_lista(p, ranking=i+1))
        btn_maraton = ft.Container(
            content=ft.ElevatedButton(
                "Maratón 🎬",
                bgcolor=NEON_CYAN,
                color="black",
                on_click=lambda e: mostrar_maraton()
            ),
            padding=10
        )

        btn_reiniciar = ft.Container(
            content=ft.ElevatedButton(
                "Reiniciar",
                icon=ft.Icons.REFRESH,
                on_click=lambda e: reiniciar_totalmente()
            ),
            padding=10
        )

        contenido_principal.content = ft.Container(
            content=ft.Column([header] + lista + [btn_maraton, btn_reiniciar], scroll=ft.ScrollMode.AUTO),
            padding=40
        )
        contenido_principal.content = ft.Container(content=ft.Column([header] + lista + [btn_maraton, btn_reiniciar], scroll=ft.ScrollMode.AUTO), padding=40)
        page.update()

    def procesar_respuesta(nivel, key):
        bot.responder_pregunta(nivel, key); estado["paso"] += 1; mostrar_paso_actual()

    def mostrar_paso_actual():
        p = estado["paso"]
        if p == 1: preg(1, "¿Con quién estás ahora?", [("Amigos 🎉", "opcion_1"), ("Cita ❤️", "opcion_2"), ("Familia 👨‍👩‍👧‍👦", "opcion_3"), ("Solo y bien🦸", "opcion_4"), ("Solo y depre 🌧️", "opcion_5")], NEON_CYAN)
        elif p == 2: preg(2, "¿Mood?", [("Energía ⚡", "opcion_1"), ("Risas 😂", "opcion_2"), ("Sustos 😱", "opcion_3"), ("Pensar 🧠", "opcion_4"), ("Relax 🥰", "opcion_5")], NEON_PINK)
        elif p == 3: preg(3, "Generalmente, ¿qué estilo te representa?", [("Frenético ⏩", "opcion_1"), ("Drama 🐢", "opcion_2"), ("Magia ✨", "opcion_3"), ("Suspenso 🕵️", "opcion_4"), ("Musical 🎵", "opcion_5")], "orange")
        elif p == 4: preg(4, "¿Para que estás? Algo...", [("Futurista 🤖", "opcion_1"), ("Histórico 🏛️", "opcion_2"), ("Policial 🚔", "opcion_3"), ("Fantasioso 🐉", "opcion_4"), ("Bélico ⚔️", "opcion_5")], "blue")
        elif p == 5: preg(5, "¿Qué tiene que pasar si o si?", [("Explosiones 💥", "opcion_1"), ("Besos 💋", "opcion_2"), ("Plot Twist🌀", "opcion_3"), ("Chistes 🤡", "opcion_4"), ("Sangre 🩸", "opcion_5")], "purple")
        elif p == 6: preg(6, "¿Cuánto tiempo tenés hoy?", [("Poco (Cortometraje/Flash) ⚡", "opcion_1"), ("Normal (90-120 min) 🍿", "opcion_2"), ("Tengo toda la noche (+2h) 🛋️", "opcion_3")], NEON_YELLOW)
        else: mostrar_lista_resultados()

    def preg(nivel, txt, opts, col):
        btns = [ft.Container(content=ft.ElevatedButton(text=t, style=ft.ButtonStyle(bgcolor=CARD_BG, color="white"), width=500, height=60, on_click=lambda e, k=k: procesar_respuesta(nivel, k)), padding=5) for t, k in opts]
        contenido_principal.content = ft.Container(content=ft.Column([ft.Text(f"NIVEL {nivel}/6", color=col, weight="bold"), ft.ProgressBar(value=nivel/6, color=col, bgcolor="#333"), ft.Container(height=30), ft.Text(txt, size=30, weight="black"), ft.Container(height=30), ft.Column(btns, spacing=10, horizontal_alignment="center")], horizontal_alignment="center", scroll=ft.ScrollMode.AUTO), alignment=ft.alignment.center)
        page.update()

    def iniciar_cuestionario():
        bot.reiniciar_encuesta(); estado["paso"] = 1; mostrar_paso_actual()

    # --- SIDEBAR MEJORADO ---
    sidebar = ft.Container(content=ft.Column([
        # 1. Perfil
        ft.Container(content=ft.Row([ft.CircleAvatar(content=ft.Text("AR"), bgcolor=NEON_PINK), ft.Text("Antonio", weight="bold")]), padding=20),
        ft.Divider(color="grey"),
        
        # 2. Botón Home
        ft.Container(content=ft.Row([ft.Icon(ft.Icons.HOME, color="white"), ft.Text("Inicio", color="white")]), padding=15, ink=True, on_click=lambda e: cambiar_vista("home")),
        
        # 3. Botón Test
        ft.Container(content=ft.Row([ft.Icon(ft.Icons.PLAY_ARROW, color="grey"), ft.Text("Test", color="white")]), padding=15, ink=True, on_click=lambda e: cambiar_vista("test")),
        
        # 4. Extras
        ft.Container(content=ft.Row([ft.Icon(ft.Icons.HISTORY, color="grey"), ft.Text("Historial", color="white")]), padding=15, ink=True, on_click=lambda e: cambiar_vista("historial")),
        ft.Container(content=ft.Row([ft.Icon(ft.Icons.STAR, color="yellow"), ft.Text("Top Global", color="white")]), padding=15, ink=True, on_click=lambda e: cambiar_vista("top")),
        ft.Container(content=ft.Row([ft.Icon(ft.Icons.FORUM, color="grey"), ft.Text("Muro", color="white")]), padding=15, ink=True, on_click=lambda e: cambiar_vista("reviews"))
    ]), padding=30, bgcolor="#161616", width=250)

    page.add(ft.Row([sidebar, contenido_principal], expand=True))
    
    # --- ARRANQUE: MOSTRAR BIENVENIDA DIRECTO ---
    mostrar_bienvenida()

ft.app(target=main, port=8080)