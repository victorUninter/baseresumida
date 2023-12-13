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
import sqlite3
import openpyxl
from passlib.hash import bcrypt

base=pd.read_excel('EQUIPE COMPLETA COB E TELE.xlsx')

# Configuração do banco de dados
con = sqlite3.connect('bancoDados.db')
cur = con.cursor()

base.to_sql('colaboradores',con,index=False,if_exists='replace')

cur.execute("INSERT INTO colaboradores (Senha) VALUES('')")
con.commit()

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="Relatório Metas",
        page_icon="/workspaces/baseresumida/imagens/goal_3310111.png",
        layout="wide",
        initial_sidebar_state="expanded")

    def cadastro(username, password):
        cur.execute("SELECT * FROM colaboradores WHERE MATRICULA = ?", (username,))
        result = cur.fetchone()

        if result and bcrypt.verify(password, result[1]):  # Verifique a senha com hash usando a biblioteca bcrypt
            return result
        return ""

    # Mantenha a conexão com o banco de dados aberta durante a execução
    def verifica_matricula(username):

        cur.execute("SELECT * FROM colaboradores WHERE MATRICULA = ?", (username,))
        usu = cur.fetchone()

        # Verifica se o usuário foi encontrado
        if usu:
            cur.execute("SELECT Senha FROM colaboradores WHERE MATRICULA = ?", (username,))
            sen = cur.fetchone()

            # Verifica se a senha está vazia ou nula
            if sen:
                # Usuário encontrado e senha vazia ou nula
                print("Usuário encontrado e a senha está vazia ou nula.")
            else:
                # Senha não está vazia ou nula
                print("Usuário encontrado, mas a senha não está vazia ou nula.")
        else:
            # Usuário não encontrado
            print("Usuário não encontrado.")

        # if result and bcrypt.verify(password, result[1]):  # Verifique a senha com hash usando a biblioteca bcrypt
        return (usu,sen[0])
        # return None
    
    def pagina_login():
        st.title("Login")

        # Entradas para o nome de usuário e senha
        username = st.text_input("Matrícula")
        password = st.text_input("Senha", type="password")

     # Crie duas colunas para os botões
        col1, col2, col3,col4,col5 = st.columns(5)

        # Botão de login
        if col1.button("Login"):
            usuario = verifica_credenciais(username, password)
            if usuario:
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("Credenciais inválidas")

        # Botão de cadastro
        if col2.button("Cadastro"):
            usuario,senha = verifica_matricula(username)
            if usuario and senha==0:
                cadastro(username, password)
            else:
                st.error(f"Usuário {usuario[0]} já cadastrado, Procure o Administrativo para alterar a senha")

    def pagina_principal():
        st.title("Página Principal")
        st.success("Login bem-sucedido!")

    # Verifica se o usuário está logado
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Se o usuário não estiver logado, mostre a página de login
    if not st.session_state.logged_in:
        pagina_login()
    # Se o usuário estiver logado, mostre a página principal
    else:
        pagina_principal()

if __name__ == "__main__":
    run()