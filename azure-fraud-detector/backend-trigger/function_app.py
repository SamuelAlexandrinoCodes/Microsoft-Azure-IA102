import logging
import os
import hashlib
import time
from io import BytesIO

import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# --- Inicialização Global (Executa uma vez) ---
# O modelo v2 gerencia melhor os clientes, mas inicializar
# o cliente do Search aqui ainda é uma boa prática.
try:
    search_service_name = os.environ['AZURE_SEARCH_SERVICE_NAME']
    search_key = os.environ['AZURE_SEARCH_KEY']
    search_index_name = os.environ['AZURE_SEARCH_INDEX_NAME']

    search_endpoint = f"https://{search_service_name}.search.windows.net"
    search_credential = AzureKeyCredential(search_key)
    
    # Cliente do Cognitive Search
    search_client = SearchClient(endpoint=search_endpoint, 
                                 index_name=search_index_name, 
                                 credential=search_credential)
    
    logging.info(f"Conexão com Search Service '{search_service_name}' estabelecida.")

except KeyError as e:
    logging.error(f"ERRO CRÍTICO: Variável de ambiente não encontrada: {e}. A função não pode iniciar.")
    search_client = None

# -------------------------------------------------

# Inicializa o aplicativo de função (modelo v2)
app = func.FunctionApp()

@app.blob_trigger(
    arg_name="myblob", # Nome da variável que recebe o blob
    path="documentos-brutos/{name}", # O caminho a monitorar
    connection="AzureWebJobsStorage" # Nome da config. em local.settings.json
)
def ProcessDocumentHash(myblob: func.InputStream):
    """
    Função V5 (Modelo v2): Disparada por Blob Trigger.
    Calcula o hash e salva diretamente no Cognitive Search.
    """
    
    if not search_client:
        logging.error("Cliente do Search não inicializado. Verifique as variáveis de ambiente.")
        return

    logging.info(f"Processando blob: {myblob.name} (Tamanho: {myblob.length} bytes)")

    try:
        # 1. Ler o arquivo inteiro
        file_bytes = myblob.read()
        
        # 2. Calcular o Hash (Exatamente como o frontend faz)
        hasher = hashlib.sha256()
        hasher.update(file_bytes)
        document_hash = hasher.hexdigest()

        logging.info(f"Hash calculado para {myblob.name}: {document_hash[:10]}...")

        # 3. Preparar o documento para o Cognitive Search
        document_key = document_hash
        
        document_to_index = {
            "id": document_key, # Assumindo que 'id' é sua chave no índice
            "document_hash": document_hash,
            "status": "Processado_V5",
            "filename": myblob.name.split('/')[-1],
            "processed_timestamp": time.time()
        }

        # 4. Enviar para o Cognitive Search
        logging.info(f"Enviando documento {document_key} para o índice...")
        result = search_client.upload_documents(documents=[document_to_index])
        
        if result[0].succeeded:
            logging.info(f"Documento {document_key} indexado com sucesso.")
        else:
            logging.error(f"Falha ao indexar {document_key}. Razão: {result[0].error_message}")

    except Exception as e:
        logging.error(f"Erro catastrófico ao processar {myblob.name}: {e}")
        raise e # Lança a exceção para o runtime do Functions