import streamlit as st
from database import db

# --- CONFIGURAÇÃO DE SEGURANÇA MÁXIMA ---
def is_admin(user_id):
    # 1. TRAVA BIOMÉTRICA (Hardcoded Email Check)
    # Coloque aqui o(s) email(s) que têm permissão de DEUS no sistema.
    EMAILS_DO_BOSS = [
        "ricardinho.coutofilho@outlook.com",  # SUBSTITUA PELO SEU EMAIL DE LOGIN EXATO
         
    ]
    
    email_atual = st.session_state.get("user_email", "")
    
    if email_atual in EMAILS_DO_BOSS:
        return True

    # 2. Fallback: Checagem no Banco (caso você queira delegar a gerentes no futuro)
    try:
        res = db.table("profiles").select("role").eq("id", user_id).single().execute()
        return res.data and res.data.get("role") == "admin"
    except:
        return False

def render(user_id):
    st.markdown("<h2 class='titulo-neon'>🎓 CORTEX ACADEMY</h2>", unsafe_allow_html=True)
    
    admin_mode = is_admin(user_id)
    
    # Carrega produtos do banco
    try:
        produtos = db.table("academy_products").select("*").order("created_at", desc=True).execute().data
    except Exception as e:
        # Se a tabela não existir, não quebra a tela
        produtos = []

    # --- ÁREA RESTRITA AO COMANDANTE ---
    if admin_mode:
        with st.expander("🔐 ÁREA RESTRITA: GERENCIAMENTO DE ARSENAL", expanded=False):
            st.markdown("### 🔧 Adicionar Novo Info-Produto")
            
            with st.form("novo_produto"):
                titulo = st.text_input("Título do Produto")
                desc = st.text_area("Descrição Curta (Gatilho de Venda)")
                img_url = st.text_input("URL da Imagem (Capa 3D)")
                link_checkout = st.text_input("Link do Checkout (Pagamento)")
                link_aula = st.text_input("Link da Área de Membros (Entrega)")
                
                c1, c2 = st.columns(2)
                with c1:
                    submit = st.form_submit_button("💾 SALVAR NO ARSENAL")
                
                if submit:
                    if titulo and link_checkout:
                        try:
                            db.table("academy_products").insert({
                                "titulo": titulo,
                                "descricao": desc,
                                "img_url": img_url,
                                "link_checkout": link_checkout,
                                "link_aula": link_aula
                            }).execute()
                            st.success("✅ Produto adicionado ao catálogo global.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")
                    else:
                        st.warning("Título e Checkout são obrigatórios.")
            
            st.divider()
            st.markdown("### 🗑️ Gerenciar Existentes")
            for p in produtos:
                c_del1, c_del2 = st.columns([4, 1])
                with c_del1:
                    st.write(f"**{p['titulo']}**")
                with c_del2:
                    if st.button("EXCLUIR", key=f"del_{p['id']}"):
                        db.table("academy_products").delete().eq("id", p['id']).execute()
                        st.rerun()

    # --- VITRINE PÚBLICA (O QUE OS SOLDADOS VÊEM) ---
    st.divider()
    st.markdown("### 📚 Biblioteca de Expansão de Consciência")
    
    # CSS cards dark executive (Visual de Elite)
    st.markdown("""
    <style>
    .container-cards {display:flex;flex-wrap:wrap;gap:20px;justify-content:center;padding:20px;}
    .card-3d {width:250px;height:400px;background:#0d0d0d;border-radius:12px;position:relative;overflow:hidden;transition:all .3s ease;border:1px solid #333;text-decoration:none!important;}
    .card-3d:hover {transform:translateY(-5px);border-color:#00f3ff;box-shadow:0 0 20px rgba(0,243,255,0.2);}
    .card-bg {width:100%;height:200px;object-fit:cover;opacity:0.8;}
    .card-content {padding:15px;color:white;}
    .card-title {font-family:'Courier New';color:#00f3ff;font-weight:bold;font-size:1.1rem;margin-bottom:10px;height:50px;overflow:hidden;}
    .btn-action {display:block;width:100%;padding:10px;text-align:center;border-radius:5px;font-weight:bold;margin-top:10px;text-transform:uppercase;}
    .btn-buy {background:#00f3ff;color:black;}
    .btn-access {background:#00ff88;color:black;}
    </style>
    """, unsafe_allow_html=True)
    
    html_cards = '<div class="container-cards">'
    
    if not produtos:
        st.info("Nenhum treinamento disponível no momento. O Mestre está forjando novas armas.")
    
    for p in produtos:
        # Verifica se o usuário já comprou (precisa da tabela user_products)
        possui = False
        try:
            check = db.table("user_products").select("id").eq("user_id", user_id).eq("product_id", p['id']).execute()
            if check.data: possui = True
        except:
            pass # Se a tabela user_products não existir, assume que não tem
        
        link_destino = p['link_aula'] if possui else p['link_checkout']
        texto_botao = "ACESSAR AGORA" if possui else "ADQUIRIR ACESSO"
        classe_botao = "btn-access" if possui else "btn-buy"
        img_src = p.get('img_url') or "https://via.placeholder.com/250x200?text=Cortex+Academy"
        
        html_cards += f"""
        <div class="card-3d">
            <img src="{img_src}" class="card-bg">
            <div class="card-content">
                <div class="card-title">{p['titulo']}</div>
                <p style="font-size:0.8rem;color:#aaa;height:40px;overflow:hidden;">{p['descricao'][:60]}...</p>
                <a href="{link_destino}" target="_blank" class="btn-action {classe_botao}">{texto_botao}</a>
            </div>
        </div>
        """
    
    html_cards += '</div>'
    st.markdown(html_cards, unsafe_allow_html=True)
