import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import datetime as dt
import re
from unidecode import unidecode 
import math
import numpy as np
import time
import os

LOGGER = get_logger(__name__)

def run():
  st.set_page_config(
      page_title="Relatório Metas",
      page_icon="/workspaces/baseresumida/imagens/goal_3310111.png",
      layout="wide",
      initial_sidebar_state="expanded")

  # Campo para entrada de caminho de arquivo
  uploaded_file = st.text_input("Informe o caminho do arquivo CSV")

  # Campo opcional para upload de arquivo
  # uploaded_file = st.file_uploader("Faça o upload do arquivo da Carteira (CSV) - Opcional", type=["csv"])

  # Combinação dos caminhos, dando prioridade ao upload se disponível
  caminho_entrada = uploaded_file
  caminho_entrada=caminho_entrada.replace('"',"")
  def process_item(item):
      item_str = str(item)
      if len(item_str) > 2 and item_str[2].isdigit() and int(item_str[2]) <= 5:
          return 0
      else:
          if len(item_str) > 2 and item_str[2].isdigit() and int(item_str[3]) <= 5:
              return 0
      return item

  def ajustaCel(item):
      item_str = str(item)
      if item_str[:2] == '41':
          return item_str[2:]
      else:
          return item_str

  def cadastrar(caminho_entrada):
      if caminho_entrada:
          base = pd.read_csv(caminho_entrada, sep=";")

          total_rows = len(base)

          # Criando uma barra de progresso com Streamlit
          progress_text = "Processo em andamento. Por favor aguarde."
          my_bar = st.progress(0, text=progress_text)

          base['valor'] = base['valor'].str.replace(',', '.').astype(float)

          # Cria uma nova coluna com a contagem de títulos por código
          base['Qtd de Títulos'] = base.groupby('Codigo_Aluno')['id_titulo'].transform('count')

          base['valor'] = base.groupby('Codigo_Aluno')['valor'].transform('sum')

          ##################################################################################
          # Separa em duas planilhas e salva em uma
          data = dt.datetime.now().strftime("%d.%m.%y")
          basedividida = math.ceil(base.shape[0] / 2)
          baseResumo1, baseResumo2 = base.iloc[:basedividida, :], base.iloc[basedividida:, :]
          nomeArquivo = (f'CARTEIRA COBRANÇA REF {data} NOVO MODELO.csv')
          baseResumo1.to_csv(f"CARTEIRA COBRANÇA REF {data}- NOVO MODELO.csv", sep=";")
          baseResumo2.to_csv(f"CARTEIRA COBRANÇA REF {data}- NOVO MODELO2.csv", sep=";")

          ##################################################################################

          # Junta as colunas fone1 e cel
          base['fone1'] = base['fone1'].fillna(base['cel'])
          base['fone1'] = base['fone1'].str.cat(base['cel'], sep=';').str.replace(";;", ";")
          base.loc[(base['fone1'].isna()) & (base['cel'].isna()), 'fone1'] = 0

          base2 = base.drop_duplicates(subset='Codigo_Aluno')

          base2['telefone'] = base2['fone1'].str.split(';')
          base2 = base2.explode('telefone')

          base2['nome'] = base2['nome'].apply(unidecode).str.replace(r'\W', ' ').str.replace(r"'", '').str.replace(
              ";", "").str.replace('`', "").str.rstrip().str[0:60]

          base2['telefone'] = base2['telefone'].str.replace('(', "").str.replace(')', "").str.replace(';', "").str.replace(
              ' ', "").str.replace('-', "")

          base2['telefone'] = base2['telefone'].apply(process_item)
          base2.loc[(base2['telefone'] == ""), 'telefone'] = 0
          base2.loc[(base2['telefone'].isnull()), 'telefone'] = 0
          basezeros = base2[(base2['telefone'] == 0)]
          baseSemzeros = base2[(base2['telefone'] != 0)]

          baseSemzeros = baseSemzeros.drop_duplicates(subset='telefone')

          baseResumida2 = pd.concat([baseSemzeros, basezeros])
          baseResumida2 = baseResumida2.drop_duplicates(subset='Codigo_Aluno')

          baseResumida2 = baseResumida2[
              ['codigo', 'nome', 'cpf', 'email', 'fone1', 'data_vencimento', 'valor', 'Qtd de Títulos', 'id_titulo',
              'Tipo_Titulo', 'Situacao_Matricula', 'empresa_cobranca', 'Codigo_Aluno', 'telefone', 'Nome_Local']]

          baseResumida2['qtdCarct'] = baseResumida2['telefone'].apply(lambda x: len(str(x)))

          # baseResumida2=baseResumida2[baseResumida2['telefone'].notna()]
          baseResumida2['telefone'] = baseResumida2['telefone'].apply(
              lambda x: x[:2] + "9" + x[2:] if len(str(x)) == 10 else x)
          baseResumida2['telefone'] = baseResumida2['telefone'].apply(lambda x: x[1:] if len(str(x)) == 12 else x)

          baseResumida2['telefone'] = baseResumida2['telefone'].apply(ajustaCel)

          baseResumida2 = baseResumida2.drop('qtdCarct', axis=1)

          data = dt.datetime.now().strftime("%d%m%y")
          baseResumida2.to_excel(f"Y:\COBRANCA\CARLOS\BASE RESUMIDA\REF {data} teste.xlsx", index=False)

          for percent_complete in range(100):
              time.sleep(0.01)
              my_bar.progress(percent_complete + 1, text=progress_text)
          time.sleep(1)
          my_bar.empty()

          if caminho_entrada:
              st.success('Base criada com sucesso!', icon="✅")        
              st.dataframe(baseResumida2.head())
              baseResumida2.shape
          else:
              st.info('Preencha o caminho da base', icon="ℹ️")
          return baseResumida2
      else:
          st.info('Faça o upload do arquivo da Carteira', icon="ℹ️")
  clique = st.button("Gerar", type="primary")
  if clique == True and uploaded_file != "":
      cadastrar(caminho_entrada)
  elif clique == True and uploaded_file == "":
      st.info('Preencha o caminho da base', icon="ℹ️")

if __name__ == "__main__":
    run()
