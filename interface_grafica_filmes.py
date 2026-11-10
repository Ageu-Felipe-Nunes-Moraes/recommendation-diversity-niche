import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. CONFIGURAÇÃO E ESTILO (VISUAL Reconflix)
# ==========================================
st.set_page_config(page_title="Reconflix - Full List", layout="wide")

st.markdown("""
<style>
    .stApp {
        background-color: #141414;
        color: white;
    }
    
    .netflix-logo {
        color: #E50914;
        font-family: 'Arial Black', sans-serif;
        font-size: 45px;
        font-weight: bold;
        margin: 0;
    }

    div[data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }

    .movie-card {
        background-color: #1c1f26;
        border-radius: 8px;
        transition: transform 0.3s ease;
        margin-bottom: 10px;
    }
    
    .movie-card:hover {
        transform: scale(1.05);
        z-index: 5;
    }

    .movie-info-text {
        padding: 10px;
        font-size: 14px;
    }

    .relevance-tag {
        color: #46d369;
        font-weight: bold;
        font-size: 13px;
    }

    div.stButton > button {
        background-color: #e50914;
        color: white;
        border: none;
        width: 100%;
        font-weight: bold;
        height: 35px;
    }
    
    div.stButton > button:hover {
        background-color: #f40612;
        color: white;
    }

    div[data-testid="stDialog"] div[role="dialog"] {
        background-color: #181818 !important;
        color: #FFFFFF !important;
        border: 1px solid #444;
    }

    .modal-title {
        color: #FFFFFF !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin-bottom: 5px;
    }

    .modal-text {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
        line-height: 1.6;
    }

    .modal-label {
        color: #B3B3B3 !important;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# 2. CARREGAMENTO DE DADOS
# =========================
@st.cache_data
def carregar_dados():
    try:
        # CORREÇÃO 1: Definimos os tipos (dtype) como str para evitar falhas de conversão de nulos
        # e usamos 'keep_default_na=True' para tratar os campos vazios corretamente.
        df = pd.read_csv(
            "filmes_encontrados.txt",
            sep="|",
            header=None,
            names=["search_title", "year", "id", "title", "release_date", "vote_average", "poster_url", "overview"],
            dtype=str, 
            keep_default_na=True
        )
        
        # Converte a nota para numérico com segurança (o que for vazio vira NaN)
        df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce")
        
        # CORREÇÃO 2: Se o título original estiver nulo, usamos o 'search_title' para não ficar em branco
        df["title"] = df["title"].fillna(df["search_title"])
        
        return df
    except Exception as e:
        # Mensagem temporária caso haja um erro real de estrutura no arquivo
        st.error(f"Erro ao ler arquivo: {e}")
        return pd.DataFrame(columns=["id", "title", "vote_average", "poster_url", "release_date", "overview"])

df = carregar_dados()
PLACEHOLDER = "https://via.placeholder.com/300x450/1c1f26/ffffff?text=Sem+Poster"

def get_poster(url):
    return url if pd.notna(url) and str(url).startswith('http') else PLACEHOLDER

# Helper para calcular a relevância sem quebrar com valores nulos
def calcular_relevancia(vote_average):
    if pd.isna(vote_average):
        return 0
    return int(vote_average * 10)

# ==========================================
# 3. FUNÇÃO DO POP-UP (MODAL)
# ==========================================
@st.dialog(" ")
def mostrar_modal(filme):
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.image(get_poster(filme["poster_url"]), width="stretch") 
    with col2:
        st.markdown(f'<div class="modal-title">{filme["title"]}</div>', unsafe_allow_html=True)
        
        relevancia = calcular_relevancia(filme['vote_average'])
        nota_exibicao = f"{filme['vote_average']} / 10" if pd.notna(filme['vote_average']) else "Sem nota"
        data_lancamento = filme['release_date'] if pd.notna(filme['release_date']) else "Não informada"
        
        st.markdown(f"""
            <div class="modal-text">
                <span class="modal-label">Lançamento:</span> {data_lancamento}<br>
                <span class="modal-label">Avaliação:</span> ⭐ {nota_exibicao}<br>
                <span style='color:#46d369; font-weight:900; font-size:1.3rem;'>{relevancia}% relevante</span>
            </div>
            <hr style="border-color: #444;">
            <div class="modal-text">
                <span class="modal-label">Sinopse:</span><br>
                {filme['overview'] if pd.notna(filme['overview']) and str(filme['overview']).strip() != '' else 'Sinopse não disponível.'}
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        # Backup caso o ID esteja nulo para não quebrar a chave do botão
        id_filme = filme['id'] if pd.notna(filme['id']) else f"sem_id_{filme['title']}"
        if st.button("▶ Assistir Agora", key=f"play_{id_filme}"):
            st.info(f"Iniciando: {filme['title']}")

# ==========================================
# 4. GRID DE FILMES (EXIBE TUDO)
# ==========================================
def mostrar_todos_filmes(dataframe):
    if dataframe.empty:
        st.warning("Nenhum filme encontrado com os filtros selecionados.")
        return

    st.subheader(f"Catálogo Completo ({len(dataframe)} títulos)")
    
    num_cols = 5
    cols = st.columns(num_cols)

    for i, (_, filme) in enumerate(dataframe.iterrows()):
        idx_col = i % num_cols
        with cols[idx_col]:
            relevancia = calcular_relevancia(filme['vote_average'])
            
            st.markdown(f'''
                <div class="movie-card">
                    <img src="{get_poster(filme['poster_url'])}" style="width:100%; border-radius: 8px 8px 0 0; aspect-ratio: 2/3; object-fit: cover;">
                    <div class="movie-info-text">
                        <div style="height: 40px; overflow: hidden; color: white;"><b>{filme['title']}</b></div>
                        <span class="relevance-tag">{relevancia}% relevante</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

            id_filme = filme['id'] if pd.notna(filme['id']) else f"sem_id_{i}"
            btn_key = f"btn_main_{id_filme}_{i}"
            if st.button("Detalhes", key=btn_key):
                mostrar_modal(filme)

# =========================
# 5. EXECUÇÃO DA INTERFACE
# =========================

st.markdown('<p class="netflix-logo">RECONFLIX</p>', unsafe_allow_html=True)

col_busca, col_filtro = st.columns([3, 1])
with col_busca:
    busca = st.text_input(
        label="Barra de busca", 
        placeholder="Pesquise por título no catálogo completo...", 
        label_visibility="collapsed"
    )

with col_filtro:
    nota_min = st.slider("Filtrar por nota mínima", 0.0, 10.0, 0.0)

df_final = df.copy()

if busca:
    df_final = df_final[df_final["title"].str.contains(busca, case=False, na=False)]

# CORREÇÃO 3: Modificado o filtro da nota para incluir os filmes que não possuem nota (NaN)
# permitindo que apareçam caso o slider esteja em 0.0
if nota_min > 0.0:
    df_final = df_final[df_final["vote_average"] >= nota_min]
else:
    # Se o slider for 0.0, traz inclusive os que tem nota nula (NaN)
    df_final = df_final[(df_final["vote_average"] >= nota_min) | (df_final["vote_average"].isna())]

mostrar_todos_filmes(df_final)