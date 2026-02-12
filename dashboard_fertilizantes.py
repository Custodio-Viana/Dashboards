import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- Configuração Inicial ---
# Define o título da página e o layout para 'wide' (usa toda a largura da tela)
st.set_page_config(page_title="Comparador de Fertilizantes - Golf", layout="wide")
DATA_FILE = 'Fertilizante.csv'

# --- Carregamento e Limpeza de Dados ---
# @st.cache_data armazena o resultado da função em cache para acelerar o recarregamento
@st.cache_data
def load_and_clean_data():
    # Verifica se o arquivo existe antes de tentar carregar
    if not os.path.exists(DATA_FILE):
        return None
    
    # Tenta ler o arquivo com diferentes codificações, priorizando utf-8/utf-8-sig
    # A ordem importa! utf-8 não aceita bytes invalidos, enquanto latin1 aceita quase tudo como errado.
    for encoding in ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']:
        try:
            df = pd.read_csv(DATA_FILE, encoding=encoding)
            break
        except:
            continue
            
    # --- Padronização dos Nomes das Colunas ---
    # O objetivo é garantir que o código entenda as colunas independentemente de pequenas variações no CSV
    # Exemplo: 'N (%)' vira apenas 'N'
    
    clean_cols = {}
    for col in df.columns:
        new_col = col.strip() # Remove espaços extras no início/fim
        
        # Mapeamento de nomes de colunas
        if 'N (%)' in new_col or 'N_%' in new_col: new_col = 'N'
        elif 'P (%)' in new_col or 'P_%' in new_col: new_col = 'P'
        elif 'K (%)' in new_col or 'K_%' in new_col: new_col = 'K'
        elif 'Pre' in new_col and 'Est' in new_col: new_col = 'Preco_Saca'
        # Correção crítica: Mapeia 'Total' e 'Ha' para 'Custo_por_Ha'
        elif 'Total' in new_col and 'Ha' in new_col: new_col = 'Custo_por_Ha'
        elif 'Saca' in new_col and 'Kg' in new_col: new_col = 'Saca_Kg'
        
        clean_cols[col] = new_col
        
    df = df.rename(columns=clean_cols)
    
    # --- Conversão de Tipos ---
    # Garante que colunas numéricas sejam tratadas como números (float), não texto
    for col in ['N', 'P', 'K', 'Preco_Saca', 'Custo_por_Ha']:
        if col in df.columns:
            # erros='coerce' transforma textos não numéricos em NaN (vazio), depois preenchemos com 0
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

# Carrega os dados processados para a variável df
df = load_and_clean_data()

# --- Interface Principal (Main App) ---
st.title("⛳ Comparador de Fertilizantes: Visão Greenkeeper")

if df is None:
    st.error(f"Arquivo '{DATA_FILE}' não encontrado. Por favor, verifique se o arquivo está na mesma pasta do script.")
    st.stop()

# --- Filtros (Barra Lateral) ---
st.sidebar.header("Filtros de Campo")

# Cria filtros dinâmicos baseados nos dados disponíveis
# Se a coluna existir, pega os valores únicos para criar as opções
categorias = df['Categoria'].unique() if 'Categoria' in df.columns else []
selected_cats = st.sidebar.multiselect("Categoria", options=categorias, default=categorias)

fabricantes = df['Fabricante'].unique() if 'Fabricante' in df.columns else []
selected_fabs = st.sidebar.multiselect("Fabricante", options=fabricantes, default=fabricantes)

tecnologias = df['Tecnologia'].unique() if 'Tecnologia' in df.columns else []
selected_techs = st.sidebar.multiselect("Tecnologia", options=tecnologias, default=tecnologias)

# --- Aplicação dos Filtros ---
# Cria uma máscara booleana inicial (tudo True) e vai filtrando conforme seleção
mask = pd.Series(True, index=df.index)
if 'Categoria' in df.columns and selected_cats:
    mask &= df['Categoria'].isin(selected_cats)
if 'Fabricante' in df.columns and selected_fabs:
    mask &= df['Fabricante'].isin(selected_fabs)
if 'Tecnologia' in df.columns and selected_techs:
    mask &= df['Tecnologia'].isin(selected_techs)    
    
# Cria um novo DataFrame apenas com os dados filtrados
filtered_df = df[mask]

# --- Gráficos (Dashboard) ---

