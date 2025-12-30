import streamlit as st
from database import db
from datetime import date

def render(user_id):
    st.markdown("<h2 class='titulo-neon'>🏗️ GESTÃO DE PROJETOS</h2>", unsafe_allow_html=True)
    
    # --- NOVO PROJETO (MODAL/EXPANDER) ---
    with st.expander("➕ INICIAR NOVO PROJETO MACRO"):
        with st.form("form_projeto"):
            nome = st.text_input("Nome do Projeto (Ex: Lançamento Black Friday)")
            desc = st.text_area("Descrição Estratégica")
            c1, c2 = st.columns(2)
            with c1:
                prazo = st.date_input("Data Limite (Deadline)")
            with c2:
                prio = st.selectbox("Prioridade", ["Alta 🔥", "Média ⚠️", "Normal 💤"])
            
            if st.form_submit_button("CRIAR ESTRUTURA"):
                db.table("projects").insert({
                    "user_id": user_id,
                    "nome": nome,
                    "descricao": desc,
                    "data_final": str(prazo),
                    "prioridade": prio,
                    "status": "Em Planejamento"
                }).execute()
                st.toast("Projeto iniciado. Hora de executar.")
                st.rerun()

    st.divider()

    # --- KANBAN BOARD SIMPLIFICADO ---
    # Busca projetos
    projs = db.table("projects").select("*").eq("user_id", user_id).execute().data

    if not projs:
        st.info("Nenhum projeto estratégico em andamento.")
    else:
        # Colunas do Kanban
        col_plan, col_exec, col_done = st.columns(3)
        
        with col_plan:
            st.markdown("<h4 style='text-align:center; color:#888;'>📝 PLANEJAMENTO</h4>", unsafe_allow_html=True)
            for p in [x for x in projs if x['status'] == 'Em Planejamento']:
                render_card(p)

        with col_exec:
            st.markdown("<h4 style='text-align:center; color:#00f3ff;'>🔥 EM EXECUÇÃO</h4>", unsafe_allow_html=True)
            for p in [x for x in projs if x['status'] == 'Em Execução']:
                render_card(p, active=True)

        with col_done:
            st.markdown("<h4 style='text-align:center; color:#00ff00;'>✅ CONCLUÍDO</h4>", unsafe_allow_html=True)
            for p in [x for x in projs if x['status'] == 'Concluído']:
                render_card(p, done=True)

def render_card(projeto, active=False, done=False):
    """Renderiza um card de projeto com controles de movimento"""
    cor_borda = "#00ff00" if done else "#00f3ff" if active else "#555"
    
    st.markdown(f"""
    <div style="border: 1px solid {cor_borda}; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #0d0d0d;">
        <strong style="font-size:1.1rem;">{projeto['nome']}</strong><br>
        <span style="font-size:0.8rem; color:#aaa;">📅 {projeto['data_final']}</span>
        <p style="font-size:0.9rem; margin-top:5px;">{projeto.get('descricao', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Controles de Movimento
    c1, c2 = st.columns(2)
    with c1:
        if not done:
            if st.button(" avançar ➡️", key=f"adv_{projeto['id']}"):
                prox_status = "Em Execução" if projeto['status'] == "Em Planejamento" else "Concluído"
                db.table("projects").update({"status": prox_status}).eq("id", projeto['id']).execute()
                st.rerun()
    with c2:
        if st.button("🗑️", key=f"del_proj_{projeto['id']}"):
            db.table("projects").delete().eq("id", projeto['id']).execute()
            st.rerun()