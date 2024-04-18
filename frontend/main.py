import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import plotly.figure_factory as ff

# Caminho do arquivo CSV para os projetos
PROJECTS_FILEPATH = Path('data/cadastro.csv')
# Caminho para o arquivo de ordens de serviço
ORDERS_FILEPATH = Path('data/controle.csv')
# Caminho para o logotipo
LOGO_PATH = Path('img/Conami.png')

def load_data(filepath):
    # Carregamento e processamento do dataframe
    df = pd.read_csv(filepath)
    # Conversão de datas com o formato mês/dia/ano
    df['Data Recebim.'] = pd.to_datetime(df['Data Recebim.'], format='%m/%d/%Y', errors='coerce')
    df['Data de Entrega'] = pd.to_datetime(df['Data de Entrega'], format='%m/%d/%Y', errors='coerce')
    df['Data envio'] = pd.to_datetime(df['Data envio'], format='%m/%d/%Y', errors='coerce')
    return df

def plot_gantt_chart(df):
    # Preparando dados para o gráfico de Gantt
    df_gantt = []
    for _, row in df.iterrows():
        df_gantt.append(dict(Task="Cliente: " + row['Cliente'], Start=row['Data Recebim.'], Finish=row['Data de Entrega'], Resource='Data de Entrega'))
        df_gantt.append(dict(Task="Cliente: " + row['Cliente'], Start=row['Data Recebim.'], Finish=row['Data Recebim.'] + pd.Timedelta(days=1), Resource='Data Recebim.'))
        df_gantt.append(dict(Task="Cliente: " + row['Cliente'], Start=row['Data envio'], Finish=row['Data envio'] + pd.Timedelta(days=1), Resource='Data envio'))

    colors = {'Data de Entrega': '#0000FF', 'Data Recebim.': '#008000', 'Data envio': '#FFFF00'}
    fig = ff.create_gantt(df_gantt, index_col='Resource', colors=colors, show_colorbar=True, group_tasks=True, showgrid_x=True, showgrid_y=True)
    return fig

def load_order_data(filepath):
    df = pd.read_csv(filepath)
    return df

def plot_total_orders_by_client(df):
    order_counts = df['Cliente'].value_counts().reset_index()
    order_counts.columns = ['Cliente', 'Total de Ordens']
    fig = px.bar(order_counts, x='Cliente', y='Total de Ordens', title='Total de Ordens de Serviço por Cliente')
    return fig

def plot_total_value_by_client(df):
    # Primeiro agrupamos por cliente e somamos os valores
    total_values = df.groupby('Cliente')['Serviços'].sum().reset_index()
    total_values.columns = ['Cliente', 'Valor Acumulado']

    # Agora contamos as ordens por cliente para ordenação
    order_counts = df['Cliente'].value_counts().reset_index()
    order_counts.columns = ['Cliente', 'Total de Ordens']

    # Juntamos os dados de valores acumulados com as contagens de ordens
    total_values = total_values.merge(order_counts, on='Cliente')

    # Ordenamos os valores acumulados pela quantidade de ordens (Total de Ordens)
    total_values.sort_values('Total de Ordens', ascending=False, inplace=True)

    # Criamos o gráfico
    fig = px.bar(total_values, x='Cliente', y='Valor Acumulado', title='Valor Acumulado por Cliente',
                 labels={'Valor Acumulado': 'Valor Acumulado (R$)'}, text='Total de Ordens')
    return fig

def main():
    st.title('Dashboard de Acompanhamento de Projetos')
    col1, col2 = st.columns([8, 1])  # Ajusta o tamanho das colunas
    with col2:
        st.image(str(LOGO_PATH), width=100)  # Converte Path para string

    project_data = load_data(PROJECTS_FILEPATH)
    st.subheader('Gráfico de Gantt dos Projetos')
    gantt_fig = plot_gantt_chart(project_data)
    st.plotly_chart(gantt_fig)

    order_data = load_order_data(ORDERS_FILEPATH)
    st.subheader('Análise de Ordens de Serviço')

    value_fig = plot_total_value_by_client(order_data)
    st.plotly_chart(value_fig)

if __name__ == "__main__":
    main()