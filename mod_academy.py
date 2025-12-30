import streamlit as st
from database import db

def is_admin(user_id):
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
        produtos = db.table("academy_products").select("*").execute().data
    except Exception as e:
        st.error(f"Erro ao carregar produtos: {str(e)}")
        produtos = []

    # MODO ADMIN: Gerenciar produtos
    if admin_mode:
        st.markdown("### 🔧 Modo Admin – Gerenciar Produtos & Ebooks")
        
        # Formulário para adicionar novo produto
        with st.expander("➕ Adicionar Novo Produto / Ebook"):
            with st.form("novo_produto"):
                titulo = st.text_input("Título (ex: Protocolo Equipe Infinita)")
                desc = st.text_area("Descrição curta")
                
                st.markdown("**URL da Capa (cole o link que abre no navegador)**")
                img_url = st.text_input("Link da Imagem (ex: https://i.imgur.com/...)")
                
                link_checkout = st.text_input("Link Hotmart Checkout")
                link_aula = st.text_input("Link Área de Membros Hotmart (acesso ao ebook/material)")
                
                submit = st.form_submit_button("Salvar Produto")
                
                if submit:
                    if titulo and link_checkout and img_url:
                        db.table("academy_products").insert({
                            "titulo": titulo,
                            "descricao": desc,
                            "img_url": img_url,
                            "link_checkout": link_checkout,
                            "link_aula": link_aula
                        }).execute()
                        st.success("Produto adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Título, URL da Capa e Link Checkout são obrigatórios")
        
        # Lista para edição/exclusão
        st.markdown("### Produtos Existentes")
        for p in produtos:
            with st.expander(f"{p['titulo']} (ID: {p['id']})"):
                novo_titulo = st.text_input("Título", value=p['titulo'], key=f"tit_{p['id']}")
                novo_desc = st.text_area("Descrição", value=p['descricao'], key=f"desc_{p['id']}")
                
                st.markdown("**URL da Capa Atual**")
                novo_img = st.text_input("Atualizar URL Capa", value=p.get('img_url', ''), key=f"img_{p['id']}")
                
                novo_checkout = st.text_input("Checkout", value=p['link_checkout'], key=f"chk_{p['id']}")
                novo_aula = st.text_input("Área Membros", value=p['link_aula'], key=f"aula_{p['id']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Atualizar", key=f"upd_{p['id']}"):
                        db.table("academy_products").update({
                            "titulo": novo_titulo,
                            "descricao": novo_desc,
                            "img_url": novo_img,
                            "link_checkout": novo_checkout,
                            "link_aula": novo_aula
                        }).eq("id", p['id']).execute()
                        st.success("Atualizado!")
                        st.rerun()
                with col2:
                    if st.button("Excluir", key=f"del_{p['id']}"):
                        db.table("academy_products").delete().eq("id", p['id']).execute()
                        st.success("Excluído!")
                        st.rerun()
        
        st.divider()

    # VISUALIZAÇÃO PARA TODOS (CLIENTES)
    st.markdown("### Produtos & Ebooks Disponíveis")
    
    # CSS cards dark executive
    st.markdown("""
    <style>
    .container-cards {display:flex;flex-wrap:wrap;gap:20px;justify-content:center;padding:20px;}
    .card-3d {width:250px;height:444px;background:#0d0d0d;border-radius:15px;position:relative;overflow:hidden;transition:transform .4s ease,box-shadow .4s ease;border:1px solid #333;cursor:pointer;text-decoration:none!important;}
    .card-3d:hover {transform:translateY(-10px) scale(1.02) rotateX(2deg);box-shadow:0 15px 30px rgba(0,243,255,.3);border-color:#00f3ff;}
    .card-bg {width:100%;height:100%;object-fit:cover;opacity:.6;transition:opacity .4s;}
    .card-3d:hover .card-bg {opacity:.3;}
    .card-content {position:absolute;bottom:0;left:0;width:100%;padding:20px;background:linear-gradient(to top,#000000 10%,transparent);color:white;}
    .card-title {font-family:'Courier New',monospace;color:#00f3ff;font-weight:bold;font-size:1.2rem;margin-bottom:5px;text-shadow:0 0 5px #00f3ff;}
    .card-status {font-size:.8rem;font-weight:bold;text-transform:uppercase;padding:5px 10px;border-radius:4px;display:inline-block;margin-bottom:10px;}
    .status-locked {background:#ff0055;color:white;border:1px solid #ff0055;}
    .status-unlocked {background:#00ff88;color:black;border:1px solid #00ff88;box-shadow:0 0 10px #00ff88;}
    </style>
    """, unsafe_allow_html=True)
    
    html_cards = '<div class="container-cards">'
    
    for p in produtos:
        possui = db.table("user_products").select("id").eq("user_id", user_id).eq("product_id", p['id']).execute().data
        
        link_destino = p['link_aula'] if possui else p['link_checkout']
        texto_status = "📖 ACESSAR ÁREA / EBOOK" if possui else "🔒 COMPRAR AGORA"
        classe_status = "status-unlocked" if possui else "status-locked"
        
        img_src = p.get('img_url') or "https://via.placeholder.com/250x444?text=Capa+Produto"
        
        html_cards += f"""
        <a href="{link_destino}" target="_blank" class="card-3d">
            <img src="{img_src}" class="card-bg">
            <div class="card-content">
                <span class="card-status {classe_status}">{texto_status}</span>
                <div class="card-title">{p['titulo']}</div>
                <p style="font-size:0.8rem;color:#ccc;">{p['descricao']}</p>
            </div>
        </a>
        """
    
    html_cards += '</div>'
    st.markdown(html_cards, unsafe_allow_html=True)
    
    if not produtos:
        st.info("Nenhum produto disponível no momento. (Admin: adicione acima)")