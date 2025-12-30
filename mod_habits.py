import streamlit as st
from datetime import date
from database import db

def render(user_id):
    st.markdown("<h2 class='titulo-neon'>🧬 HÁBITOS ATÔMICOS</h2>", unsafe_allow_html=True)
    
    # Criação de novo hábito
    col1, col2 = st.columns([4, 1])
    with col1:
        novo = st.text_input("Novo Hábito", placeholder="Ex: Meditar 10min por dia")
    with col2:
        if st.button("Criar Hábito", use_container_width=True):
            if novo.strip():
                db.table("habits").insert({
                    "user_id": user_id,
                    "titulo": novo.strip(),
                    "streak": 0,
                    "ultimo_check": None
                }).execute()
                st.success("Hábito criado com sucesso!")
                st.rerun()
            else:
                st.warning("Digite o nome do hábito.")

    st.divider()

    # Carrega hábitos do usuário
    habits = db.table("habits").select("*").eq("user_id", user_id).execute().data

    if not habits:
        st.info("Você ainda não tem hábitos criados. Comece agora!")
    else:
        colunas = st.columns(3)
        for i, h in enumerate(habits):
            with colunas[i % 3]:
                with st.container():
                    st.markdown(f"""
                    <div style="border:1px solid #bc13fe; padding:15px; border-radius:10px; text-align:center; background:#0f0f1a;">
                        <h4>{h['titulo']}</h4>
                        <p style="color:#00f3ff; font-size:24px; font-weight:bold;">🔥 {h['streak']} Dias</p>
                        <p style="color:#888; font-size:14px;">
                            Último check: {h['ultimo_check'] if h['ultimo_check'] else 'Nunca'}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Botões de ação: Check e Excluir
                    col_check, col_delete = st.columns([3, 1])
                    with col_check:
                        if st.button("Check ✅", key=f"check_{h['id']}", use_container_width=True):
                            db.table("habits").update({
                                "streak": h['streak'] + 1,
                                "ultimo_check": str(date.today())
                            }).eq("id", h['id']).execute()
                            st.rerun()

                    with col_delete:
                        if st.button("🗑️ Excluir", key=f"delete_{h['id']}", use_container_width=True):
                            db.table("habits").delete().eq("id", h['id']).execute()
                            st.success(f"Hábito '{h['titulo']}' excluído!")
                            st.rerun()