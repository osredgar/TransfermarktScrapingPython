import sqlite3

import pandas as pd
import streamlit as st


# Exemplo da sua rotina existente
# 3. Dica de Performance: st.cache_data
# Não é ideal que o Streamlit execute a consulta ao SQLite toda vez que você clicar em um botão ou filtro.
# Use o decorador de cache para salvar os dados na memória:
@st.cache_data
def busca_dados_sqlite():
    # Sua lógica aqui
    return dados


# 1. Converter para DataFrame
dados = busca_dados_sqlite()
df = pd.DataFrame(dados)

## Configuração da Página
st.set_page_config(page_title="Meu Dashboard SQLite", layout="wide")
st.title("📊 Análise de Dados de Vendas")

## Sidebar para Filtros (Opcional)
st.sidebar.header("Filtros")
filtro_nome = st.sidebar.multiselect(
    "Selecione o Item:", options=df["coluna_nome"].unique()
)

if filtro_nome:
    df = df[df["coluna_nome"].isin(filtro_nome)]

## Layout de Métricas (Cards)
col1, col2, col3 = st.columns(3)
col1.metric("Total de Registros", len(df))
col2.metric("Soma de Valores", f"R$ {df['valor'].sum():,.2f}")
col3.metric("Média", f"{df['valor'].mean():,.2f}")

## Gráficos e Tabelas
aba1, aba2 = st.tabs(["📈 Gráficos", "📄 Dados Brutos"])

with aba1:
    st.subheader("Visualização Gráfica")
    # Gráfico de barras simples
    st.bar_chart(df, x="coluna_nome", y="valor")

with aba2:
    st.subheader("Tabela de Dados")
    st.dataframe(df, use_container_width=True)
