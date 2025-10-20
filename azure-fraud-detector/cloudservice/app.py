import streamlit as st
import os
import hashlib
import time
import base64
import logging
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
# ResourceExistsError não é mais pego no frontend, mas mantido para referência
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import SearchIndex
from azure.search.documents.indexes import SearchIndexClient

# --- 1. CONFIGURAÇÃO E FUNÇÕES DE APOIO ---

st.set_page_config(layout="centered")

def initialize_app():
    """Carrega configs e inicializa clientes no st.session_state."""
    if 'initialized' in st.session_state:
        return True
    
    load_dotenv()
    required_vars = ['AZURE_STORAGE_CONNECTION_STRING', 'AZURE_SEARCH_SERVICE_NAME', 'AZURE_SEARCH_KEY']
    if not all(os.getenv(var) for var in required_vars):
        st.error("ERRO CRÍTICO: Variáveis de ambiente não encontradas no .env.")
        return False

    st.session_state.blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_STORAGE_CONNECTION_STRING'))
    search_endpoint = f"https://{os.getenv('AZURE_SEARCH_SERVICE_NAME')}.search.windows.net"
    search_credential = AzureKeyCredential(os.getenv('AZURE_SEARCH_KEY'))
    st.session_state.search_client = SearchClient(endpoint=search_endpoint, index_name="index-vigilancia-fraudes", credential=search_credential)
    st.session_state.initialized = True
    return True

def calculate_hash(file_bytes):
    """Calcula o hash SHA256 do arquivo."""
    hasher = hashlib.sha256()
    hasher.update(file_bytes)
    return hasher.hexdigest()

def check_hash_in_index(document_hash):
    """
    Verifica se um hash já existe no índice, usando o método de 'search' (V1).
    Este método é o correto pois filtra pelo campo 'document_hash'.
    """
    try:
        # --- DEBUG ---
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Depuração: Verificando hash {document_hash} no índice...")
        
        results = st.session_state.search_client.search(
            search_text="*",  # Busca em tudo
            filter=f"document_hash eq '{document_hash}'", # Filtra pelo campo 'document_hash'
            include_total_count=True # Pede para o Azure contar o total
        )
        
        count = results.get_count()
        
        # --- DEBUG ---
        logging.info(f"Depuração: Contagem de resultados encontrada: {count}")
        
        return count > 0 # Se count > 0, o hash existe
    
    except Exception as e:
        st.error(f"Erro ao consultar o índice: {e}")
        logging.error(f"Falha na consulta ao índice: {e}")
        # Doutrina "falhe em segurança"
        return True

def clear_status():
    """Limpa o status da operação anterior ao carregar um novo arquivo."""
    st.session_state.last_status = None

# --- 2. LÓGICA PRINCIPAL DA APLICAÇÃO ---

if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'last_status' not in st.session_state:
    st.session_state.last_status = None

if not initialize_app():
    st.stop()

# --- INTERFACE DO POSTO DE COMANDO ---
st.title("️Sistema de Verificação de Fraudes (v2.0 - Assíncrono)")

# REMOVIDO: A verificação de lock global. A UI está sempre ativa.

st.markdown("Faça o upload de um comprovante para análise. A resposta será imediata.")

# Exibe o resultado da operação anterior, se houver
if st.session_state.last_status:
    status_type = st.session_state.last_status["type"]
    message = st.session_state.last_status["message"]
    if status_type == "success":
        st.success(message)
    elif status_type == "error":
        st.error(message)

uploaded_file = st.file_uploader(
    "Selecione o arquivo do comprovante:",
    type=['pdf', 'png', 'jpg', 'jpeg'],
    key='uploader',
    on_change=clear_status 
)

if uploaded_file is not None:
    if st.button("Analisar Documento"):
        st.session_state.processing = True
        st.rerun()

# --- LÓGICA DE PROCESSAMENTO (V2 - CORRIGIDA) ---
if st.session_state.processing:
    
    try:
        status_placeholder = st.empty()
        progress_bar = st.progress(0, "Iniciando análise...")
        file_bytes = uploaded_file.getvalue()

        # FASE 1: Verificação de hash (Rápida)
        progress_bar.progress(33, "Fase 1: Verificando duplicatas...")
        doc_hash = calculate_hash(file_bytes)
        
        if check_hash_in_index(doc_hash):
            # --- CAMINHO 1: HASH ENCONTRADO (REJEITADO) ---
            progress_bar.progress(100, "Concluído.")
            st.session_state.last_status = {"type": "error", "message": f"Status: **REJEITADO**. Este documento (Hash: {doc_hash[:10]}...) já existe no sistema."}
            # (Não fazemos mais nada. O código pulará para o 'finally')
            
        else:
            # --- CAMINHO 2: HASH NOVO (ACEITO PARA ANÁLISE) ---
            
            # FASE 2: Submissão para Pipeline (Rápida)
            progress_bar.progress(66, "Fase 2: Enviando para o pipeline de IA...")
            
            file_extension = os.path.splitext(uploaded_file.name)[1]
            blob_name = f"{doc_hash}{file_extension}"
            
            blob_client = st.session_state.blob_service_client.get_blob_client(container="documentos-brutos", blob=blob_name)
            
            blob_metadata = { "original_filename": uploaded_file.name }
            blob_client.upload_blob(file_bytes, metadata=blob_metadata, overwrite=True) 
            
            # FASE 3: Veredito Imediato (Rápido)
            progress_bar.progress(100, "Fase 3: Documento protocolado.")
            st.session_state.last_status = {"type": "success", "message": f"Status: **EM ANÁLISE**. O documento é novo e foi recebido com sucesso. O processamento de IA será concluído em segundo plano."}

    except Exception as e:
        # Erro genérico na submissão
        st.session_state.last_status = {"type": "error", "message": f"Falha crítica na submissão. Erro: {e}"}
    
    finally:
        # Este bloco agora é executado em AMBOS os caminhos (Rejeitado ou Em Análise)
        st.session_state.processing = False
        st.rerun() # <-- O rerun agora vai mostrar a mensagem correta