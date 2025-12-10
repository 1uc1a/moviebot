-----

# 🎬 MovieBot - Sistema Experto de Recomendación de Cine

Sistema híbrido inteligente (Python + Prolog) que genera recomendaciones de películas en tiempo real y optimiza el orden de visualización para maratones utilizando algoritmos combinatorios (Problema del Viajante).

[](https://www.python.org/)
[](https://www.swi-prolog.org/)
[](https://flet.dev/)
[](https://www.themoviedb.org/)

-----

## 📋 Tabla de Contenidos

  - [Características](https://www.google.com/search?q=%23-caracter%C3%ADsticas)
  - [Arquitectura](https://www.google.com/search?q=%23-arquitectura)
  - [Lógica y Algoritmos](https://www.google.com/search?q=%23-l%C3%B3gica-y-algoritmos)
  - [Requisitos](https://www.google.com/search?q=%23-requisitos-previos)
  - [Instalación](https://www.google.com/search?q=%23-instalaci%C3%B3n)
  - [Uso](https://www.google.com/search?q=%23-uso)
  - [Estructura del Proyecto](https://www.google.com/search?q=%23-estructura-del-proyecto)
  - [Tecnologías](https://www.google.com/search?q=%23-tecnolog%C3%ADas)

-----

## ✨ Características

### 🧠 Motor de Recomendación Experto

  - **Filtrado Multinivel**: 5 niveles de preguntas psicológicas y de preferencia (Situación, Mood, Ritmo, etc.).
  - **Inferencia Lógica**: Motor Prolog que calcula puntajes de afinidad por género.
  - **Bonus Temporal**: Reglas lógicas para filtrar por duración disponible (Corto, Normal, Largo).
  - **Datos en Tiempo Real**: Conexión viva con la API de TMDB para obtener carátulas, sinopsis y votos actuales.

### 🏃‍♂️ Modo Maratón (TSP - Traveling Salesperson Problem)

  - **Problema**: Minimizar la "disrupción cognitiva" al ver varias películas seguidas.
  - **Algoritmo**: Optimización combinatoria que ordena el Top 5.
  - **Métrica**: La distancia entre películas se basa en la intersección de conjuntos de géneros.
  - **Resultado**: Una transición fluida entre películas temáticamente conectadas.

### 🎨 Interfaz Gráfica Moderna (Flet)

  - **Diseño Neón/Dark**: Estética inmersiva de cine.
  - **Fichas Detalladas**: Visualización de pósters, todos los géneros (etiquetas dinámicas), duración y puntuación.
  - **Interactividad**: Sistema de Reviews, Historial de Vistas y "Muro de la Comunidad".

-----

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    INTERFAZ DE USUARIO (Flet)            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │     Test     │  │   Detalle    │  │ Modo Maratón │  │
│  │ Interactivo  │  │   Pelicula   │  │    (TSP)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              SISTEMA EXPERTO (Python + PySwip)           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  sistema_experto.py: Controlador Lógico          │  │
│  │  - conectar_prolog()                             │  │
│  │  - ordenar_por_tsp()                             │  │
│  └──────────────────────────────────────────────────┘  │
            │                               │
            ▼                               ▼
┌───────────────────────┐       ┌─────────────────────────┐
│   API MANAGER (TMDB)  │       │  BASE DE CONOCIMIENTO   │
│ ┌───────────────────┐ │       │      (SWI-Prolog)       │
│ │ Descarga Catálogo │ │       │ ┌─────────────────────┐ │
│ │ + Duración Real   │ │       │ │ movies.pl           │ │
│ └───────────────────┘ │       │ │ - pelicula/8        │ │
│                       │       │ │ - optimizar_maraton │ │
│                       │       │ │ - reglas puntos     │ │
│                       │       │ └─────────────────────┘ │
└───────────────────────┘       └─────────────────────────┘
```

### Flujo de Datos

1.  **Python (API)**: Descarga \~200 películas populares y sus metadatos (duración, géneros).
2.  **Inyección**: Se inyectan como `hechos` dinámicos en la base de conocimiento Prolog.
3.  **Preferencia**: El usuario responde el test en la UI. Python inyecta `respuesta(Nivel, Opcion)`.
4.  **Inferencia**: Prolog calcula puntajes acumulativos y devuelve el Top 5.
5.  **Optimización**: Al activar "Maratón", Prolog calcula la permutación óptima de esas 5 películas.

-----

## 🧮 Lógica y Algoritmos

### 1\. Sistema de Puntajes (Inferencia)

Prolog utiliza reglas acumulativas para definir el perfil del usuario.

```prolog
% Ejemplo de regla: Si elige "Cita", suma puntos a Romance y Drama
puntos(romance, 20) :- respuesta(1, opcion_2).
puntos(drama, 10)   :- respuesta(1, opcion_2).
```

### 2\. Problema del Viajante (Maratón)

Para ordenar las películas, modelamos el problema como un grafo completo donde:

  * **Nodos**: Películas del Top 5.
  * **Peso (Distancia)**: Inversamente proporcional a los géneros compartidos.

**Fórmula de Distancia:**
$$Distancia(A, B) = K - |Intersección(Generos_A, Generos_B)|$$

**Implementación en Prolog:**

```prolog
% Calcula intersección de listas de géneros y resta a la constante 20
distancia_entre_titulos(T1, T2, Dist) :-
    pelicula(T1, ..., Lista1),
    pelicula(T2, ..., Lista2),
    intersection(Lista1, Lista2, Comunes),
    length(Comunes, N),
    Dist is 20 - N.

% Busca la permutación con menor costo total
optimizar_maraton(Lista, MejorRuta) :- ...
```

**Complejidad**: $O(N! \cdot N)$. Dado que $N=5$ (Top 5), el espacio de búsqueda es de 120 permutaciones, lo cual permite encontrar el **óptimo global exacto** en tiempo despreciable.

-----

## 📦 Requisitos Previos

1.  **Python 3.8+**
2.  **SWI-Prolog** (Debe estar instalado y en el PATH del sistema).
      - [Descargar SWI-Prolog](https://www.swi-prolog.org/Download.html)
3.  **API Key de TMDB** (Gratuita).

-----

## 🚀 Instalación

### 1\. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/MovieBot.git
cd MovieBot
```

### 2\. Crear Entorno Virtual

```bash
python -m venv venv
# Activar:
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 3\. Instalar Dependencias

```bash
pip install -r requirements.txt
```

*Dependencias clave:* `flet`, `pyswip`, `requests`, `python-dotenv`.

### 4\. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz y añade tu clave:

```env
TMDB_API_KEY=tu_clave_aqui
```

-----

## 💻 Uso

Ejecuta el archivo principal de la interfaz:

```bash
python app_alegre.py
```

1.  **Inicio**: El sistema cargará la base de datos de Prolog y descargará películas de TMDB.
2.  **Test**: Responde las 6 preguntas (Situación, Mood, Ritmo, Tiempo, etc.).
3.  **Resultados**: Verás tu Top 5 recomendado.
4.  **Maratón**: Presiona el botón "Maratón 🎬" para ver el orden optimizado por Prolog.
5.  **Detalles**: Haz clic en "Ver Ficha" para ver detalles, marcar como vista o dejar una review.

-----

## 📁 Estructura del Proyecto

```
MovieBot/
├── prolog/
│   └── movies.pl              # Cerebro lógico: Reglas, Hechos y TSP
├── api_manager.py             # Conexión con TMDB (Data Fetching)
├── sistema_experto.py         # Puente Python-Prolog (Lógica de Negocio)
├── app_alegre.py              # Interfaz de Usuario (Flet Frontend)
├── .env                       # Credenciales (No incluido en repo)
└── README.md                  # Documentación
```

-----

## 🛠️ Tecnologías

### Backend & Lógica

  - **SWI-Prolog**: Motor de inferencia y resolución de problemas combinatorios.
  - **Python**: Orquestación y manejo de datos.
  - **PySwip**: Librería puente para consultas Prolog desde Python.

### Frontend

  - **Flet**: Framework de UI basado en Flutter para Python. Permite interfaces reactivas y modernas.

### Datos

  - **The Movie Database (TMDB) API**: Fuente de metadatos, imágenes y popularidad.

-----

## 👨‍💻 Autores

**Lucia Formenti y**
**Sol Mansilla**

  - Proyecto Universitario: Algortimia y Lógica Computacional.

-----

**¡Disfruta la función\! 🍿🎬**
