import requests, uuid, json, os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

# --- Extrai as credenciais de forma segura do ambiente ---
chave_secreta = os.getenv('AZURE_TRANSLATOR_KEY')
endpoint = os.getenv('AZURE_TRANSLATOR_ENDPOINT')
localizacao = os.getenv('AZURE_TRANSLATOR_LOCATION')

# --- DADOS DE INTELIGÊNCIA: GLOSSÁRIO DE IDIOMAS ---
IDIOMAS_SUPORTADOS = {
    'pt': 'Português', 'en': 'Inglês', 'es': 'Espanhol', 'fr': 'Francês',
    'de': 'Alemão', 'it': 'Italiano', 'ja': 'Japonês', 'ko': 'Coreano',
    'ru': 'Russo', 'zh-Hans': 'Chinês (Simplificado)'
}

# --- Validação das Credenciais ---
if not all([chave_secreta, endpoint, localizacao]):
    print("ERRO CRÍTICO: Uma ou mais credenciais (chave, endpoint, localização) não foram encontradas no ficheiro .env.")
    exit()

def traduzir_texto(texto_para_traduzir, idioma_de_origem, idiomas_de_destino):
    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'to': idiomas_de_destino
    }
    if idioma_de_origem:
        params['from'] = idioma_de_origem

    headers = {
        'Ocp-Apim-Subscription-Key': chave_secreta,
        'Ocp-Apim-Subscription-Region': localizacao,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    body = [{'text': texto_para_traduzir}]

    try:
        request = requests.post(constructed_url, params=params, headers=headers, json=body)
        request.raise_for_status()
        response = request.json()
        
        print("\n--- TRADUÇÃO CONCLUÍDA ---")
        
        # Se a deteção automática foi usada, reporta o idioma detetado
        if not idioma_de_origem:
            idioma_detetado = response[0]['detectedLanguage']['language']
            print(f"Idioma de Origem Detetado: {idioma_detetado}")

        print(f"Texto Original: {body[0]['text']}")
        print("-" * 30)
        
        for translation in response[0]['translations']:
            print(f"Tradução ({translation['to']}): {translation['text']}")

    except requests.exceptions.HTTPError as err:
        print(f"\nERRO: Falha na comunicação com a API (Status Code: {err.response.status_code}).")
    except Exception as err:
        print(f"\nOcorreu um erro inesperado: {err}")

def exibir_ajuda_idiomas():
    """
    Exibe o glossário de idiomas disponíveis.
    """
    print("\n--- GLOSSÁRIO DE CÓDIGOS DE IDIOMAS ---")
    for codigo, nome in IDIOMAS_SUPORTADOS.items():
        print(f"{codigo.ljust(10)} : {nome}")
    print("---------------------------------------")

# --- Loop de Execução Principal ---
if __name__ == "__main__":
    print("--- Ferramenta de Tradução Global (Azure AI) ---")
    while True:
        print("\n-------------------------------------------")
        texto = input("Digite o texto que deseja traduzir (ou 'sair' para terminar):\n> ")
        if texto.lower() == 'sair':
            break

        while True:
            origem = input("Digite o código do idioma de origem (ou deixe em branco para detetar automaticamente):\n> ")
            if origem.lower() == 'ajuda':
                exibir_ajuda_idiomas()
                continue
            break

        while True:
            destino_str = input("Digite o(s) código(s) do(s) idioma(s) de destino (ex: en,es) ou 'ajuda' para ver a lista:\n> ")
            if destino_str.lower() == 'ajuda':
                exibir_ajuda_idiomas()
                continue
            break
        
        destino = [lang.strip() for lang in destino_str.split(',')]

        traduzir_texto(texto, origem, destino)
        
    print("\nOperação concluída. Intérprete Global desativado.")
