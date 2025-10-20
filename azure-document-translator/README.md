# Azure Document Translator Pipeline

Este projeto implementa um pipeline Python end-to-end que automatiza a tradução de documentos inteiros utilizando os Serviços de IA do Microsoft Azure.

O script orquestra uma operação na nuvem a partir de um único comando local, demonstrando uma arquitetura segura e desacoplada para o processamento de ficheiros em lote.

---

## Fluxo da Automação

O processo é executado em três fases distintas, totalmente automatizadas pelo script:

[Sua Máquina Local (documento.txt)] | |-- 1. Upload --> [Azure Blob Storage (Contentor 'origem')] | |-- 2. Tradução --> [Serviço Azure AI Translator lê o ficheiro e escreve em...] | +----------------> [Azure Blob Storage (Contentor 'destino')] | |-- 3. Download --> [Sua Máquina Local (traduzido_documento.txt)]

## Destaques Técnicos

* **Automação Completa**: Um único comando (`python doctranslate.py`) executa o upload, a limpeza da área de destino, a tradução assíncrona e o download do resultado.
* **Arquitetura Cloud**: Integra múltiplos serviços Azure (Blob Storage para armazenamento, AI Translator para processamento), demonstrando a capacidade de construir soluções na nuvem.
* **Segurança (Managed Identity)**: A autenticação crítica entre o serviço Tradutor e a Conta de Armazenamento é realizada via **Azure Managed Identity**. Esta é uma best practice de segurança que elimina a necessidade de expor ou gerir chaves de acesso (como tokens SAS) para a comunicação entre serviços.
* **Configuração Segura**: Todas as credenciais e parâmetros são geridos externamente através de um ficheiro `.env`, garantindo que nenhum dado sensível é exposto no código-fonte.

---

## Como Executar o Projeto

Para verificar este projeto, siga os três passos de configuração abaixo.

### Passo 1: Configuração no Portal Azure

Esta operação requer a seguinte infraestrutura na sua subscrição Azure:

1.  **Criar Recursos**:
    * Um **Recurso Tradutor** (Translator).
    * Uma **Conta de Armazenamento** (Storage Account).
        * Dentro da Conta de Armazenamento, crie dois **Contentores** (ex: `origem` e `destino`).

2.  **Configurar a Autenticação Segura**:
    * No seu **Recurso Tradutor**, navegue para o menu **Identidade** e **ative** a identidade gerida atribuída pelo sistema.
    * Na sua **Conta de Armazenamento**, navegue para o menu **Controlo de Acesso (IAM)**. Adicione uma atribuição de função (`Add role assignment`).
        * **Função**: `Storage Blob Data Contributor`.
        * **Atribuir a**: `Managed Identity`.
        * **Membro**: Selecione a identidade do seu Recurso Tradutor.

### Passo 2: Configuração Local

1.  **Clone o Repositório**:
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO]
    cd Microsoft-Azure-IA102/azure-document-translator
    ```

2.  **Instale as Dependências**:
    * (Opcional, mas recomendado) Crie e ative um ambiente virtual.
    * Instale as bibliotecas necessárias:
    ```bash
    pip install requests python-dotenv azure-storage-blob
    ```

3.  **Configure as Variáveis de Ambiente**:
    * Crie um ficheiro chamado `.env` neste diretório.
    * Copie o modelo abaixo para o ficheiro e preencha os valores com as suas próprias credenciais e parâmetros.

    ```dotenv
    # --- CREDENCIAIS DE SERVIÇO ---
    AZURE_TRANSLATOR_KEY="SUA_CHAVE_DO_TRADUTOR_AQUI"
    AZURE_TRANSLATOR_ENDPOINT="SEU_PONTO_FINAL_DO_TRADUTOR_AQUI"
    AZURE_STORAGE_CONNECTION_STRING="SUA_CONNECTION_STRING_DA_CONTA_DE_ARMAZENAMENTO_AQUI"

    # --- PARÂMETROS DA OPERAÇÃO ---
    SOURCE_CONTAINER_NAME="origem"
    TARGET_CONTAINER_NAME="destino"
    LOCAL_FILE_PATH="C:/caminho/completo/para/seu/documento.txt"
    BLOB_NAME_IN_CLOUD="documento_a_traduzir.txt"
    TARGET_LANGUAGE="en"
    ```

### Passo 3: Execução

* Certifique-se de que o caminho `LOCAL_FILE_PATH` no seu `.env` aponta para um ficheiro real na sua máquina.
* Execute o pipeline completo com o seguinte comando no seu terminal:
    ```bash
    python doctranslate.py
    ```
O script exibirá o progresso de cada fase e, ao final, um ficheiro traduzido aparecerá no mesmo diretório do seu ficheiro original.

---

## Detalhes do Ficheiro de Configuração (`.env`)

| Variável                        | Descrição                                                                         | Onde Encontrar no Portal Azure                                    |
| ------------------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `AZURE_TRANSLATOR_KEY`          | Chave de API para autenticar o pedido inicial.                                    | Recurso Tradutor -> `Keys and Endpoint`                           |
| `AZURE_TRANSLATOR_ENDPOINT`     | URL base do serviço de tradução.                                                  | Recurso Tradutor -> `Keys and Endpoint`                           |
| `AZURE_STORAGE_CONNECTION_STRING` | Credencial para o script Python aceder ao armazenamento (upload/download).        | Conta de Armazenamento -> `Access Keys`                           |
| `SOURCE_CONTAINER_NAME`         | Nome do contentor de onde o tradutor irá ler.                                     | Definido por si.                                                  |
| `TARGET_CONTAINER_NAME`         | Nome do contentor onde o tradutor irá escrever.                                   | Definido por si.                                                  |
| `LOCAL_FILE_PATH`               | Caminho absoluto na **sua máquina** para o ficheiro a ser traduzido. (Use `/`). | Ficheiro local.                                                   |
| `BLOB_NAME_IN_CLOUD`            | O nome que o ficheiro terá ao ser carregado para a nuvem.                           | Definido por si.                                                  |
| `TARGET_LANGUAGE`               | O código do idioma para o qual o documento será traduzido (ex: `es`, `fr`).    | [Lista de Idiomas Suportados](https://learn.microsoft.com/azure/ai-services/translator/language-support) |