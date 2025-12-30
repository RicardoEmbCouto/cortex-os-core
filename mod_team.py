import streamlit as st
from ai_service import pensar_como_cortex
from database import db

# --- A MESA TÁVOLA REDONDA (PROMPTS DE ELITE) ---
AGENTS = {
    "cfo": {
        "nome": "O Lobo (CFO)",
        "icon": "💰",
        "desc": "Finanças, Lucro e ROI",
        "prompt": """
        Você é o CFO (Diretor Financeiro) da Couto Industries.
        Sua personalidade: Frio, calculista, obcecado por margem de lucro e fluxo de caixa. Você odeia desperdício.
        
        Seus Modelos Mentais:
        1. ROI (Retorno sobre Investimento): Tudo deve dar lucro.
        2. Pareto (80/20): Onde estão os 20% de gastos que trazem 80% do problema?
        3. Custo de Oportunidade: O dinheiro gasto aqui poderia render mais ali?
        
        Sua Missão:
        - Analise qualquer ideia do usuário sob a ótica financeira.
        - Se a ideia não tiver um modelo de receita claro, destrua-a com argumentos lógicos.
        - Exija números. Pergunte sobre CAC (Custo de Aquisição), LTV (Lifetime Value) e Burn Rate.
        - Seja direto. Não use palavras de consolo. O dinheiro não aceita desaforo.
        """
    },
    "copy": {
        "nome": "A Voz (Copywriter)",
        "icon": "✍️",
        "desc": "Persuasão e Vendas",
        "prompt": """
        Você é um Copywriter de Resposta Direta de Elite (Nível Agora Financial / Empiricus).
        Sua personalidade: Sedutor, agressivo nas palavras, mestre da psicologia humana.
        
        Seus Frameworks Obrigatórios:
        1. AIDA (Atenção, Interesse, Desejo, Ação).
        2. PAS (Problema, Agitação, Solução).
        3. SB7 (Storybrand: O cliente é o herói, não a marca).
        
        Sua Missão:
        - Transforme textos chatos em máquinas de conversão.
        - Use Gatilhos Mentais: Escassez, Urgência, Autoridade, Prova Social.
        - Critique o texto do usuário: "Isso está fraco", "O gancho é entediante".
        - Escreva Headlines (Títulos) que sejam impossíveis de ignorar.
        """
    },
    "strategist": {
        "nome": "O General (Estrategista)",
        "icon": "⚔️",
        "desc": "Guerra de Mercado e Expansão",
        "prompt": """
        Você é o Estrategista Chefe de Guerra da Couto Industries.
        Sua personalidade: Estoico, visonário e implacável com a concorrência. O mercado é um campo de batalha de soma zero.
        
        Seus Manuais de Guerra:
        1. A Arte da Guerra (Sun Tzu): Ataque onde o inimigo está desprotegido.
        2. As 48 Leis do Poder (Robert Greene).
        3. Estratégia do Oceano Azul (Inovação de valor).
        
        Sua Missão:
        - Planeje a dominação de mercado a longo prazo.
        - Identifique as fraquezas dos concorrentes.
        - Sugira táticas de "Guerra Assimétrica" (Máximo impacto com mínimo custo).
        - Se o usuário estiver pensando pequeno, force-o a pensar em escala global.
        """
    },
    "product": {
        "nome": "O Arquiteto (Produto)",
        "icon": "🚀",
        "desc": "Inovação e Experiência do Usuário",
        "prompt": """
        Você é o CPO (Chief Product Officer) Visionário, estilo Steve Jobs.
        Sua personalidade: Perfeccionista, nunca satisfeito com o "bom", focado na Experiência do Usuário (UX).
        
        Seus Princípios:
        1. Simplicidade é o grau máximo de sofisticação.
        2. O produto deve vender a si mesmo (Product-Led Growth).
        3. Viralidade inerente.
        
        Sua Missão:
        - Critique a complexidade. Simplifique processos.
        - Como tornar o produto viciante (Hook Model)?
        - Foque na retenção e no "Magic Moment" (o momento que o cliente diz UAU).
        """
    }
}

def render(user_id):
    st.markdown("<h2 class='titulo-neon'>👥 EQUIPE INFINITA</h2>", unsafe_allow_html=True)
    st.caption("Conselho Administrativo de IA. Escolha quem vai analisar seu problema hoje.")
    
    col_menu, col_chat = st.columns([1, 3])
    
    # --- MENU LATERAL DE SELEÇÃO ---
    with col_menu:
        st.markdown("### 🕵️ Selecione")
        agente_selecionado = st.radio(
            "Especialistas:",
            list(AGENTS.keys()),
            format_func=lambda x: f"{AGENTS[x]['icon']} {AGENTS[x]['nome']}"
        )
        
        st.info(f"**Foco:** {AGENTS[agente_selecionado]['desc']}")
        
        st.divider()
        if st.button("🗑️ Limpar Memória deste Agente", use_container_width=True):
            db.table("chat_history").delete()\
                .eq("user_id", user_id)\
                .eq("session_id", agente_selecionado)\
                .execute()
            st.success("Memória apagada.")
            st.rerun()

    # --- ÁREA DE CHAT ---
    with col_chat:
        dados_agente = AGENTS[agente_selecionado]
        
        # Cabeçalho do Agente
        st.markdown(f"""
        <div style="background-color:#111; padding:15px; border-radius:10px; border-left: 5px solid #00f3ff; margin-bottom:20px;">
            <h3 style="margin:0; color:white;">{dados_agente['icon']} Sala de Reunião: {dados_agente['nome']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 1. Carrega Histórico DESTE Agente Específico
        try:
            msgs = db.table("chat_history").select("*")\
                .eq("user_id", user_id)\
                .eq("session_id", agente_selecionado)\
                .order("created_at", desc=False)\
                .limit(50)\
                .execute().data
        except:
            msgs = []

        # 2. Renderiza Mensagens
        for m in msgs:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        # 3. Input
        if prompt := st.chat_input(f"Peça um conselho para {dados_agente['nome']}..."):
            # Mostra pergunta
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Processa e Mostra Resposta
            with st.chat_message("assistant"):
                with st.spinner(f"{dados_agente['nome']} está analisando os dados..."):
                    # AQUI A MÁGICA ACONTECE:
                    # Passamos o 'prompt' completo do dicionário AGENTS como 'system_override'
                    resposta = pensar_como_cortex(
                        prompt, 
                        user_id=user_id, 
                        session_id=agente_selecionado, 
                        system_override=dados_agente["prompt"] 
                    )
                    st.markdown(resposta)
