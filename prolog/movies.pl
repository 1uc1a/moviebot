% --- movies.pl ---

% HECHOS DINÁMICOS
:- dynamic pelicula/8.      % pelicula(Titulo, IdGen, Votos, Pop, Desc, Img, Dur, ListaGids).
:- dynamic genero/2.        % genero(Id, Nombre).
:- dynamic respuesta/2.     % respuesta(Nivel, Opcion).
:- dynamic review/4.        % review(Peli, User, Stars, Comment).
:- dynamic visto/1.         % visto(Titulo).

% REVIEWS BASE
review('Gladiator II', 'Maximus', 5, 'Sangre y honor.').
review('Wicked', 'Ana', 5, 'Musica hermosa y vestuario genial.').
review('Moana 2', 'DisneyFan', 4, 'Buena animacion, pero prefiero la 1.').
review('The Batman', 'DarkKnight', 5, 'Muy oscura y realista.').
review('Superbad', 'McLovin', 4, 'Me rei demasiado.').

% --- SISTEMA DE PUNTAJES (ACUMULATIVO) ---

% NIVEL 1: SITUACIÓN (20 pts)
puntos(accion, 20)    :- respuesta(1, opcion_1).
puntos(comedia, 20)   :- respuesta(1, opcion_1).
puntos(romance, 20)   :- respuesta(1, opcion_2).
puntos(drama, 10)     :- respuesta(1, opcion_2).
puntos(familia, 20)   :- respuesta(1, opcion_3).
puntos(animacion, 20) :- respuesta(1, opcion_3).
puntos(terror, 20)    :- respuesta(1, opcion_4).
puntos(misterio, 20)  :- respuesta(1, opcion_4).
puntos(drama, 20)     :- respuesta(1, opcion_5).

% NIVEL 2: MOOD (10 pts)
puntos(accion, 10)          :- respuesta(2, opcion_1).
puntos(aventura, 10)        :- respuesta(2, opcion_1).
puntos(comedia, 10)         :- respuesta(2, opcion_2).
puntos(terror, 10)          :- respuesta(2, opcion_3).
puntos(ciencia_ficcion, 10) :- respuesta(2, opcion_4).
puntos(romance, 10)         :- respuesta(2, opcion_5).

% NIVEL 3: RITMO (10 pts)
puntos(accion, 10)    :- respuesta(3, opcion_1).
puntos(crimen, 10)    :- respuesta(3, opcion_1).
puntos(drama, 10)     :- respuesta(3, opcion_2).
puntos(fantasia, 10)  :- respuesta(3, opcion_3).
puntos(misterio, 10)  :- respuesta(3, opcion_4).
puntos(musical, 20)   :- respuesta(3, opcion_5).

% NIVEL 4: AMBIENTACIÓN (30 pts)
puntos(ciencia_ficcion, 30) :- respuesta(4, opcion_1).
puntos(historia, 30)        :- respuesta(4, opcion_2).
puntos(guerra, 30)          :- respuesta(4, opcion_2).
puntos(crimen, 30)          :- respuesta(4, opcion_3).
puntos(fantasia, 30)        :- respuesta(4, opcion_4).
puntos(guerra, 40)          :- respuesta(4, opcion_5).

% NIVEL 5: ELEMENTO CLAVE (30 pts)
puntos(accion, 30)    :- respuesta(5, opcion_1).
puntos(guerra, 30)    :- respuesta(5, opcion_1).
puntos(romance, 30)   :- respuesta(5, opcion_2).
puntos(misterio, 30)  :- respuesta(5, opcion_3).
puntos(comedia, 30)   :- respuesta(5, opcion_4).
puntos(terror, 30)    :- respuesta(5, opcion_5).

% --- MOTOR: Calcular puntaje total por género ---
puntaje_genero(Genero, Total) :-
    genero(_, Genero),
    findall(P, points_for_genre(Genero, P), ListaPuntos),
    sum_list(ListaPuntos, Total).

points_for_genre(Genero, P) :- puntos(Genero, P).

% CORRECCIÓN AQUÍ: Usamos una lista [Puntaje, Nombre] en vez de Puntaje-Nombre
obtener_puntajes_totales(Lista) :-
    findall([Puntaje, Nombre], (
        genero(_, Nombre),
        puntaje_genero(Nombre, Puntaje),
        Puntaje > 0
    ), Lista).

recomendar_generos(TopIds) :-
    obtener_puntajes_totales(Lista),
    extraer_ids(Lista, TopIds).

extraer_ids([], []).
% No necesitamos esto para la logica hibrida, pero lo dejo por si acaso
extraer_ids(_, []).

es_duracion_valida(Duracion, opcion_1) :- Duracion =< 90.
es_duracion_valida(Duracion, opcion_2) :- Duracion > 90, Duracion =< 120.
es_duracion_valida(Duracion, opcion_3) :- Duracion > 120.

% Regla para dar BONUS si coincide el tiempo
puntos_extra_tiempo(Duracion, PuntosExtra) :-
    respuesta(6, OpcionElegida),      % 6 es el nivel de la pregunta de tiempo
    es_duracion_valida(Duracion, OpcionElegida),
    PuntosExtra is 50.                % ¡50 Puntos extra si coincide!

puntos_extra_tiempo(_, 0).

% ====================================================
%   PROBLEMA DEL VIAJANTE (MARATÓN)
% ====================================================

% 1. Distancia entre dos películas
% La distancia es INVERSA a la cantidad de géneros compartidos.
% Si comparten 3 géneros, distancia = 20 - 3 = 17.
% Si comparten 0 géneros, distancia = 20 - 0 = 20 (Más lejos).
distancia_entre_titulos(T1, T2, Dist) :-
    pelicula(T1, _, _, _, _, _, _, Lista1), % Obtenemos lista completa 1
    pelicula(T2, _, _, _, _, _, _, Lista2), % Obtenemos lista completa 2
    intersection(Lista1, Lista2, Comunes),  % Calculamos intersección
    length(Comunes, N),
    Dist is 20 - N. 

% 2. Costo total de una ruta (lista de títulos)
costo_ruta([_], 0). % Una sola peli tiene costo 0
costo_ruta([P1, P2 | Resto], CostoTotal) :-
    distancia_entre_titulos(P1, P2, D),
    costo_ruta([P2 | Resto], CostoResto),
    CostoTotal is D + CostoResto.

% 3. Encontrar la mejor permutación (TSP)
% Recibe una lista de titulos desordenados y devuelve la lista ordenada.
optimizar_maraton(ListaOriginal, MejorRuta) :-
    findall(Costo-Ruta, (
        permutation(ListaOriginal, Ruta), % Genera todas las combinaciones posibles (5! = 120)
        costo_ruta(Ruta, Costo)           % Calcula el costo de esa combinación
    ), Opciones),
    keysort(Opciones, [_-MejorRuta | _]). % Ordena por costo y se queda con la primera (la menor)