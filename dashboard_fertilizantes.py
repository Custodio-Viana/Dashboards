import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- Configuration ---
st.set_page_config(page_title="Comparador de Fertilizantes", layout="wide")
DATA_FILE = 'Fertilizante.csv'

# --- Data Loading & Cleaning ---
@st.cache_data
def load_and_clean_data():
    if not os.path.exists(DATA_FILE):
        return None
    
    # Try different encodings
    for encoding in ['latin1', 'utf-8', 'cp1252']:
        try:
            df = pd.read_csv(DATA_FILE, encoding=encoding)
            break
        except:
            continue
            
    # Clean Column Names
    # Expecting: Produto, N (%), P (%), K (%), Preo...
    # Normalize:
    # 1. Remove special chars
    # 2. Rename N, P, K for clarity
    
    clean_cols = {}
    for col in df.columns:
        new_col = col.strip()
        if 'N (%)' in new_col or 'N_%' in new_col: new_col = 'N'
        elif 'P (%)' in new_col or 'P_%' in new_col: new_col = 'P'
        elif 'K (%)' in new_col or 'K_%' in new_col: new_col = 'K'
        elif 'Pre' in new_col and 'Est' in new_col: new_col = 'Preco_Saca'
        elif 'Total' in new_col and 'Ha' in new_col: new_col = 'Custo_por_Ha'
        elif 'Saca' in new_col and 'Kg' in new_col: new_col = 'Saca_Kg'
        
        clean_cols[col] = new_col
        
    df = df.rename(columns=clean_cols)
    
    # Ensure numeric types
    for col in ['N', 'P', 'K', 'Preco_Saca', 'Custo_por_Ha']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

df = load_and_clean_data()

# --- Main App ---
st.title("🌱 Comparador de Fertilizantes: N-P-K e Custos")

if df is None:
    st.error(f"Arquivo '{DATA_FILE}' não encontrado.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filtros")

categorias = df['Categoria'].unique() if 'Categoria' in df.columns else []
selected_cats = st.sidebar.multiselect("Categoria", options=categorias, default=categorias)

fabricantes = df['Fabricante'].unique() if 'Fabricante' in df.columns else []
selected_fabs = st.sidebar.multiselect("Fabricante", options=fabricantes, default=fabricantes)

tecnologias = df['Tecnologia'].unique() if 'Tecnologia' in df.columns else []
selected_techs = st.sidebar.multiselect("Tecnologia", options=tecnologias, default=tecnologias)

# Filter Data
mask = pd.Series(True, index=df.index)
if 'Categoria' in df.columns and selected_cats:
    mask &= df['Categoria'].isin(selected_cats)
if 'Fabricante' in df.columns and selected_fabs:
    mask &= df['Fabricante'].isin(selected_fabs)
if 'Tecnologia' in df.columns and selected_techs:
    mask &= df['Tecnologia'].isin(selected_techs)    
    
filtered_df = df[mask]

# --- Charts ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("Composição Nutricional (N-P-K)")
    
    # Melt for stacked bar chart
    if {'N', 'P', 'K', 'Produto'}.issubset(filtered_df.columns):
        melted_df = filtered_df.melt(id_vars=['Produto'], value_vars=['N', 'P', 'K'], var_name='Nutriente', value_name='Porcentagem')
        
        fig_npk = px.bar(
            melted_df, 
            x='Produto', 
            y='Porcentagem', 
            color='Nutriente', 
            title="Comparação N-P-K por Produto",
            color_discrete_map={'N': '#2ca02c', 'P': '#1f77b4', 'K': '#ff7f0e'}, # Green, Blue, Orange
            text_auto=True
        )
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
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_cost, use_container_width=True)
    else:
        st.warning("Coluna 'Custo_por_Ha' não identificada.")

# --- Detailed Table ---
st.subheader("Detalhes dos Produtos")
st.dataframe(filtered_df)

# --- Advanced Analysis (Efficiency) ---
st.subheader("Eficiência Econômica: Custo por Unidade de Azoto (aplicado por Hectare)")

if {'N', 'Custo_por_Ha', 'KG_por_Ha', 'Produto'}.issubset(filtered_df.columns):
    # Calculate Kg of Nitrogen delivered per Hectare (Units of N)
    # N is percentage (e.g., 20 for 20%)
    filtered_df['Unidades_N_Ha'] = filtered_df['KG_por_Ha'] * (filtered_df['N'] / 100)
    
    # Calculate Cost per Unit of Nitrogen
    # Avoid division by zero
    filtered_df['Custo_Por_Unidade_N'] = filtered_df.apply(
        lambda row: row['Custo_por_Ha'] / row['Unidades_N_Ha'] if row['Unidades_N_Ha'] > 0 else 0, 
        axis=1
    )
    
    # Sort for ranking (Cheapest N at top)
    df_chart = filtered_df[filtered_df['Unidades_N_Ha'] > 0].sort_values('Custo_Por_Unidade_N')

    fig_efficiency = px.bar(
        df_chart,
        x='Produto',
        y='Custo_Por_Unidade_N',
        color='Categoria',
        title="Custo da Unidade de Azoto por Hectare (€)",
        text_auto='.2f',
        labels={
            'Custo_Por_Unidade_N': 'Custo Unidade Azoto (€)', 
            'Produto': 'Produto',
            'Unidades_N_Ha': 'Unidades N / Ha'
        },
        hover_data=['Custo_por_Ha', 'Unidades_N_Ha', 'Fabricante']
    )
    
    # Formatting
    fig_efficiency.update_yaxes(title_text='Custo Unidade Azoto (€)')
    fig_efficiency.update_traces(textposition='outside')
    
    st.plotly_chart(fig_efficiency, use_container_width=True)
    
    st.info("💡 **Análise:** Este gráfico mostra quanto você paga por cada 'Unidade' (Kg) de Nitrogênio efetivamente aplicada no campo. O cálculo divide o **Custo Total por Hectare** pelo total de **Unidades de Nitrogênio por Hectare**.")

else:
    st.warning("Colunas necessárias para cálculo de eficiência (N, KG_por_Ha, Custo_por_Ha) não encontradas.")
