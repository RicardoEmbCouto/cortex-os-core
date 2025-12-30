import streamlit as st
from database import db

def render(user_id):
    st.markdown("<h2 class='titulo-neon'>👥 EQUIPE INFINITA</h2>", unsafe_allow_html=True)
    
    # --- CATÁLOGO DE PERSONAS (O "LIVRO" EQUIPE INFINITA) ---
    CATALOGO_PERSONAS = {
        "Personalizado (Criar do Zero)": {
            "cargo": "",
            "prompt": ""
        },
        "💀 Copywriter Agressivo": {
            "cargo": "Especialista em Vendas",
            "prompt": "Atue como um Copywriter Sênior de Resposta Direta (Direct Response). Seu tom é agressivo, polêmico e focado em converter leads frios. Use gatilhos mentais de escassez, urgência e autoridade. Seus textos devem ter frases curtas, punchlines fortes e foco total na dor do cliente."
        },
        "🧠 Estrategista de Lançamentos": {
            "cargo": "Estrategista Digital",
            "prompt": "Você é um Estrategista de Lançamentos Digitais com experiência em múltiplos 7 dígitos. Você pensa em funis de vendas, escada de valor e jornada do cliente. Seu foco é maximizar o LTV (Lifetime Value) e criar ofertas irresistíveis."
        },
        "🎨 Diretor de Criação (Visual)": {
            "cargo": "Designer & Branding",
            "prompt": "Atue como um Diretor de Arte visionário. Você não cria imagens, mas descreve conceitos visuais detalhados, paletas de cores cyberpunk/neon e composições cinematográficas para guiar a criação de posts e vídeos. Seu estilo é minimalista e futurista."
        },
        "💰 Closer de Vendas (Negociação)": {
            "cargo": "Vendedor",
            "prompt": "Você é um Closer de Vendas especialista em quebrar objeções. Nenhuma resposta é 'não' para você. Você usa o método socrático para fazer o cliente perceber que precisa do produto. Seu tom é confiante, empático mas firme no fechamento."
        },
        "📊 Analista de Dados (Growth)": {
            "cargo": "Data Scientist",
            "prompt": "Você é um Analista de Growth Hacking. Ignore emoções, foque nos números. Analise métricas, proponha testes A/B e encontre gargalos na operação. Suas respostas devem ser baseadas em lógica, ROI e otimização de processos."
        },
        "🧘 Mentor de Alta Performance": {
            "cargo": "Coach Executivo",
            "prompt": "Você é um treinador de elite para CEOs. Seu objetivo é garantir que o usuário mantenha o foco, a disciplina e a clareza mental. Seja duro quando necessário (estilo David Goggins) e encorajador quando houver progresso."
        }
    }

    tab1, tab2 = st.tabs(["➕ Contratar Novo Agente", "⚙️ Gerenciar Equipe Ativa"])
    
    # --- ABA 1: CONTRATAÇÃO ---
    with tab1:
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.info("📖 Catálogo da Equipe Infinita")
            escolha = st.selectbox(
                "Escolha o Especialista:", 
                list(CATALOGO_PERSONAS.keys())
            )
            
            # Puxa os dados do catálogo
            dados_pre = CATALOGO_PERSONAS[escolha]
            
        with c2:
            st.markdown("### Configuração do Contrato")
            
            # Se for personalizado, campos vazios. Se for catálogo, preenche automático.
            nome_padrao = escolha if escolha != "Personalizado (Criar do Zero)" else ""
            
            nome = st.text_input("Nome do Agente", value=nome_padrao)
            cargo = st.text_input("Cargo / Função", value=dados_pre["cargo"])
            prompt = st.text_area("Prompt do Sistema (Personalidade)", value=dados_pre["prompt"], height=200)
            
            if st.button("CONTRATAR AGENTE 🤝"):
                if nome and prompt:
                    try:
                        db.table("infinite_team").insert({
                            "user_id": user_id, 
                            "nome": nome, 
                            "cargo": cargo, 
                            "prompt_especializado": prompt
                        }).execute()
                        st.success(f"Agente **{nome}** contratado e pronto para operar!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erro na contratação: {e}")
                else:
                    st.warning("Preencha o nome e o prompt para contratar.")

    # --- ABA 2: GERENCIAMENTO ---
    with tab2:
        st.markdown("### 🧬 Sua Equipe")
        
        # Busca no banco
        try:
            agentes = db.table("infinite_team").select("*").eq("user_id", user_id).execute().data
            
            if not agentes:
                st.info("Sua equipe está vazia. Vá na aba 'Contratar' para trazer novos talentos.")
            
            for a in agentes:
                with st.container():
                    col_info, col_action = st.columns([4, 1])
                    
                    with col_info:
                        st.markdown(f"""
                        <div style="border-left: 3px solid #bc13fe; padding-left: 10px; margin-bottom: 10px;">
                            <h4 style="margin:0; color:#00f3ff;">{a['nome']}</h4>
                            <span style="color:#888; font-size:0.8rem;">{a['cargo']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        with st.expander("Ver Prompt"):
                            st.code(a['prompt_especializado'])

                    with col_action:
                        # Botão de Ativar
                        if st.button("ATIVAR 🧠", key=f"btn_atv_{a['id']}"):
                            st.session_state['agente_ativo'] = a['prompt_especializado']
                            st.session_state['nome_agente_ativo'] = a['nome']
                            st.toast(f"MINDSET ATIVADO: {a['nome']}")
                        
                        # Botão de Demitir
                        if st.button("Demitir 🗑️", key=f"btn_del_{a['id']}"):
                            db.table("infinite_team").delete().eq("id", a['id']).execute()
                            st.rerun()
                            
                st.divider()

        except Exception as e:
            st.error("Erro ao carregar equipe. Verifique a conexão.")