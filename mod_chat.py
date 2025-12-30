import streamlit as st
from database import db
from ai_service import pensar_como_cortex

def render():
    st.markdown("<h2 class='titulo-neon'>🧠 CORTEX CHAT</h2>", unsafe_allow_html=True)
    user_id = st.session_state.get('user_id')
    
    # 1. Carrega Histórico Visual
    try:
        # Pega as últimas 50 mensagens para não pesar
        msgs = db.table("chat_history").select("*").eq("user_id", user_id).eq("session_id", "default").order("created_at", desc=False).limit(50).execute().data
    except:
        msgs = []

    # 2. Exibe na tela
    for m in msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # 3. Nova mensagem
    if prompt := st.chat_input("Comando..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Processando..."):
                res = pensar_como_cortex(prompt, user_id=user_id, session_id="default")
                st.markdown(res)
