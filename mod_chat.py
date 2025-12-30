import streamlit as st
from ai_service import pensar_como_cortex

def render():
    st.markdown("<h2 class='titulo-neon'>🧠 CORTEX CHAT</h2>", unsafe_allow_html=True)
    
    # Recupera o ID do usuário da sessão (Isso é CRÍTICO para salvar no banco)
    # Se não houver ID, definimos como None (o que impede gravações no banco)
    user_id = st.session_state.get('user_id')

    if 'agente_ativo' in st.session_state:
        st.info(f"⚠️ MODO AGENTE ATIVO")
        
    user_input = st.chat_input("Ordem para o sistema...")
    
    if user_input:
        # Exibe mensagem do usuário
        with st.chat_message("user"): 
            st.write(user_input)
            
        # Processa resposta
        with st.chat_message("assistant"):
            with st.spinner("Processando comando tático..."):
                ctx = st.session_state.get('agente_ativo', "")
                prompt_final = f"{ctx}\n\nUsuário: {user_input}" if ctx else user_input
                
                # --- A CORREÇÃO ESTÁ AQUI ---
                # Passamos o user_id para que o ai_service possa executar SQL
                res = pensar_como_cortex(prompt_final, user_id=user_id)
                
                st.write(res)
                
                # Se a resposta indicar sucesso financeiro, forçamos um reload visual sutil
                if "✅" in str(res) and "registrado" in str(res).lower():
                    st.toast("Transação Financeira Confirmada.", icon="💰")