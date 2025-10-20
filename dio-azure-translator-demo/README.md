# Azure AI - Ferramenta de Tradução de Texto (CLI)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Azure](https://img.shields.io/badge/Azure-Services-0078D4)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

Uma ferramenta de linha de comando simples e interativa para tradução de texto em tempo real utilizando a API de Tradução de Texto do Azure.

## Funcionalidades

* Tradução de texto para múltiplos idiomas de uma só vez.
* Deteção automática do idioma de origem.
* Interface interativa via terminal.

## Como Executar o Projeto

### 1. Pré-requisitos

* Python 3.8+
* Uma conta do Azure.

### 2. Configuração

**a) Crie um Recurso "Tradutor" no Portal Azure.**
   * Após a criação, aceda a **"Keys and Endpoint"** para obter as suas credenciais.

**b) Configure as Variáveis de Ambiente.**
   * Crie um ficheiro chamado `.env` neste diretório.
   * Copie o conteúdo abaixo para o ficheiro e preencha com as suas credenciais do Azure.

   ```dotenv
   # Credenciais obtidas do seu recurso Tradutor no Portal Azure
   AZURE_TRANSLATOR_KEY="SUA_CHAVE_AQUI"
   AZURE_TRANSLATOR_ENDPOINT="SEU_PONTO_FINAL_AQUI"
   AZURE_TRANSLATOR_LOCATION="SUA_LOCALIZACAO_AQUI"

**c) Instale as Dependências.**
    * Abra um terminal neste diretório e execute:
    pip install -r requirements.txt (Certifique-se de que um ficheiro requirements.txt existe com as bibliotecas requests e python-dotenv)
    * Para iniciar a aplicação, execute no terminal:
    python traduzir.py