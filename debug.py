import google.generativeai as genai

# --- COLE SUA CHAVE AQUI ---
API_KEY = "AIzaSyAKRevw-NVPP9LFZdnh3eWKUotTdygFs3c"

print("🔍 INICIANDO DIAGNÓSTICO DO CORTEX...")
print("-" * 40)

try:
    # 1. Verifica a Versão da Biblioteca
    import importlib.metadata
    versao = importlib.metadata.version('google-generativeai')
    print(f"📦 VERSÃO DO DRIVER INSTALADO: {versao}")
    print("-" * 40)

    # 2. Testa a Conexão e Lista Modelos
    genai.configure(api_key=API_KEY)
    print("📡 CONECTANDO AO GOOGLE...")
    
    modelos = genai.list_models()
    encontrados = []
    
    print("📋 MODELOS DISPONÍVEIS NA SUA CONTA:")
    for m in modelos:
        if 'generateContent' in m.supported_generation_methods:
            print(f"   ✅ {m.name}")
            encontrados.append(m.name)

    print("-" * 40)
    
    # 3. Veredito
    if not encontrados:
        print("⚠️ ALERTA CRÍTICO: Nenhum modelo encontrado. Sua API Key pode estar inválida ou o projeto no Google Cloud sem permissão.")
    elif 'models/gemini-pro' in encontrados or 'models/gemini-1.5-flash' in encontrados:
        print("🚀 STATUS: Conexão bem sucedida! Copie o nome exato de um modelo acima (ex: 'gemini-pro') para o seu código.")
    else:
        print("⚠️ ESTRANHO: Conectou, mas os modelos Gemini não apareceram. Tente criar uma nova API Key.")

except Exception as e:
    print(f"❌ ERRO FATAL DE CONEXÃO: {e}")