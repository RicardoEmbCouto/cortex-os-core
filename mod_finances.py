import streamlit as st
import pandas as pd
import plotly.express as px
from database import db
from datetime import datetime

def render(user_id):
    st.markdown("<h2 class='titulo-neon'>💰 CENTRAL FINANCEIRA GLOBAL</h2>", unsafe_allow_html=True)
    
    # RECUPERAÇÃO DE DADOS
    try:
        response = db.table("finances").select("*").eq("user_id", user_id).order("data_transacao", desc=False).execute()
        dados = response.data
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        dados = []

    # NOVO LANÇAMENTO
    with st.expander("💸 NOVO LANÇAMENTO", expanded=False):
        c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
        
        with c1:
            data_mov = st.date_input("Data", value=datetime.now(), format="DD/MM/YYYY")
        with c2:
            tipo = st.selectbox("Tipo", ["Saída", "Entrada"])
        with c3:
            valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        with c4:
            desc = st.text_input("Descrição")
            
        if st.button("REGISTRAR", use_container_width=True):
            if valor > 0:
                db.table("finances").insert({
                    "user_id": user_id,
                    "tipo": tipo,
                    "valor": valor,
                    "descricao": desc,
                    "categoria": "Manual",
                    "data_transacao": str(data_mov)
                }).execute()
                st.success("Registrado!")
                st.rerun()

    st.divider()

    if dados:
        df = pd.DataFrame(dados)
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        df['data_transacao'] = pd.to_datetime(df['data_transacao'], errors='coerce', dayfirst=True)
        df = df.dropna(subset=['data_transacao'])
        
        # FILTROS
        anos = sorted(df['data_transacao'].dt.year.unique())
        meses = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                 7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_ano = st.selectbox("Ano", ["Todos"] + list(anos))
        with col_f2:
            filtro_mes = st.selectbox("Mês", ["Todos"] + [f"{k:02d}-{meses[k]}" for k in meses])
        
        if filtro_ano != "Todos":
            df = df[df['data_transacao'].dt.year == int(filtro_ano)]
        if filtro_mes != "Todos":
            mes_num = int(filtro_mes.split('-')[0])
            df = df[df['data_transacao'].dt.month == mes_num]
        
        # Agrupamento mensal para LINHA
        df_mensal = df.groupby([df['data_transacao'].dt.strftime('%Y-%m'), 'tipo'])['valor'].sum().reset_index()
        df_mensal.columns = ['mes_ano', 'tipo', 'valor']
        df_mensal = df_mensal.sort_values('mes_ano')
        
        # GRÁFICO: LINHA MENSAL + PONTOS DIÁRIOS
        st.markdown("### 📈 Controle Diário e Mensal")
        
        fig = px.line(
            df_mensal,
            x='mes_ano',
            y='valor',
            color='tipo',
            markers=True,
            line_shape='linear',
            color_discrete_map={'Entrada': '#00ff88', 'Saída': '#ff0055'},
            template="plotly_dark",
            title="Tendência Mensal (linhas) + Transações Diárias (pontos)"
        )
        
        # Adiciona pontos individuais nos dias reais
        df['data_str'] = df['data_transacao'].dt.strftime('%Y-%m-%d')
        
        fig.add_scatter(
            x=df['data_str'],
            y=df['valor'],
            mode='markers+text',
            text=df['valor'].apply(lambda v: f'R$ {v:,.0f}'),
            textposition='top center' if df['tipo'].iloc[0] == 'Entrada' else 'bottom center',
            marker=dict(size=10, color=df['tipo'].map({'Entrada': '#00ff88', 'Saída': '#ff0055'})),
            showlegend=False
        )
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Período",
            yaxis_title="Valor (R$)",
            hovermode="x unified",
            xaxis_tickformat='%Y-%m'
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # MÉTRICAS
        total_entradas = df[df['tipo'] == 'Entrada']['valor'].sum()
        total_saidas = df[df['tipo'] == 'Saída']['valor'].sum()
        saldo = total_entradas - total_saidas
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Entradas", f"R$ {total_entradas:,.2f}")
        col2.metric("Saídas", f"R$ {total_saidas:,.2f}")
        col3.metric("Saldo", f"R$ {saldo:,.2f}", delta_color="normal")

        st.divider()

        # TABELA
        st.dataframe(
            df[['data_transacao', 'tipo', 'descricao', 'valor']].sort_values('data_transacao', ascending=False),
            use_container_width=True,
            column_config={
                "data_transacao": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f")
            }
        )

        # EXCLUSÃO
        with st.expander("Excluir Lançamento"):
            id_del = st.selectbox("ID:", df['id'].tolist())
            if st.button("Apagar"):
                db.table("finances").delete().eq("id", id_del).execute()
                st.rerun()

    else:
        st.info("Nenhum lançamento. Cadastre acima.")