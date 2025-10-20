# Portfólio de Projetos: Microsoft Azure AI Services

Este repositório contém uma coleção de projetos Python que demonstram a integração com vários Serviços de IA do Microsoft Azure, incluindo Tradução e Detecção de Fraudes.

## Projetos

| Projeto | Descrição | Tecnologias Principais |
| --- | --- | --- |
| **[azure-translator-demo](./azure-translator-demo/)** | Uma ferramenta de linha de comando (CLI) para tradução de texto em tempo real. Ideal para interações rápidas e testes da API de Tradução de Texto. | `Python`, `Azure Text Translation`, `REST API` |
| **[azure-document-translator](./azure-document-translator/)** | Um pipeline automatizado para tradução de documentos inteiros. O script faz o upload de um ficheiro, aciona a tradução em lote e baixa o resultado. | `Python`, `Azure Document Translation`, `Azure Blob Storage` |
| **[azure-fraud-detector](./azure-fraud-detector/)** | Um sistema *serverless* ("Doutrina 0800") para detecção de fraudes em documentos. Impede o uso duplicado de arquivos verificando um hash `SHA-256` em tempo real. | `Python`, `Azure Functions`, `Azure AI Search`, `Blob Storage`, `Streamlit` |

## Como Utilizar

Cada projeto é autocontido. Para instruções de configuração e execução, por favor, navegue até o diretório do projeto desejado e siga as instruções no seu `README.md` específico.