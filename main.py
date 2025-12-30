import streamlit as st
from auth_service import login_tatico

# Importação dos Módulos Táticos (Certifique-se que os arquivos mod_*.py existem na pasta)
import mod_dashboard
import mod_finances
import mod_tasks
import mod_habits
import mod_projects
import mod_journal
import mod_team
import mod_arsenal
import mod_content
import mod_chat
import mod_academy

# 1. Configuração Global de Elite
st.set_page_config(
    page_title="Cortex OS | Couto Industries", 
    layout="wide",
    initial_sidebar_state="expanded" # Garante que a sidebar tente abrir expandida
)

# 2. CSS Cyberpunk (Estética Néctar Dark & Neon)
st.markdown("""
    <style>
    /* Fundo Total Black */
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Títulos Neon */
    .titulo-neon {
        color: #00f3ff !important;
        text-shadow: 0 0 10px #00f3ff, 0 0 20px #00f3ff;
        font-family: 'Courier New', Courier, monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: bold;
        text-align: center;
        margin: 0;
    }
    
    /* Cards do Dashboard */
    .metric-card {
        background-color: #0d0d0d;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.1);
        margin-bottom: 10px;
    }
    .metric-value { font-size: 1.8rem; font-weight: bold; color: #00f3ff; }
    .metric-label { font-size: 0.8rem; color: #888; text-transform: uppercase; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #050505; 
        border-right: 1px solid #333; 
    }
    
    /* Inputs e Botões */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
        background-color: #121212; 
        color: #00f3ff; 
        border: 1px solid #333;
    }
    
    div.stButton > button:first-child {
        background-color: transparent; 
        color: #00f3ff; 
        border: 1px solid #00f3ff;
        width: 100%; 
        font-weight: bold; 
        text-transform: uppercase; 
        transition: 0.3s;
    }
    
    div.stButton > button:first-child:hover {
        background-color: #00f3ff; 
        color: #000000; 
        box-shadow: 0 0 15px #00f3ff;
    }
    
    /* Esconder menu padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    /* header {visibility: hidden;} */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def main():
    # Inicialização da Sessão de Segurança
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    # LÓGICA DE EXIBIÇÃO
    if not st.session_state.autenticado:
        # --- TELA DE LOGIN (Sem Sidebar) ---
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 class='titulo-neon'>🧠 CORTEX OS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#555;'>COUTO INDUSTRIES // SECURE TERMINAL</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("ID OPERACIONAL", placeholder="seu@email.com")
            senha = st.text_input("CHAVE DE ACESSO", type="password")
            
            if st.button("INICIALIZAR SISTEMA"):
                user = login_tatico(email, senha)
                if user:
                    st.session_state.autenticado = True
                    st.session_state.user_id = user.id
                    st.session_state.user_email = email
                    st.rerun() # Reinicia a página para carregar o Menu
                else:
                    st.error("ACESSO NEGADO: Credenciais inválidas.")

    else:
        # --- SISTEMA LOGADO (Com Sidebar e Módulos) ---
        
        # 1. Menu Lateral
        with st.sidebar:
            st.markdown("<h3 style='color:#00f3ff; text-align:center; margin-bottom:20px;'>MENU TÁTICO</h3>", unsafe_allow_html=True)
            
            menu = st.radio(
                "Navegação",
                [
                    "👁️ Visão Estratégica",
                    "🧠 Chat IA",
                    "🎓 Cortex Academy",
                    "✅ Tarefas",
                    "🧬 Hábitos",
                    "🏗️ Projetos",
                    "💰 Finanças",
                    "📔 Diário",
                    "📝 Produção Conteúdo",
                    "👥 Equipe Infinita",
                    "⚔️ Arsenal Prompts"
                ],
                label_visibility="collapsed"
            )
            
            st.divider()
            st.caption(f"Operador: {st.session_state.user_email}")
            
            if st.button("LOGOFF / SAIR"):
                st.session_state.autenticado = False
                st.rerun()

        # 2. Roteamento de Módulos (Carrega o arquivo correspondente)
        uid = st.session_state.user_id
        
        try:
            if menu == "👁️ Visão Estratégica": mod_dashboard.render(uid)
            elif menu == "🧠 Chat IA": mod_chat.render()
            elif menu == "🎓 Cortex Academy": mod_academy.render(uid)
            elif menu == "✅ Tarefas": mod_tasks.render(uid)
            elif menu == "🧬 Hábitos": mod_habits.render(uid)
            elif menu == "🏗️ Projetos": mod_projects.render(uid)
            elif menu == "💰 Finanças": mod_finances.render(uid)
            elif menu == "📔 Diário": mod_journal.render(uid)
            elif menu == "📝 Produção Conteúdo": mod_content.render(uid)
            elif menu == "👥 Equipe Infinita": mod_team.render(uid)
            elif menu == "⚔️ Arsenal Prompts": mod_arsenal.render(uid)
            
        except Exception as e:
            st.error(f"Erro ao carregar módulo: {e}")
            st.info("Verifique se o arquivo do módulo existe na pasta e se o banco de dados está conectado.")

if __name__ == "__main__":
    main()