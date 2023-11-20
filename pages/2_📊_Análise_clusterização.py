import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import plotly.express as px
import base64

from ydata_profiling import ProfileReport

@st.cache_data
def carregar_dados(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    st.warning("Por favor, faça upload de um arquivo .CSV para continuar.")
    return None

def compras_acessos(df, x_col):
    """
    Gera um gráfico de barras mostrando a quantidade de sessões por uma determinada coluna (x_col),
    com opção de agrupamento (hue_col), e exibindo o número de compras (y_col).

    Parâmetros:
    - df (pandas.DataFrame): O DataFrame contendo os dados.
    - x_col (str): O nome da coluna a ser usada no eixo x do gráfico.
    """

    # Define os valores fixos para y_col e hue_col
    y_col = 'Acessos'
    hue_col = 'Revenue'

    # Filtra os dados
    df_filtered = df[df[x_col] != 0.0]

    # Agrupa os dados por x_col e y_col e conta o número de ocorrências
    df_grouped = df_filtered.groupby([x_col, hue_col]).size().reset_index(name='count')

    # Calcula o número total de acessos para cada valor de x_col
    total_accesses = df_grouped.groupby(x_col)['count'].sum().reset_index(name='total')

    # Mescla os dados de compras e acessos totais
    df_merged = df_grouped[df_grouped[hue_col] == True].merge(total_accesses, on=x_col)

    # Renomeia as colunas
    df_merged.rename(columns={'count': f'{y_col} Compras', 'total': f'{y_col} Totais'}, inplace=True)

    # Reestrutura os dados para que cada série de dados esteja em uma coluna separada
    df_melted = df_merged.melt(id_vars=x_col, value_vars=[f'{y_col} Compras', f'{y_col} Totais'], var_name='Legenda', value_name='count')

    # Gera o gráfico de barras
    fig = px.bar(df_melted, x=x_col, y='count', text='count', color='Legenda')
    fig.update_layout(title=f"Quantidade de Sessões por {x_col}",
                      xaxis_title=x_col,
                      yaxis_title="Quantidade de Sessões",
                      showlegend=True)

    st.plotly_chart(fig)


def plot_weekend(df):
    """
    Gera um gráfico de barras mostrando a proporção de compras por acessos para dias de semana e fins de semana.

    Parâmetros:
    - df (pandas.DataFrame): O DataFrame contendo os dados.
    """

    # Agrupar os dados por 'Weekend' e contar o número de sessões
    df_grouped = df.groupby(['Weekend', 'Revenue']).size().reset_index(name='count')

    # Calcular o número total de acessos para cada categoria de 'Weekend'
    total_accesses = df_grouped.groupby('Weekend')['count'].sum().reset_index(name='total')

    # Mesclar os dados de comprasimportadas e plotar o gráfico

    # Mesclar os dados de compras e acessos totais
    df_merged = df_grouped[df_grouped['Revenue'] == True].merge(total_accesses, on='Weekend')

    # Renomear as colunas
    df_merged.rename(columns={'count': 'Acessos Compras', 'total': 'Acessos Totais'}, inplace=True)

    # Calcular a proporção de compras por acessos para cada categoria de 'Weekend'
    df_merged['Proporção Compras/Acessos'] = df_merged['Acessos Compras'] / df_merged['Acessos Totais']

    # Gerar o gráfico de barras
    fig = px.bar(df_merged, x='Weekend', y='Proporção Compras/Acessos', color='Weekend', text='Proporção Compras/Acessos')
    fig.update_layout(title="Proporção de Compras por Acessos para dias de semana e fins de semana",
                      xaxis_title="Weekend",
                      yaxis_title="Proporção Compras/Acessos",
                      showlegend=False)

    st.plotly_chart(fig)


def plot_access(df, access_type='quantidade'):
    """
    Plota um gráfico de barras mostrando a quantidade de acessos ou a duração dos acessos por tipo de página.

    Args:
        df (DataFrame): O DataFrame contendo os dados.
        access_type (str, optional): O tipo de acesso a ser plotado. Pode ser 'quantidade' (padrão) para a quantidade de
            acessos ou 'duração' para a duração dos acessos. Defaults para 'quantidade'.
    """

    # Seleciona as colunas de acordo com o tipo de acesso escolhido
    if access_type == 'quantidade':
        access_columns = ['Administrative', 'Informational', 'ProductRelated']
        title = 'Acessos Totais por Tipo de Página (Quantidade)'
    elif access_type == 'duração':
        access_columns = ['Administrative_Duration', 'Informational_Duration', 'ProductRelated_Duration']
        title = 'Acessos Totais por Tipo de Página (Duração)'
    else:
        raise ValueError('Tipo de acesso inválido. Escolha "quantidade" ou "duração".')

    # Agrupa os dados por tipo de página e soma as variáveis de acesso
    df_grouped = df[access_columns].sum().reset_index()
    df_grouped.columns = ['Tipo de Página', 'Acessos']

    # Cria o gráfico de barras
    fig = px.bar(df_grouped, x='Tipo de Página', y='Acessos', color='Tipo de Página',
                title=title,
                labels={'Tipo de Página': 'Tipo de Página', 'Acessos': 'Acessos'})

    st.plotly_chart(fig)


def outliers_box(df):
    """
    Gera gráficos de boxplot mostrando a distribuição dos acessos por página.

    Parâmetros:
    - df (pandas.DataFrame): O DataFrame contendo os dados.
    """

    # Cria um objeto Figure do Matplotlib
    fig, ax = plt.subplots()

    # Gera o gráfico de boxplot para a quantidade de acesso
    sns.boxplot(data=df[['Administrative','Informational','ProductRelated']], ax=ax)
    ax.set_ylim(0, 100)

    # Exibe o gráfico na página do Streamlit
    st.pyplot(fig)

    # Cria um novo objeto Figure do Matplotlib
    fig, ax = plt.subplots()

    # Gera o gráfico de boxplot para o tempo de acesso
    sns.boxplot(data=df[['Administrative_Duration','Informational_Duration','ProductRelated_Duration']], ax=ax)
    ax.set_ylim(0, 7500)

    # Exibe o gráfico na página do Streamlit
    st.pyplot(fig)

def main():  # sourcery skip: avoid-builtin-shadow
    # Definir o template
    st.set_page_config(page_title='Clusterização',
                       page_icon='🧩',
                       layout='wide')

    # Título centralizado
    st.markdown('<div style="display:flex; align-items:center; justify-content:center;"><h1 style="font-size:4.5rem;">Análises Clusterização</h1></div>',
                unsafe_allow_html=True)

    # Divisão
    st.write("---")

    # Carregar dados
    uploaded_file = st.sidebar.file_uploader("Faça upload do arquivo CSV")
    label="Faça upload do arquivo CSV",
    type=["csv"]

    df = carregar_dados(uploaded_file)

    if df is not None:
        # Adicionar caixa de seleção na barra lateral
        selecao_dados = st.sidebar.selectbox(
            "Selecione uma opção",
            ("Info", "Descritiva")
        )

        if selecao_dados == "Info":
            # Mostrar título
            st.header("Dicionário de dados:")

            # Mostrar imagem
            st.image("https://raw.githubusercontent.com/.../imagem.png")

            # Mostrar cabeçalho do DataFrame
            st.dataframe(df.head())

            # Adicionar botão para gerar relatório HTML
            if st.button("Gerar relatório"):
                # Gerar relatório HTML usando o ydata-profiling
                profile = ProfileReport(df)
                html = profile.to_html()

                # Exibir relatório HTML na página do Streamlit
                components.html(html, width=900, height=500, scrolling=True)

        else:
            # Adicionar caixa de seleção na barra lateral
            selecao_compras_acessos = st.sidebar.selectbox(
                "Selecione uma opção",
                ("Compras x Acessos", "Acessos por página", "Outliers")
            )
            if selecao_compras_acessos == "Compras x Acessos":
                # Filtra as colunas que já estão na função compras_acessos
                cols = [col for col in df.columns if col not in [
                    'Acessos', 'Revenue']]
                col_selected = st.selectbox("Selecione a coluna", cols)
                compras_acessos(df, col_selected)
            elif selecao_compras_acessos == "Acessos por página":
                access_type = st.selectbox("Selecione o tipo de acesso", ['quantidade', 'duração'])
                plot_access(df, access_type)
            else:
                outliers_box(df)
if __name__ == "__main__":
    main()
