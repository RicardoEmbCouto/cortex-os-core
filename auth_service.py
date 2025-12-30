from database import db

def login_tatico(email, senha):
    try:
        # 1. Realiza a autenticação no Supabase Auth
        res = db.auth.sign_in_with_password({"email": email, "password": senha})
        user_id = res.user.id
        
        # --- LINHA DE DIAGNÓSTICO (NÃO REMOVER) ---
        print(f"\n[DEBUG] ID Autenticado: {user_id}")
        # ------------------------------------------

        # 2. Busca o perfil na tabela pública
        # O .single() espera encontrar exatamente 1 linha
        query = db.table("profiles").select("subscription_status").eq("id", user_id).single().execute()
        
        perfil = query.data

        # 3. Validação de Assinatura (Conforme erro da image_b3809c)
        if perfil and perfil.get("subscription_status") == "active":
            return res.user
        else:
            print(f"X [BLOQUEIO] Usuário {email} encontrado, mas assinatura não está 'active'.")
            return None

    except Exception as e:
        # Captura o erro PGRST116 se a linha não existir
        if "PGRST116" in str(e):
            print(f"\n[ERRO CRÍTICO] O ID {user_id} não existe na tabela 'profiles'.")
            print("Ação: Rode o INSERT no SQL Editor com o ID acima.")
        else:
            print(f"\nX [FALHA TÁTICA]: {e}")
        return None