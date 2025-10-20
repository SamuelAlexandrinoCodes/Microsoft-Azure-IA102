import logging
import json
import hashlib
import base64
import azure.functions as func

app = func.FunctionApp()

@app.route(route="CalculateHash", auth_level=func.AuthLevel.FUNCTION, methods=['POST'])
def CalculateHash(req: func.HttpRequest) -> func.HttpResponse:
    """
    Esta função é acionada por HTTP (como uma Custom Skill), 
    recebe o CONTEÚDO ORIGINAL do documento (base64) e calcula seu hash SHA-256.
    (Versão V4 - Corrigindo o input para /document/file_data)
    """
    logging.info('Função CalculateHash (Modelo V4 - Input Corrigido) recebendo um pedido.')

    try:
        body = req.get_json()
        values = body['values']
        response_values = []

        for record in values:
            record_id = record['recordId']
            result_data = { "recordId": record_id, "data": {} }

            try:
                # 1. Verifica se o input 'file_input' (vindo de /document/file_data) existe
                if 'file_input' in record['data'] and record['data']['file_input']:
                    
                    # 2. O input é o Base64 (ASCII), que é o que queríamos
                    base64_content = record['data']['file_input']
                    document_bytes = base64.b64decode(base64_content)
                    
                    # 3. Calcula o hash (o mesmo cálculo do frontend)
                    hasher = hashlib.sha256()
                    hasher.update(document_bytes)
                    document_hash = hasher.hexdigest()
                    
                    # 4. Retorna o hash
                    result_data["data"]["document_hash"] = document_hash
                
                else:
                    logging.warning(f"Nenhum 'file_input' (de /document/file_data) encontrado para o registro {record_id}.")
                    result_data["warnings"] = [{"message": "O conteúdo do arquivo (file_data) estava vazio."}]

            except Exception as e:
                # Se o erro de ASCII acontecer de novo, ele será pego aqui
                logging.error(f"Erro ao processar o registro {record_id}: {str(e)}")
                result_data["errors"] = [{"message": f"Erro interno na função: {str(e)}"}]
            
            response_values.append(result_data)

        response_body = {"values": response_values}
        return func.HttpResponse(json.dumps(response_body), mimetype="application/json")

    except Exception as e:
        logging.error(f"Erro geral no pedido: {str(e)}")
        return func.HttpResponse("Pedido inválido.", status_code=400)