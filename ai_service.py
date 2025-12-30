import streamlit as st
import requests
import json
import re
from datetime import datetime
from database import db
from dateutil.relativedelta import relativedelta

# --- CONFIGURAÇÃO DE CHAVES ---
try:
    OPENROUTER_API_KEY = st.secrets["api"]["openrouter"]
except:
    st.error("CRÍTICO: Chaves de API ausentes.")
    st.stop()

# --- FUNÇÕES DE MEMÓRIA ---
def salvar_mensagem(user_id, session_id, role, content):
    """Grava mensagem no banco para memória futura"""
    if not user_id: return
    try:
        db.table("chat_history").insert({
            "user_id": user_id,
            "session_id": session_id,
            "role": role,
            "content": content
        }).execute()
    except Exception as e:
        print(f"Erro ao salvar histórico: {e}")

def carregar_historico(user_id, session_id, limite=6):
    """Carrega últimas mensagens para contexto"""
    if not user_id: return []
    try:
        res = db.table("chat_history").select("role, content")\
            .eq("user_id", user_id)\
            .eq("session_id", session_id)\
            .order("created_at", desc=True)\
            .limit(limite)\
            .execute()
        return res.data[::-1] if res.data else [] # Inverte para ordem cronológica
    except:
        return []

# --- CÉREBRO PRINCIPAL ---
def pensar_como_cortex(prompt_usuario, user_id=None, session_id="default", system_override=None):
    if not user_id:
        return "❌ ERRO: Identidade não detectada."

    hoje = datetime.now()
    hoje_str = hoje.strftime('%Y-%m-%d')
    
    # 1. AUTO-INICIALIZAÇÃO (Cria usuário novo se não existir)
    try:
        user_query = db.table("users").select("*").eq("id", user_id).execute()
        if not user_query.data:
            novo_reset = (hoje + relativedelta(months=1)).strftime('%Y-%m-%d')
            payload_novo = {
                "id": user_id,
                "username": f"Operador_{user_id[:6]}",
                "password_hash": "auth_managed_by_supabase",
                "plano_atual": "basico",
                "tokens_disponiveis": 1000, 
                "tokens_total_gasto": 0,
                "data_reset_tokens": novo_reset
            }
            db.table("users").insert(payload_novo).execute()
            user_data = payload_novo
        else:
            user_data = user_query.data[0]
    except Exception as e:
        return f"❌ Falha BD: {str(e)}"

    # 2. VERIFICAÇÃO DE SALDO
    tokens_atuais = user_data.get("tokens_disponiveis", 0)
    if tokens_atuais <= 10:
        return f"⛔ SEM COMBUSTÍVEL. Saldo: {tokens_atuais}."
    
    # 3. CONTEXTO E PROMPT
    prompt_padrao = f"""
Você é o CORTEX OS. Data: {hoje_str}.
Objetivo: Classificar intenção e responder.
REGRAS DE COMANDO (Retorne APENAS JSON se for comando):
1. FINANCEIRO (gastei, recebi, pix) -> {{"acao": "financeiro", "dados": {{"tipo": "Saída/Entrada", "valor": 0.00, "descricao": "...", "data": "{hoje_str}"}}}}
2. TAREFA (lembrar, fazer) -> {{"acao": "tarefa", "dados": {{"titulo": "...", "prazo": "YYYY-MM-DD", "prioridade": "Alta"}}}}
3. HÁBITO (novo hábito) -> {{"acao": "habito", "dados": {{"titulo": "..."}}}}
4. PROJETO (novo projeto) -> {{"acao": "projeto", "dados": {{"nome": "..."}}}}
5. CONTEÚDO (ideia post) -> {{"acao": "conteudo", "dados": {{"tema": "...", "plataforma": "Instagram"}}}}
CASO CONTRÁRIO: Responda como Tony Stark.
"""
    system_final = system_override if system_override else prompt_padrao
    
    # Monta Payload com Memória
    msgs = [{"role": "system", "content": system_final}]
    msgs.extend(carregar_historico(user_id, session_id)) # Adiciona memória
    msgs.append({"role": "user", "content": prompt_usuario})

    # 4. EXECUÇÃO IA
    try:
        salvar_mensagem(user_id, session_id, "user", prompt_usuario) # Salva pergunta
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "HTTP-Referer": "cortex.os"}
        payload = {"model": "deepseek/deepseek-chat", "messages": msgs, "temperature": 0.3}
        
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code != 200: return f"Erro API: {resp.text}"
        
        texto = resp.json()['choices'][0]['message']['content'].strip()
        salvar_mensagem(user_id, session_id, "assistant", texto) # Salva resposta
        
        # Debita Tokens
        custo = len(prompt_usuario)//3 + len(texto)//3 + 10
        db.table("users").update({"tokens_disponiveis": tokens_atuais - custo}).eq("id", user_id).execute()

    except Exception as err:
        return f"⚠️ Falha Neural: {str(err)}"

    # 5. PROCESSA COMANDOS (Apenas no chat principal para segurança)
    if session_id == "default":
        match = re.search(r'\{.*\}', texto, re.DOTALL)
        if match:
            try:
                d = json.loads(match.group())
                acao, info = d.get("acao"), d.get("dados", {})
                
                if acao == "financeiro":
                    db.table("finances").insert({
                        "user_id": user_id, "tipo": info.get("tipo"), "valor": float(info.get("valor",0)), 
                        "descricao": info.get("descricao"), "data_transacao": info.get("data", hoje_str)
                    }).execute()
                    return f"💸 Transação: {info.get('tipo')} R$ {info.get('valor')}."
                
                elif acao == "tarefa":
                    db.table("tasks").insert({
                        "user_id": user_id, "titulo": info.get("titulo"), "prazo": info.get("prazo", hoje_str), "concluido": False
                    }).execute()
                    return f"✅ Tarefa: {info.get('titulo')}."
                
                # (Outros comandos mantidos simplificados aqui, o código original já os tem)
            except:
                pass 

    return texto
