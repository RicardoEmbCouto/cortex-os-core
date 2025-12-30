import streamlit as st
from database import db

def render(user_id):
    st.markdown("<h2 class='titulo-neon'>✅ TAREFAS TÁTICAS</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([3, 1])
    with c1:
        nova = st.text_input("Nova Missão", label_visibility="collapsed", placeholder="Digite a tarefa...")
    with c2:
        if st.button("ADICIONAR"):
            if nova:
                db.table("tasks").insert({"user_id": user_id, "titulo": nova}).execute()
                st.rerun()

    tasks = db.table("tasks").select("*").eq("user_id", user_id).order("created_at", desc=True).execute().data
    for t in tasks:
        col_a, col_b, col_c = st.columns([0.1, 0.8, 0.1])
        with col_a:
            check = st.checkbox("", value=t['concluido'], key=t['id'])
        with col_b:
            st.write(f"~~{t['titulo']}~~" if t['concluido'] else t['titulo'])
        with col_c:
            if st.button("🗑️", key=f"del_{t['id']}"):
                db.table("tasks").delete().eq("id", t['id']).execute()
                st.rerun()
        
        if check != t['concluido']:
            db.table("tasks").update({"concluido": check}).eq("id", t['id']).execute()
            st.rerun()