import pandas as pd
import seaborn as sn
import numpy as np
import streamlit as st
import base64

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.cluster import AgglomerativeClustering


@st.cache_data
def carregar_dados(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    st.warning("Por favor, faça upload de um arquivo .CSV para continuar.")
    return None

def padronizar_dados(df):
    # Pegando as variáveis relacionadas a acesso
    var_sessao = df[['Administrative', 'Informational', 'ProductRelated', 'Administrative_Duration', 'Informational_Duration', 'ProductRelated_Duration']].copy()

    # Pegar as variáveis relacionadas a datas
    var_data = df[['SpecialDay', 'Month', 'Weekend']].copy()

    # Cria uma instância do StandardScaler
    scaler = StandardScaler()

    # Aplica a padronização às variáveis do DataFrame var_sessao
    var_sessao_scaled = scaler.fit_transform(var_sessao)

    # Cria um novo DataFrame com as variáveis padronizadas
    var_sessao_scaled_df = pd.DataFrame(var_sessao_scaled, columns=var_sessao.columns)

    # Transformando a variável 'month' em dummies
    var_data_encoded = pd.get_dummies(var_data, columns=['Month'])

    return var_sessao_scaled_df.join(var_data_encoded, on=None)

def plot_elbow_kmeans(df):
    """
    Plota o gráfico do método do cotovelo para o algoritmo K-means.

    Parâmetros:
    - df (pandas.DataFrame): O DataFrame contendo os dados.
    """

    # Lista para armazenar a soma dos quadrados das distâncias
    SQD = []

    # Define o range de valores para o número de clusters (k) de 1 a 10
    K = range(1, 10)

    # Loop sobre cada valor de k
    for k in K:
        # Cria uma instância do modelo KMeans com o número de clusters (k) atual e n_init=10
        km = KMeans(n_clusters=k, n_init=10)

        # Executa o algoritmo KMeans no conjunto de dados
        km.fit(df)

        # Calcula e armazena a soma dos quadrados das distâncias (inertia_) na lista SQD
        SQD.append(km.inertia_)

    # Cria o DataFrame com os valores de k e a soma dos quadrados das distâncias
    df_sqd = pd.DataFrame({'num_clusters': list(range(1, len(SQD)+1)), 'SQD': SQD})

    # Plota o gráfico do método do cotovelo
    st.line_chart(df_sqd.set_index('num_clusters'))

def plot_silhouette_kmeans(df):
    """
    Plota o gráfico do coeficiente de silhueta para o algoritmo K-means.

    Parâmetros:
    - df (pandas.DataFrame): O DataFrame contendo os dados.
    """

    # Range de valores de clusters que você deseja testar
    range_clusters = range(2, 11)

    # Lista para armazenar os valores de silhueta média
    silhouette_scores = []

    # Loop pelos diferentes números de clusters
    for n_clusters in range_clusters:
        # Inicializar e ajustar o modelo K-means
        kmeans = KMeans(n_clusters=n_clusters, n_init=10)
        kmeans.fit(df)

        # Obter os rótulos dos clusters e calcular o coeficiente de silhueta média
        cluster_labels = kmeans.labels_
        silhouette_avg = silhouette_score(df, cluster_labels)

        # Armazenar o valor médio de silhueta
        silhouette_scores.append(silhouette_avg)

    # Plotar o gráfico de silhueta
    st.line_chart(pd.DataFrame({'Número de Clusters': list(range_clusters), 'Coeficiente de Silhueta': silhouette_scores}).set_index('Número de Clusters'))

def get_cluster_labels(X, n_clusters, linkage='ward'):
    # sourcery skip: inline-immediately-returned-variable

    # Criar objeto AgglomerativeClustering
    agglomerative_fit = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
    
    # Ajustar o modelo aos dados
    labels = agglomerative_fit.fit_predict(X)
    
    return labels

def filter_groups_categorical(df, group_column, filter_variable, filter_category):
    # sourcery skip: inline-immediately-returned-variable
    """
    Filtra um DataFrame por uma variável categórica e retorna a contagem de ocorrências para cada grupo.

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame a ser filtrado.
    group_column : str
        Nome da coluna usada para agrupar os dados.
    filter_variable : str
        Nome da variável categórica usada para filtrar os dados.
    filter_category : str
        Categoria da variável categórica usada para filtrar os dados.

    Retorna
    -------
    pd.DataFrame
        DataFrame com a contagem de ocorrências para cada grupo.
    """
    # Filtrar o DataFrame com base na condição
    filtered_df = df[df[filter_variable] == filter_category]

    # Contar a quantidade de ocorrências da categoria especificada em cada grupo
    data = filtered_df.groupby(group_column)[filter_variable].count()

    return data

def filter_groups_continuous(df, group_column, filter_variable):
    # sourcery skip: inline-immediately-returned-variable
    """
    Agrupa um DataFrame por uma coluna e retorna a soma dos valores para uma variável contínua em cada grupo.

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame a ser agrupado.
    group_column : str
        Nome da coluna usada para agrupar os dados.
    filter_variable : str
        Nome da variável contínua usada para calcular a soma dos valores.

    Retorna
    -------
    pd.Series
        Série com a soma dos valores para cada grupo.
    """
    # Calcular a soma dos valores para a variável contínua em cada grupo
    data = df.groupby(group_column)[filter_variable].sum()

    return data




def main():  # sourcery skip: extract-duplicate-method, extract-method
    # Definir o template
    st.set_page_config(page_title='Previsão de Renda',
                    page_icon='🧩',
                    layout='wide')

    # Título centralizado
    st.write(
        '<div style="display:flex; align-items:center; justify-content:center;">'
        '<h1 style="font-size:4.5rem;">Clusterização</h1>'
        '</div>',
        unsafe_allow_html=True
    )

    # Divisão
    st.write("---")

    # Adiciona uma sidebar box para escolher entre K-means e Hierárquicos
    tipo_algoritmo = st.sidebar.selectbox(
        "Selecione o tipo de algoritmo", ("K-means", "Hierárquicos"))

        # Carregar dados
    uploaded_file = st.sidebar.file_uploader(
    label="Faça upload do arquivo CSV",
    type=["csv"]
)
    df = carregar_dados(uploaded_file)

    # Verifica se o arquivo foi carregado
    if uploaded_file is not None:
        # Lê o arquivo CSV em um DataFrame
        df = pd.read_csv(uploaded_file)

        # Verifica qual opção foi selecionada e executa o respectivo fluxo
        if tipo_algoritmo == "K-means":
            # Chama a função para padronizar os dados
            df_transformado = padronizar_dados(df)

            # Escolha entre Elbow e Silhueta
            tipo_metrica = st.radio(
                "Escolha a métrica de avaliação", ("Elbow", "Silhueta"))
            if tipo_metrica == "Elbow":
                st.subheader("Gráfico do Método do Cotovelo")
                plot_elbow_kmeans(df_transformado)
            else:
                tipo_metrica == "Silhueta"
                st.subheader("Gráfico do Coeficiente de Silhueta")
                plot_silhouette_kmeans(df_transformado)
            # Widget para definir a quantidade de clusters
            num_clusters_input = st.text_input("Digite a quantidade de clusters")

            # Converte o valor inserido para inteiro (caso seja válido)
            try:
                num_clusters = int(num_clusters_input)
            except ValueError:
                st.error("Digite um valor inteiro válido para a quantidade de clusters.")

            # Verifica se a quantidade de clusters é válida
            if num_clusters_input and num_clusters > 0:
                # Executa o algoritmo de K-means com a quantidade de clusters desejada
                kmeans = KMeans(n_clusters=num_clusters,
                                n_init=10, random_state=123)
                kmeans.fit(df_transformado)

                # Obter os rótulos de cluster atribuídos a cada ponto de dados
                labels = kmeans.labels_

                # Criar uma cópia do DataFrame original
                df_copia = df.copy()

                # Adicionar os rótulos de cluster no DataFrame df_copia
                df_copia['K-Means'] = labels

                # Exibir os resultados na página do Streamlit
                st.subheader("Resultados do Filtro")

                # Widget para selecionar a variável
                filter_variable = st.selectbox("Selecione a variável para o filtro", df_copia.columns)

                # Verificar o tipo de dado da variável
                variable_dtype = df_copia[filter_variable].dtype

                if pd.api.types.is_bool_dtype(variable_dtype) or pd.api.types.is_categorical_dtype(variable_dtype) or pd.api.types.is_object_dtype(variable_dtype):
                    # Widget para selecionar a categoria
                    unique_categories = df_copia[filter_variable].unique()
                    filter_category = st.selectbox("Selecione a categoria para o filtro", unique_categories)

                    # Executar a função filter_groups_categorical
                    results = filter_groups_categorical(df_copia, 'K-Means', filter_variable, filter_category)
                else:
                    # Executar a função filter_groups_continuous
                    results = filter_groups_continuous(df_copia, 'K-Means', filter_variable)

                # Exibir os resultados na página do Streamlit
                st.dataframe(results)

                # Botão de download do DataFrame copiado
                if st.button("Download DataFrame Clusterizado"):
                    csv = df_copia.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="df_copia.csv">Download</a>'
                    st.markdown(href, unsafe_allow_html=True)

        else:
            tipo_algoritmo == "Hierárquicos"
            # Chama a função para padronizar os dados
            df_transformado_hierarquicos = padronizar_dados(df)

            # Widget para selecionar o método de ligação
            metodo_ligacao = st.selectbox(
                "Selecione o método de ligação", ("ward", "complete", "average", "single"))

            # Widget para o usuário digitar a quantidade de clusters desejada
            num_clusters_desejado = st.text_input(
                "Digite a quantidade de clusters desejada", value='2')

            if num_clusters_desejado is not None:
                try:
                    num_clusters_desejado = int(num_clusters_desejado)
                    if num_clusters_desejado > 0:
                        # Treinar e extrair as labels do Agglomerative Clustering
                        labels_hierarquicos = get_cluster_labels(
                            df_transformado_hierarquicos, n_clusters=num_clusters_desejado, linkage=metodo_ligacao)
                except ValueError:
                    st.error("Digite um valor inteiro válido para a quantidade de clusters desejada.")
            else:
                num_clusters_desejado = None

            # Criar uma cópia do DataFrame original
            df_copia_hierarquicos = df.copy()

            # Treinar e extrair as labels do Agglomerative Clustering
            labels_hierarquicos = get_cluster_labels(
                df_transformado_hierarquicos, n_clusters=num_clusters_desejado, linkage=metodo_ligacao)

            # Adicionar os rótulos dos clusters ao DataFrame como uma nova coluna
            df_copia_hierarquicos['Hierárquicos'] = labels_hierarquicos

            # Exibir os resultados na página do Streamlit
            st.subheader("Resultados do Filtro")

            # Widget para selecionar a variável
            filter_variable_hierarquicos = st.selectbox(
                "Selecione a variável para o filtro", df_copia_hierarquicos.columns)

            # Widget para selecionar a categoria
            unique_categories_hierarquicos = df_copia_hierarquicos[filter_variable_hierarquicos].unique(
            )
            filter_category_hierarquicos = st.selectbox(
                "Selecione a categoria para o filtro", unique_categories_hierarquicos)

            # Montar as condições do filtro

            filter_conditions_hierarquicos = {
                filter_variable_hierarquicos: filter_category_hierarquicos}

            # Executar a função filter_groups para o algoritmo hierárquico
            results_hierarquicos, max_group_hierarquicos = filter_groups(
                df_copia_hierarquicos, 'Hierárquicos', filter_conditions_hierarquicos)

            # Exibir os resultados na página do Streamlit
            st.write("Grupo com a maior predominância:", max_group_hierarquicos)
            st.dataframe(results_hierarquicos)

            # Botão de download do DataFrame copiado
            if st.button("Download DataFrame Clusterizado"):
                csv = df_copia_hierarquicos.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="df_copia.csv">Download</a>'
                st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()




