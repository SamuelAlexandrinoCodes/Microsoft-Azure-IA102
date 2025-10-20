# Sistema de Detecção de Fraudes de Documentos no Azure (v5)

Este projeto implementa um sistema de alta performance e baixo custo ("Doutrina 0800") para a prevenção de fraudes em documentos, construído inteiramente sobre a plataforma Microsoft Azure.

O objetivo principal é impedir o uso duplicado de um documento (como comprovantes, extratos ou identificações) em um processo de negócios. O sistema faz isso calculando um hash `SHA-256` único para cada arquivo e verificando-o contra um banco de dados centralizado em tempo real.

## 🚀 Arquitetura (Serverless e Orientada a Eventos)

Este projeto segue uma arquitetura moderna, assíncrona e 100% *serverless* para garantir desempenho máximo com custo zero quando ocioso.

O sistema é dividido em três componentes principais:

1.  **Frontend (Streamlit):** Uma interface web (`app.py`) onde o usuário faz o upload do documento. Esta aplicação é responsável pela "verificação rápida" (pré-checagem).
2.  **Backend (Azure Function V5):** Um "cérebro" (`function_app.py`) que é acionado instantaneamente (`Blob Trigger`) quando um novo arquivo é enviado, responsável por processar e salvar o hash.
3.  **Banco de Dados (Azure AI Search):** Utilizado como um banco de dados de hashes de alta velocidade, permitindo buscas e filtros instantâneos.

---

## ⚙️ Fluxo de Trabalho

O fluxo de verificação é projetado para dar uma resposta imediata ao usuário:

1.  **Upload:** O usuário seleciona um arquivo (PDF, PNG, etc.) na interface do Streamlit.
2.  **Cálculo (Frontend):** O `app.py` calcula o hash `SHA-256` do arquivo localmente no navegador.
3.  **Consulta (Frontend):** O `app.py` consulta o **Azure AI Search** (`ai-search-fraudes-v5`) para verificar se este hash já existe.
4.  **Veredito Imediato:**
    * **Se o hash existe (`count > 0`):** O sistema exibe **`REJEITADO`**. O processo termina.
    * **Se o hash é novo (`count == 0`):** O sistema exibe **`EM ANÁLISE`** e continua para a próxima etapa.
5.  **Upload (Assíncrono):** O `app.py` faz o upload do arquivo original para um contêiner do Azure Blob Storage (`documentos-brutos`).
6.  **Disparo (Backend):** O upload no Blob Storage aciona *imediatamente* o **Azure Function (`saofunc-backendtrigger-fraud`)**.
7.  **Processamento (Backend):** A Função V5 lê o blob, calcula seu hash (para verificação), e salva o hash e os metadados no índice do **Azure AI Search**.

Na próxima vez que o mesmo documento for enviado, o sistema o encontrará na **Etapa 4** e o rejeitará.

---

## 🏛️ Pilares do Well-Architected Framework

Este projeto foi desenhado com foco em duas prioridades principais do WAF:

* **⚡ Eficiência de Desempenho:** A arquitetura é assíncrona. O usuário nunca espera pelo processamento de backend. A checagem de duplicatas (consulta ao AI Search) leva menos de 2 segundos.
* **💰 Otimização de Custo (A "Doutrina 0800"):**
    * O **Azure AI Search** é provisionado no *Tier Gratuito (Free)*.
    * O **Azure Function App** é provisionado no *Plano de Consumo (Consumption Plan)*, que tem custo $0 quando não está processando arquivos.

---

## 🛠️ Componentes do Projeto

Este repositório está dividido em duas partes principais:

### 1. Frontend (`cloudservice/app.py`)

* **Tecnologia:** Streamlit
* **Função:** Fornece a interface de usuário (UI), calcula o hash de pré-verificação, consulta o AI Search e faz o upload do blob.

### 2. Backend (`backend-v5-trigger/function_app.py`)

* **Tecnologia:** Azure Functions (Python, Modelo v2)
* **Gatilho (Trigger):** `Blob Trigger` (monitorando o contêiner `documentos-brutos`).
* **Função:** Recebe o novo blob, calcula o hash `SHA-256` (confirmação do lado do servidor) e escreve o hash no índice do AI Search.

---

## 🔧 Configuração e Variáveis de Ambiente

Para executar este projeto, tanto o Frontend quanto o Backend precisam de credenciais para se conectar aos serviços do Azure.

### Frontend (Streamlit - arquivo `.env`)

O `app.py` espera um arquivo `.env` no mesmo diretório com as seguintes chaves:

```ini
# Chaves de conexão do Streamlit
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=..."
AZURE_SEARCH_SERVICE_NAME="ai-search-fraudes-v5"
AZURE_SEARCH_KEY="SUA_CHAVE_DE_ADMIN_DO_AI_SEARCH"