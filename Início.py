import streamlit as st

# Definir o template
st.set_page_config(page_title='Clusterização',
                page_icon='🧩',
                layout='wide')

# Apresenta a imagem na barra lateral da aplicação
url = "https://raw.githubusercontent.com/Caiodrp/Previsao-Renda-Streamlit/main/img/Design%20sem%20nome.jpg"
st.sidebar.image(url,use_column_width=True)

# Título centralizado
st.write(
    '<div style="display:flex; align-items:center; justify-content:center;">'
    '<h1 style="font-size:4.5rem;">CLUSTERIZAÇÃO E SEGMENTAÇÃO</h1>'
    '</div>',
    unsafe_allow_html=True
)

# Subtítulo
st.write(
    '<div style="display:flex; align-items:center; justify-content:center;">'
    '<h2 style="font-size:2.5rem;">Modelos de Machine Learning não supervisionados.</h2>'
    '</div>',
    unsafe_allow_html=True
)

# Divisão
st.write("---")

# Imagem do lado da explicação
col1, col2 = st.columns(2)

col1.write(
    "<p style='font-size:1.5rem;'> Esse aplicativo é uma ferramenta de algoritmos de Machine Learning para modelos não supervisionados, "
    "<strong>Clusterização (K-means e Algoritmos hierárquicos) e Segmentação (Análise RFV)</strong>.<br>"
    "Automatiza o agrupamento e entendimento de como os grupos se relacionam com as demais variáveis"
    " assim como possíveis soluções para problemas e geração de insights.</p>"
    "<p style='font-size:1.5rem;'>Permite o carregamento de dados, cria e filtra os grupos. Além de demonstrar visualmente relações entre os grupos e demais variáveis do"
    "conjunto de dados.</p>",
unsafe_allow_html=True
)

col2.write(
    '<div style="position:relative;"><iframe src="https://gifer.com/embed/7U4k" width="400" height="400" style="position:absolute;top:0;left:0;" frameBorder="0" allowFullScreen></iframe><p><a href="https://gifer.com">via GIFER</a></p></div>',
unsafe_allow_html=True
)

# Divisão
st.write("---")

st.write(
    '<h3 style="text-align:left;">Autor</h3>'
    '<ul style="list-style-type: disc; margin-left: 20px;">'
    '<li>Caio Douglas Rodrigues de Paula</li>'
    '<li><a href="https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO">GitHub</a></li>'
    '</ul>',
    unsafe_allow_html=True
)

