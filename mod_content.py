import streamlit as st
from database import db
from ai_service import pensar_como_cortex  # Importa o serviço com OpenRouter/DeepSeek (sua chave intacta)

def render(user_id):
    st.markdown("<h2 class='titulo-neon'>📝 ESTÚDIO DE CRIAÇÃO</h2>", unsafe_allow_html=True)
    
    col_input, col_edit = st.columns([1, 2])
    
    with col_input:
        st.markdown("### Briefing")
        tema = st.text_area("Tema do Conteúdo", height=150, placeholder="Ex: Live TikTok maternidade cristã acolhedora baseada em provérbios")
        plat = st.selectbox("Plataforma", ["Instagram", "LinkedIn", "YouTube", "Blog", "TikTok"])
        
        tom = st.selectbox(
            "Tom desejado",
            [
                "Agressivo e provocativo (vendas diretas, alta conversão)",
                "Acolhedor e inspirador (maternidade, fé, desenvolvimento pessoal)",
                "Profissional e autoritário (negócios, consultoria)",
                "Amigável e conversacional (relacionamento com audiência)",
                "Humorístico e leve (entretenimento, memes)",
                "Educativo e didático (ensino, tutoriais)"
            ]
        )
        
        if st.button("GERAR ROTEIRO PRONTO ⚡"):
            if tema.strip():
                with st.spinner("Gerando roteiro completo pronto para gravação..."):
                    # Monta prompt completo com tom e estrutura
                    prompt_completo = f"""
                    Crie um roteiro completo e pronto para gravação de Reel ou Live no {plat} sobre o tema: {tema}.
                    Use tom {tom}.
                    Estrutura obrigatória para gravação:
                    1. Gancho forte (3-5 linhas que prendem nos primeiros 3 segundos)
                    2. Corpo principal (emoção, valor, prova social, versículos bíblicos se aplicável)
                    3. CTA claro e urgente (comente, salve, compartilhe, clique no link)
                    Texto curto (30-60 segundos), impactante, natural e pronto para falar na câmera. Sem JSON, sem explicação, sem feedback. Apenas o roteiro puro.
                    """
                    
                    # Chama o ai_service (gera o roteiro real)
                    roteiro_gerado = pensar_como_cortex(prompt_completo, user_id=user_id)
                    
                    st.session_state['conteudo_temp'] = roteiro_gerado
                    st.session_state['titulo_temp'] = f"Roteiro IA - {tema[:50]}..."
                    st.success("Roteiro gerado e salvo! Pronto para gravação no Editor abaixo.")
            else:
                st.warning("Digite o tema antes de gerar.")
        
        # Fallback Gemini Free (se API falhar)
        st.markdown("---")
        st.info("Se a geração falhar, continue no Gemini Free (ilimitado):")
        st.link_button(
            label="ABRIR GEMINI FREE (nova aba)",
            url="https://gemini.google.com",
            use_container_width=True,
            type="secondary"
        )

    with col_edit:
        st.markdown("### Editor - Roteiro Pronto para Gravação")
        texto = st.text_area("Conteúdo (copie e grave direto)", value=st.session_state.get('conteudo_temp', ""), height=400)
        
        titulo = st.text_input("Título para Salvar", value=st.session_state.get('titulo_temp', ""))
        
        if st.button("SALVAR NA BIBLIOTECA"):
            if texto.strip() and titulo.strip():
                db.table("content_production").insert({
                    "user_id": user_id,
                    "titulo": titulo,
                    "plataforma": plat,
                    "conteudo": texto,
                    "status": "Rascunho"
                }).execute()
                st.success("Salvo na biblioteca!")
                st.session_state['conteudo_temp'] = ""
                st.session_state['titulo_temp'] = ""
            else:
                st.warning("Preencha título e conteúdo antes de salvar.")
        
        st.info("O roteiro acima está 100% pronto para você gravar o Reel ou Live. Copie, ajuste o tom de voz e grave!")