# Divide a tela em duas colunas para os gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("Composição Nutricional (N-P-K)")
    
    # Verifica se as colunas necessárias existem
    if {'N', 'P', 'K', 'Produto'}.issubset(filtered_df.columns):
        # Transforma os dados para formato 'longo' facilitando o gráfico agrupado
        melted_df = filtered_df.melt(id_vars=['Produto'], value_vars=['N', 'P', 'K'], var_name='Nutriente', value_name='Porcentagem')
        
        # --- Cores Tema Golf ---
        # N (Crescimento Foliar) -> Verde Escuro (DarkGreen)
        # P (Raízes) -> Verde Oliva/Terra (DarkOliveGreen)
        # K (Resistência) -> Verde Amarelado/Vibrante (YellowGreen)
        golf_colors = {
            'N': '#006400',  
            'P': '#556B2F',  
            'K': '#9ACD32'   
        }
        
        fig_npk = px.bar(
            melted_df, 
            x='Produto', 
            y='Porcentagem', 
            color='Nutriente', 
            title="Comparação N-P-K por Produto",
            color_discrete_map=golf_colors, # Aplica o mapa de cores definido acima
            text_auto=True
        )
        # Remove fundo cinza padrão para um visual mais limpo
        fig_npk.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_npk, use_container_width=True)
    else:
        st.warning("Colunas de Nutrientes (N, P, K) não identificadas.")

with col2:
    st.subheader("Análise de Custo por Hectare")
    if 'Custo_por_Ha' in filtered_df.columns and 'Produto' in filtered_df.columns:
        fig_cost = px.bar(
            filtered_df,
            x='Produto',
            y='Custo_por_Ha',
            color='Custo_por_Ha',
            title="Custo Total por Hectare (€)",
            text_auto='.0f',
            color_continuous_scale='Greens' # Escala contínua de verdes (quanto mais caro, mais escuro)
        )
        fig_cost.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_cost, use_container_width=True)
    else:
        st.warning("Coluna 'Custo_por_Ha' não identificada.")

# --- Tabela Detalhada (Scorecard) ---
st.subheader("Detalhes dos Produtos (Scorecard)")
st.dataframe(filtered_df)

# --- Análise Avançada (Eficiência) ---
st.subheader("Eficiência Econômica: Custo por Unidade de Azoto")

if {'N', 'Custo_por_Ha', 'KG_por_Ha', 'Produto'}.issubset(filtered_df.columns):
    # --- Cálculo de Eficiência ---
    
    # 1. Calcula quantos KG de Nitrogênio puro estamos jogando no campo por Hectare
    # Cálculo: (Kg totais do produto por Ha) * (% de Azoto / 100)
    filtered_df['Unidades_N_Ha'] = filtered_df['KG_por_Ha'] * (filtered_df['N'] / 100)
    
    # 2. Calcula quanto custa cada kg de Nitrogênio puro
    # Cálculo: (Custo Total por Ha) / (Unidades de N por Ha)
    # Evita divisão por zero
    filtered_df['Custo_Por_Unidade_N'] = filtered_df.apply(
        lambda row: row['Custo_por_Ha'] / row['Unidades_N_Ha'] if row['Unidades_N_Ha'] > 0 else 0, 
        axis=1
    )
    
    # Ordena para mostrar o mais eficiente (barato) primeiro
    df_chart = filtered_df[filtered_df['Unidades_N_Ha'] > 0].sort_values('Custo_Por_Unidade_N')

    fig_efficiency = px.bar(
        df_chart,
        x='Produto',
        y='Custo_Por_Unidade_N',
        title="Custo da Unidade de Azoto por Hectare (€)",
        text_auto='.2f',
        labels={
            'Custo_Por_Unidade_N': 'Custo Unidade Azoto (€)', 
            'Produto': 'Produto',
            'Unidades_N_Ha': 'Unidades N / Ha'
        },
        hover_data=['Custo_por_Ha', 'Unidades_N_Ha', 'Fabricante']
    )
    
    # Formatação Visual da Eficiência
    # Usa um verde vibrante (LimeGreen) para destacar a eficiência
    fig_efficiency.update_traces(marker_color='#32CD32', textposition='outside')
    fig_efficiency.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig_efficiency.update_yaxes(title_text='Custo Unidade Azoto (€)')
    
    st.plotly_chart(fig_efficiency, use_container_width=True)
    
    st.info("💡 **Análise Greenkeeper:** Este gráfico mostra o custo real por Kg de Nitrogênio aplicado. Pense nisso como o 'Strokes Gained' do seu orçamento: quanto menos você paga por unidade de nutriente, mais eficiente é a sua gestão.")

else:
    st.warning("Dados necessários (N, KG_por_Ha, Custo_por_Ha) não encontrados para calcular eficiência.")
