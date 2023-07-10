import streamlit as st
import pandas as pd
import base64
from datetime import datetime

@st.cache_data
def carregar_dados(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    st.warning("Por favor, faça upload de um arquivo .CSV para continuar.")
    return None

def calcular_recencia(df):
    """
    Função para calcular a Recência.
    """
    df['DiaCompra'] = pd.to_datetime(df['DiaCompra'])  # Converter a coluna para pd.Timestamp
    df_recencia = df.groupby(by='ID_cliente', as_index=False)['DiaCompra'].max()
    df_recencia.columns = ['ID_cliente', 'DiaUltimaCompra']
    dia_atual = pd.Timestamp(datetime.now().date())
    df_recencia['Recencia'] = df_recencia['DiaUltimaCompra'].apply(
        lambda x: (dia_atual - x).days)
    return df_recencia

def calcular_frequencia(df):
    """
    Função para calcular a Frequência.
    """
    df_frequencia = df[['ID_cliente', 'CodigoCompra']].groupby(
        'ID_cliente').count().reset_index()
    df_frequencia.columns = ['ID_cliente', 'Frequencia']
    return df_frequencia

def calcular_valor(df):
    """
    Função para calcular o Valor.
    """
    df_valor = df[['ID_cliente', 'ValorTotal']].groupby(
        'ID_cliente').sum().reset_index()
    df_valor.columns = ['ID_cliente', 'Valor']
    return df_valor

def calcular_quartis(df_RFV):
    """
    Função para calcular os quartis.
    """
    return df_RFV.quantile(q=[0.25, 0.5, 0.75]).drop('ID_cliente', axis=1)

def recencia_class(x, r, q_dict):
    """
    Função para classificar a Recência.
    """
    if x <= q_dict[r][0.25]:
        return 'A'
    elif x <= q_dict[r][0.50]:
        return 'B'
    elif x <= q_dict[r][0.75]:
        return 'C'
    else:
        return 'D'

def freq_val_class(x, fv, q_dict):
    """
    Função para classificar a Frequência ou Valor.
    """
    if x <= q_dict[fv][0.25]:
        return 'D'
    elif x <= q_dict[fv][0.50]:
        return 'C'
    elif x <= q_dict[fv][0.75]:
        return 'B'
    else:
        return 'A'

def gerar_df_rfv(df_RFV, quartis):
    """
    Função para gerar o DF RFV final com as classes.
    """
    df_RFV['R_quartil'] = df_RFV['Recencia'].apply(
        recencia_class, args=('Recencia', quartis))
    df_RFV['F_quartil'] = df_RFV['Frequencia'].apply(
        freq_val_class, args=('Frequencia', quartis))
    df_RFV['V_quartil'] = df_RFV['Valor'].apply(
        freq_val_class, args=('Valor', quartis))
    return df_RFV

def main():
    st.set_page_config(
        page_title='Previsão de Renda',
        page_icon='🧩',
        layout='wide'
    )

    # Título centralizado
    st.write(
        '<div style="display:flex; align-items:center; justify-content:center;">'
        '<h1 style="font-size:4.5rem;">Segmentação</h1>'
        '</div>',
        unsafe_allow_html=True
    )

    # Divisão
    st.write("---")

    st.sidebar.title('Carregar arquivo CSV')
    uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type="csv")

    if uploaded_file is not None:
        # Carregar os dados
        df = carregar_dados(uploaded_file)

        if df is not None:
            # Calcular a Recência, Frequência e Valor
            df_recencia = calcular_recencia(df)
            df_frequencia = calcular_frequencia(df)
            df_valor = calcular_valor(df)

            # Juntar o RFV de acordo com o cliente
            df_RFV = pd.merge(pd.merge(df_recencia, df_frequencia, on='ID_cliente'), df_valor, on='ID_cliente')

            # Exibir o DataFrame RFV na tela do usuário
            st.header("DataFrame RFV")
            st.dataframe(df_RFV)

            # Obter os quartis
            quartis_df = calcular_quartis(df_RFV)

            # Gerar o DF RFV final com as classes
            df_RFV_final = gerar_df_rfv(df_RFV, quartis_df)

            # Exibir o cabeçalho do DF RFV final
            st.header('DF RFV Final')
            st.dataframe(df_RFV_final.head())

            # Botão para fazer o download do DF RFV final
            if st.button('Download do DF RFV Final'):
                csv = df_RFV_final.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="df_rfv_final.csv">Download do DF RFV Final (CSV)</a>'
                st.markdown(href, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
