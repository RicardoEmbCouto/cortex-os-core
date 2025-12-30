import streamlit as st
from supabase import create_client

# O decorador @st.cache_resource impede que o app reconecte
# ao banco a cada clique, economizando recursos e acelerando o sistema.
@st.cache_resource
def get_db():
    try:
        # Busca as credenciais de forma segura no secrets.toml
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Falha Crítica de Segurança/Conexão: {e}")
        return None

db = get_db()