import pandas as pd
import streamlit as st
import base64

from ydata_profiling import ProfileReport
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns


@st.cache_data
def carregar_dados(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    st.warning("Por favor, faça upload de um arquivo .CSV para continuar.")
    return None

# Função para plotar distribuição dos dados
def plot_histogram(df):
    num_cols = len(df.columns)
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    for i, column in enumerate(df.columns):
        row = i // 2
        col = i % 2
        sns.histplot(data=df, x=column, kde=True, ax=axes[row, col])
        axes[row, col].set_title(f'Distribuição de {column}')

    plt.tight_layout()
    st.pyplot(fig)

# Função para plotar valor total por mês
def plot_valor_total_por_mes(df):
    # Converter a coluna DiaCompra para o formato de data
    df['DiaCompra'] = pd.to_datetime(df['DiaCompra'])

    # Agrupar os dados por mês e calcular a média do ValorTotal
    df_monthly = df.groupby(df['DiaCompra'].dt.to_period('M'))['ValorTotal'].mean().reset_index()

    # Converter a coluna DiaCompra para o formato de string
    df_monthly['DiaCompra'] = df_monthly['DiaCompra'].astype(str)

    # Configurar estilo Seaborn
    sns.set(style='darkgrid')

    # Criar uma figura vazia
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plotar o gráfico de linha
    sns.lineplot(data=df_monthly, x='DiaCompra', y='ValorTotal', marker='o', ax=ax)

    # Definir rótulos e título do gráfico
    ax.set_xlabel('Data de Compra (Mês)')
    ax.set_ylabel('Valor Total')
    ax.set_title('Relação do Valor Médio Total por Mês')

    # Exibir o gráfico
    st.pyplot(fig)

def main():
    # Definir o template
    st.set_page_config(
        page_title='Previsão de Renda',
        page_icon='🧩',
        layout='wide'
    )

    # Título centralizado
    st.write(
        '<div style="display:flex; align-items:center; justify-content:center;">'
        '<h1 style="font-size:4.5rem;">Análises Segmentação</h1>'
        '</div>',
        unsafe_allow_html=True
    )

    # Divisão
    st.write("---")

    # Carregar dados
    uploaded_file = st.sidebar.file_uploader(
        label="Faça upload do arquivo CSV",
        type=["csv"]
    )
    df = carregar_dados(uploaded_file)

    if df is not None:
        # Widget para selecionar entre "Dados" e "Gráficos"
        tipo_descritiva = st.selectbox("Descritiva", ["Dados", "Gráficos"])

        if tipo_descritiva == "Dados":
            # Exibir título
            st.header("Dicionário de dados:")
            # Mostrar imagem
            st.image("https://raw.githubusercontent.com/.../imagem.png")

            # Mostrar título
            st.header("Dicionário de dados:")

            # Mostrar cabeçalho do DataFrame
            st.dataframe(df.head())

            # Adicionar botão para gerar relatório HTML
            if st.button("Gerar relatório"):
                # Gerar relatório HTML usando o ydata-profiling
                profile = ProfileReport(df)
                html = profile.to_html()

                # Exibir relatório HTML na página do Streamlit
                components.html(html, width=900, height=500, scrolling=True)

        elif tipo_descritiva == "Gráficos":
            # Widget para selecionar o tipo de gráfico
            tipo_grafico = st.radio("Tipo de Gráfico", ["Histogramas", "Valor Total por Mês"])

            if tipo_grafico == "Histogramas":
                # Chamar a função para plotar histogramas das colunas do DataFrame
                plot_histogram(df)

            elif tipo_grafico == "Valor Total por Mês":
                # Chamar a função para plotar valor total por mês
                plot_valor_total_por_mes(df)

# Executar o programa principal
if __name__ == "__main__":
    main()