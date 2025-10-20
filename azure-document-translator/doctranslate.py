import os
import sys
import time
import requests
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

def vanguarda_upload(blob_service_client, local_path, container_name, blob_name):
    """Carrega o documento local para o contentor de origem."""
    print(f"A iniciar upload de '{local_path}' para o contentor '{container_name}'...")
    try:
        container_client = blob_service_client.get_container_client(container_name)
        with open(local_path, "rb") as data:
            container_client.upload_blob(name=blob_name, data=data, overwrite=True)
        print("Upload concluído com sucesso.")
        return True
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: Ficheiro local não encontrado em '{local_path}'. Verifique o caminho no ficheiro .env.")
        return False
    except Exception as ex:
        print(f"ERRO NO UPLOAD: {ex}")
        return False

def preparar_zona_alvo(blob_service_client, container_name, blob_name):
    """Garante que o alvo no contentor de destino está livre."""
    print(f"\nA preparar zona alvo no contentor '{container_name}' para o blob '{blob_name}'...")
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        if blob_client.exists():
            print("Alvo existente detetado. A neutralizar...")
            blob_client.delete_blob()
            print("Zona alvo limpa.")
        else:
            print("Zona alvo já está livre.")
        return True
    except Exception as ex:
        print(f"ERRO AO LIMPAR ZONA ALVO: {ex}")
        return False

def corpo_principal_traduzir(translator_key, translator_endpoint, account_name, source_container, target_container, target_lang):
    """Aciona a API de tradução usando a doutrina superior (Identidade Gerida)."""
    url_container_origem = f"https://{account_name}.blob.core.windows.net/{source_container}"
    url_container_destino = f"https://{account_name}.blob.core.windows.net/{target_container}"

    endpoint = f"{translator_endpoint}/translator/text/batch/v1.1"
    path = "/batches"
    constructed_url = endpoint + path

    payload = {
        "inputs": [
            {
                "source": {
                    "sourceUrl": url_container_origem,
                    "storageSource": "AzureBlob",
                    "authentication": { "type": "ManagedIdentity" }
                },
                "targets": [
                    {
                        "targetUrl": url_container_destino,
                        "language": target_lang,
                        "storageSource": "AzureBlob",
                        "authentication": { "type": "ManagedIdentity" }
                    }
                ]
            }
        ]
    }
    
    headers = {'Ocp-Apim-Subscription-Key': translator_key, 'Content-Type': 'application/json'}

    print("\nA iniciar a operação de tradução de documentos...")
    try:
        response = requests.post(constructed_url, headers=headers, json=payload)
        response.raise_for_status()
        status_url = response.headers['Operation-Location']
        
        print("Operação iniciada com sucesso. A iniciar vigilância ativa...")
        while True:
            status_response = requests.get(status_url, headers={'Ocp-Apim-Subscription-Key': translator_key})
            status_response.raise_for_status()
            status_data = status_response.json()
            current_status = status_data['status']
            print(f"Status atual da operação: {current_status}")
            if current_status in ['Succeeded', 'Failed', 'Canceled']:
                break
            time.sleep(5)

        if status_data['status'] == 'Succeeded':
            print("\n--- VITÓRIA! A TRADUÇÃO FOI CONCLUÍDA. ---")
            return True
        else:
            print(f"\n--- FALHA NA MISSÃO: {status_data['status']} ---")
            if 'error' in status_data:
                print(f"Detalhe do erro: {status_data['error']['message']}")
            return False
            
    except requests.exceptions.HTTPError as http_err:
        print(f"\n--- FALHA CRÍTICA NA SUBMISSÃO: {http_err} ---")
        print(f"Relatório do servidor: {response.text}")
        return False
    except Exception as ex:
        print(f"Ocorreu um erro na tradução: {ex}")
        return False

def retaguarda_download(blob_service_client, container_name, blob_name, local_path):
    """Baixa o documento traduzido para a máquina local."""
    download_path = os.path.join(os.path.dirname(local_path), "traduzido_" + os.path.basename(local_path))
    print(f"\nA iniciar download de '{blob_name}' do contentor '{container_name}'...")
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        print(f"Download concluído. Ficheiro guardado em: '{download_path}'")
        return True
    except Exception as ex:
        print(f"ERRO NO DOWNLOAD: {ex}")
        return False

def main():
    """Ponto de Comando Principal da Operação."""
    load_dotenv()
    
    # --- CARREGAR E VALIDAR INTELIGÊNCIA DO .ENV ---
    required_vars = [
        'AZURE_TRANSLATOR_KEY', 'AZURE_TRANSLATOR_ENDPOINT', 'AZURE_STORAGE_CONNECTION_STRING',
        'SOURCE_CONTAINER_NAME', 'TARGET_CONTAINER_NAME', 'LOCAL_FILE_PATH', 'BLOB_NAME_IN_CLOUD', 'TARGET_LANGUAGE'
    ]
    config = {var: os.getenv(var) for var in required_vars}

    if any(value is None for value in config.values()):
        print("ERRO CRÍTICO: Uma ou mais variáveis essenciais não foram encontradas no ficheiro .env. Verifique o dossiê.")
        sys.exit(1) # Termina a operação

    print("--- Dossiê de Missão Validado. A iniciar Operação 'Pipeline de Batalha Total' ---")
    
    try:
        blob_service_client = BlobServiceClient.from_connection_string(config['AZURE_STORAGE_CONNECTION_STRING'])
        storage_account_name = blob_service_client.account_name
    except Exception as ex:
        print(f"ERRO CRÍTICO: A Connection String do Armazenamento é inválida. {ex}")
        sys.exit(1)

    # --- EXECUTAR FASES DA MISSÃO ---
    if vanguarda_upload(blob_service_client, config['LOCAL_FILE_PATH'], config['SOURCE_CONTAINER_NAME'], config['BLOB_NAME_IN_CLOUD']):
        if preparar_zona_alvo(blob_service_client, config['TARGET_CONTAINER_NAME'], config['BLOB_NAME_IN_CLOUD']):
            if corpo_principal_traduzir(config['AZURE_TRANSLATOR_KEY'], config['AZURE_TRANSLATOR_ENDPOINT'], storage_account_name, config['SOURCE_CONTAINER_NAME'], config['TARGET_CONTAINER_NAME'], config['TARGET_LANGUAGE']):
                retaguarda_download(blob_service_client, config['TARGET_CONTAINER_NAME'], config['BLOB_NAME_IN_CLOUD'], config['LOCAL_FILE_PATH'])

if __name__ == "__main__":
    main()