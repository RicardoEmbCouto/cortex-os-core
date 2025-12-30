import streamlit as st
import pandas as pd
from database import db

def render(user_id):
    st.markdown("<h2 class='titulo-neon'>👁️ VISÃO ESTRATÉGICA</h2>", unsafe_allow_html=True)
    st.divider()
    
    # Cálculos
    tasks = db.table("tasks").select("*").eq("user_id", user_id).execute().data
    total = len(tasks)
    done = len([t for t in tasks if t['concluido']])
    taxa = int((done / total * 100)) if total > 0 else 0
    
    finances = db.table("finances").select("*").eq("user_id", user_id).execute().data
    entrada = sum([float(f['valor']) for f in finances if f['tipo'] == 'Entrada'])
    saida = sum([float(f['valor']) for f in finances if f['tipo'] == 'Saída'])
    saldo = entrada - saida
    lucratividade = int(((entrada - saida) / entrada * 100)) if entrada > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"""<div class="metric-card"><div class="metric-value">{taxa}%</div><div class="metric-label">Conclusão Tarefas</div></div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class="metric-card"><div class="metric-value">{done * 10}XP</div><div class="metric-label">Produtividade</div></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="metric-card"><div class="metric-value">{lucratividade}%</div><div class="metric-label">Margem Lucro</div></div>""", unsafe_allow_html=True)
    c4.markdown(f"""<div class="metric-card"><div class="metric-value">R$ {saldo:.0f}</div><div class="metric-label">Saldo Caixa</div></div>""", unsafe_allow_html=True)
    
    st.divider()
    st.info("SISTEMA ONLINE. Nenhuma anomalia detectada na operação.")