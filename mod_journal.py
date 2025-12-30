import streamlit as st
from database import db

def render(user_id):
    st.markdown("<h2 class='titulo-neon'>📔 DIÁRIO DE BORDO</h2>", unsafe_allow_html=True)
    
    # Área para novo registro
    texto = st.text_area("Registro do Dia", height=200, placeholder="Como foi o progresso hoje? Anote tudo: vitórias, lições, pendências...")
    
    if st.button("SALVAR NA MEMÓRIA"):
        if texto.strip():
            db.table("journal").insert({
                "user_id": user_id,
                "conteudo": texto
            }).execute()
            st.success("Salvo na memória. Registrado para sempre.")
            st.rerun()
        else:
            st.warning("Escreva algo antes de salvar.")
    
    # Histórico recente (últimos 5 registros)
    st.markdown("### Histórico Recente")
    
    try:
        logs = db.table("journal") \
                 .select("id, conteudo, created_at") \
                 .eq("user_id", user_id) \
                 .order("created_at", desc=True) \
                 .limit(5) \
                 .execute().data
        
        if logs:
            for log in logs:
                data_formatada = log['created_at'].split('T')[0]  # Pega só a data (YYYY-MM-DD)
                hora_formatada = log['created_at'].split('T')[1][:5]  # Pega hora:minuto
                
                st.markdown(f"**{data_formatada} às {hora_formatada}**")
                st.text_area(
                    label="Registro",
                    value=log['conteudo'],
                    height=120,
                    disabled=True,
                    key=f"journal_{log['id']}"
                )
                st.divider()
        else:
            st.info("Nenhum registro ainda. Comece a anotar acima.")
            
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {str(e)}")
        st.info("Verifique se a tabela 'journal' existe e tem as colunas: id, user_id, conteudo, created_at")