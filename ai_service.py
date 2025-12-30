import streamlit as st # Necessário para acessar os secrets
import requests
import json
import re
from datetime import datetime
from database import db
from dateutil.relativedelta import relativedelta

# --- CONFIGURAÇÃO DE CHAVES (SEGURA) ---
# Se a chave não existir no cofre, o sistema avisa em vez de quebrar silenciosamente
try:
    OPENROUTER_API_KEY = st.secrets["api"]["openrouter"]
    # GEMINI_API_KEY = st.secrets["api"]["gemini"] # Se for usar no futuro
except FileNotFoundError:
    st.error("CRÍTICO: Arquivo de segredos (.streamlit/secrets.toml) não encontrado.")
    st.stop()
except KeyError:
    st.error("CRÍTICO: Chaves de API ausentes no arquivo de segredos.")
    st.stop()

def pensar_como_cortex(prompt_usuario, user_id=None):
    if not user_id:
        return "❌ ERRO CRÍTICO: Identidade do Operador não detectada."

    hoje = datetime.now()
    hoje_str = hoje.strftime('%Y-%m-%d')
    
    # 1. BUSCA O USUÁRIO NA TABELA DE ECONOMIA (USERS)
    try:
        user_query = db.table("users").select("*").eq("id", user_id).execute()
        
        # --- PROTOCOLO DE AUTO-INICIALIZAÇÃO (V6) ---
        if not user_query.data:
            novo_reset = (hoje + relativedelta(months=1)).strftime('%Y-%m-%d')
            codinome = f"Operador_{user_id[:6]}"
            pass_dummy = "auth_managed_by_supabase" 
            
            payload_novo_user = {
                "id": user_id,
                "username": codinome,
                "password_hash": pass_dummy,
                "plano_atual": "basico",
                "tokens_disponiveis": 1000, 
                "tokens_total_gasto": 0,
                "data_reset_tokens": novo_reset
            }
            db.table("users").insert(payload_novo_user).execute()
            user_data = payload_novo_user
        else:
            user_data = user_query.data[0]

    except Exception as e:
        return f"❌ Falha de Inicialização (BD): {str(e)}"

    # 2. CARREGA DADOS VITAIS
    plano_atual = user_data.get("plano_atual", "basico")
    tokens_atuais = user_data.get("tokens_disponiveis", 0)
    data_reset_str = user_data.get("data_reset_tokens")
    total_gasto = user_data.get("tokens_total_gasto", 0)

    # 3. VERIFICAÇÃO DE RESET MENSAL
    try:
        if data_reset_str:
            data_reset = datetime.strptime(data_reset_str, '%Y-%m-%d')
            if data_reset < hoje:
                tokens_novos = 5000 if plano_atual == "imperador" else 1000
                proximo_reset = (hoje + relativedelta(months=1)).strftime('%Y-%m-%d')
                db.table("users").update({
                    "tokens_disponiveis": tokens_novos,
                    "data_reset_tokens": proximo_reset
                }).eq("id", user_id).execute()
                tokens_atuais = tokens_novos
    except Exception:
        pass 

    # 4. TRAVA DE SEGURANÇA
    if tokens_atuais <= 10:
        return f"⛔ SEM COMBUSTÍVEL. Saldo: {tokens_atuais}. Renovação em: {data_reset_str}."
    
    # --- SYSTEM PROMPT ---
    system_prompt = f"""
Você é o CORTEX OS. Data: {hoje_str}.
Seu objetivo é classificar a intenção do usuário e responder com um JSON se for um comando, ou texto se for conversa.

REGRAS DE COMANDO (Retorne APENAS o JSON, sem markdown):

1. FINANCEIRO (Gatilhos: gastei, paguei, comprei, assinatura, ifood, uber, recebi, lucro, pix, boleto)
   JSON: {{"acao": "financeiro", "dados": {{"tipo": "Saída" ou "Entrada", "valor": 0.00, "descricao": "resumo curto", "data": "{hoje_str}"}}}}

2. TAREFA (Gatilhos: lembrar, fazer, preciso, cobrar, agendar, to-do)
   JSON: {{"acao": "tarefa", "dados": {{"titulo": "ação completa", "prazo": "YYYY-MM-DD" (calcule baseado na fala), "prioridade": "Alta/Média/Baixa"}}}}

3. HÁBITO (Gatilhos: novo hábito, começar a treinar, ler todo dia, meta diária)
   JSON: {{"acao": "habito", "dados": {{"titulo": "nome do hábito"}}}}

4. PROJETO (Gatilhos: novo projeto, ideia de negócio, planejar viagem)
   JSON: {{"acao": "projeto", "dados": {{"nome": "nome do projeto", "data_final": "YYYY-MM-DD"}}}}

5. CONTEÚDO (Gatilhos: ideia de post, roteiro, instagram, tiktok, youtube)
   JSON: {{"acao": "conteudo", "dados": {{"tema": "assunto", "plataforma": "Instagram/TikTok", "titulo": "Sugestão de Titulo"}}}}

CASO CONTRÁRIO: Responda como Tony Stark: curto, arrogante, direto e genial.
"""

    # 5. EXECUÇÃO IA
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://cortex.couto.ind",
            "X-Title": "Cortex OS"
        }
        payload = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_usuario}
            ],
            "temperature": 0.3,
            "max_tokens": 450
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        if response.status_code != 200:
            raise Exception(f"Status {response.status_code}")
            
        result = response.json()
        texto = result['choices'][0]['message']['content'].strip()
        
        tokens_usados = len(prompt_usuario)//3 + len(texto)//3 + 10
        db.table("users").update({
            "tokens_disponiveis": tokens_atuais - tokens_usados,
            "tokens_total_gasto": total_gasto + tokens_usados
        }).eq("id", user_id).execute()

    except Exception as err:
        return f"⚠️ Falha Neural: {str(err)}"

    # 6. PROCESSAMENTO INTELIGENTE (REGEX)
    match_json = re.search(r'\{.*\}', texto, re.DOTALL)
    
    if match_json:
        try:
            json_str = match_json.group()
            dados = json.loads(json_str)
            acao = dados.get("acao")
            info = dados.get("dados", {})

            if acao == "financeiro":
                db.table("finances").insert({
                    "user_id": user_id,
                    "tipo": info.get("tipo", "Saída"),
                    "valor": float(info.get("valor", 0)),
                    "descricao": info.get("descricao", "Via Chat"),
                    "categoria": "IA",
                    "data_transacao": info.get("data", hoje_str)
                }).execute()
                return f"💸 Transação registrada: {info.get('tipo')} de R$ {info.get('valor')}."

            elif acao == "tarefa":
                db.table("tasks").insert({
                    "user_id": user_id,
                    "titulo": info.get("titulo"),
                    "prazo": info.get("prazo", hoje_str),
                    "prioridade": info.get("prioridade", "Média"),
                    "concluido": False
                }).execute()
                return f"✅ Tarefa agendada: {info.get('titulo')}."
            
            elif acao == "habito":
                db.table("habits").insert({
                    "user_id": user_id,
                    "titulo": info.get("titulo"),
                    "streak": 0
                }).execute()
                return f"🧬 Novo hábito iniciado: {info.get('titulo')}."

            elif acao == "projeto":
                db.table("projects").insert({
                    "user_id": user_id,
                    "nome": info.get("nome"),
                    "data_final": info.get("data_final", hoje_str),
                    "status": "Em Planejamento"
                }).execute()
                return f"🏗️ Projeto criado: {info.get('nome')}."
            
            elif acao == "conteudo":
                prompt_roteiro = f"Gere um roteiro curto e viral para {info.get('plataforma')} sobre: {info.get('tema')}."
                payload_rot = payload.copy()
                payload_rot["messages"] = [{"role": "user", "content": prompt_roteiro}]
                res_rot = requests.post(url, headers=headers, json=payload_rot, timeout=20)
                roteiro = res_rot.json()['choices'][0]['message']['content']
                
                db.table("content_production").insert({
                    "user_id": user_id,
                    "titulo": info.get("titulo", info.get("tema")),
                    "plataforma": info.get("plataforma"),
                    "conteudo": roteiro,
                    "status": "Rascunho"
                }).execute()
                return f"📝 Conteúdo gerado e salvo em 'Produção'.\n\n{roteiro[:200]}..."

        except Exception as json_err:
            return f"Erro ao processar comando: {str(json_err)}"

    return texto