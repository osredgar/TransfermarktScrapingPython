"""
python.exe -m venv .venv
.\.venv\Scripts\Activate.ps1
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run final.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from model.db import SQLiteConnector
from model.repo import DatabaseRepository

db = SQLiteConnector()
database = DatabaseRepository(db)
retorno_banco_dados = database.get_all_matches(1)

# base de dados
df = pd.DataFrame(retorno_banco_dados)
print(df.info())
# print(df.head())


# configuracao da pagina
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados", page_icon="📊​", layout="wide"
)

# filtros da barra lateral
st.sidebar.header("🔍​ Filtros")

anos_filtro = sorted(df["ano"].unique())
anos_selecionados = st.sidebar.multiselect(
    label="Ano", options=anos_filtro, default=anos_filtro
)

senioridades_filtro = sorted(df["senioridade"].unique())
senioridades_selecionados = st.sidebar.multiselect(
    label="Senioridade", options=senioridades_filtro, default=senioridades_filtro
)

contratos_filtro = sorted(df["contrato"].unique())
contratos_selecionados = st.sidebar.multiselect(
    label="Tipo Contrato", options=contratos_filtro, default=contratos_filtro
)

portes_filtro = sorted(df["porte"].unique())
portes_selecionados = st.sidebar.multiselect(
    label="Porte Empresa", options=portes_filtro, default=portes_filtro
)

# aplicar filtro ao dataframe
df_filtrado = df[
    (df["ano"].isin(anos_selecionados))
    & (df["senioridade"].isin(senioridades_selecionados))
    & (df["contrato"].isin(contratos_selecionados))
    & (df["porte"].isin(portes_selecionados))
]

# conteudo principal
st.title(body="🎲​ Dashboard de Salários na Área de Dados")

st.markdown(
    body="Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise."
)

st.markdown("---")

# metricas principais (kpis)
st.subheader(body="Métricas gerais (Salário anual em USD)")


if not df_filtrado.empty:
    salario_medio = df_filtrado["salario_dolar"].mean().round(2)
    salario_maximo = df_filtrado["salario_dolar"].max().round(2)
    total_registros = int(df_filtrado.shape[0])
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio = 0
    salario_maximo = 0
    total_registros = 0
    cargo_mais_frequente = 0

col_salario_medio, col_salario_maximo, col_total_registros, col_cargo_mais_frequente = (
    st.columns(4)
)

col_salario_medio.metric(label="Salário médio", value=salario_medio, format="dollar")

col_salario_maximo.metric(label="Salário máximo", value=salario_maximo, format="dollar")

col_total_registros.metric(
    label="Total registros", value=total_registros, format="localized"
)

col_cargo_mais_frequente.metric(
    label="Cargo mais frequente",
    value=cargo_mais_frequente,
    format="plain",
    width="stretch",
)

st.markdown("---")
st.subheader(body="Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if df_filtrado.empty:
        st.info("Nenhum dado para exibir no gráfico de cargos")
    else:
        top_cargos = (
            df_filtrado.groupby("cargo")["salario_dolar"]
            .mean()
            .nlargest(10)
            .sort_values(ascending=True)
            .reset_index()
        )

        graf_cargos = px.bar(
            data_frame=top_cargos,
            x="salario_dolar",
            y="cargo",
            orientation="h",
            title="Top 10 Média Salarial",
            labels={"salario_dolar": "Média salarial anual (USD)", "cargo": ""},
        )

        graf_cargos.update_layout(
            title_x=0.1, yaxis={"categoryorder": "total ascending"}
        )

        st.plotly_chart(figure_or_data=graf_cargos, width="stretch")

with col_graf2:
    if df_filtrado.empty:
        st.info("Nenhum dado para exibir no gráfico de distribuição")
    else:
        graf_hist = px.histogram(
            data_frame=df_filtrado,
            x="salario_dolar",
            nbins=30,
            title="Distrubuição dos salários anuais",
            labels={"salario_dolar": "Faixa salarial (USD)", "count": ""},
        )

        graf_hist.update_layout(title_x=0.1)

        st.plotly_chart(figure_or_data=graf_hist, width="stretch")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if df_filtrado.empty:
        st.info("Nenhum dado para exibir no gráfico dos tipos de trabalho")
    else:
        remoto_contagem = df_filtrado["remoto"].value_counts().reset_index()
        remoto_contagem.columns = ["tipo_trabalho", "quantidade"]

        graf_remoto = px.pie(
            remoto_contagem,
            names="tipo_trabalho",
            values="quantidade",
            title="Proporção dos tipos de trabalho",
            hole=0.5,
        )

        graf_remoto.update_traces(textinfo="percent+label")

        graf_remoto.update_layout(title_x=0.1)

        st.plotly_chart(figure_or_data=graf_remoto, width="stretch")

with col_graf4:
    if df_filtrado.empty:
        st.info("Nenhum dado para exibir no gráfico de países")
    else:
        df_data_scientist = df_filtrado[
            df_filtrado["cargo"] == df_filtrado["cargo"].mode()[0]
        ]

        media_ds_pais = (
            df_data_scientist.groupby("empresa_iso3")["salario_dolar"]
            .mean()
            .reset_index()
        )

        graf_paises = px.choropleth(
            data_frame=media_ds_pais,
            locations="empresa_iso3",
            color="salario_dolar",
            color_continuous_scale="rdylgn",
            title="Salário médio por país - " + df_filtrado["cargo"].mode()[0],
            labels={"salario_dolar": "Salário médio (USD)", "empresa_iso3": "País"},
        )

        graf_paises.update_layout(title_x=0.1)

        st.plotly_chart(figure_or_data=graf_paises, width="stretch")
