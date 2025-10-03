<div align="center">
<img src="https://notion-emojis.s3-us-west-2.amazonaws.com/prod/svg-twitter/1f680.svg" alt="Foguete" width="100">
<h1>Analisador de Emails com IA - Case Prático AutoU</h1>
<p>Uma aplicação web que utiliza a API do Google Gemini para classificar emails e sugerir respostas automaticamente, desenvolvida como parte do processo seletivo da AutoU.</p>
<p>
<img src="https://img.shields.io/badge/status-conclu%C3%ADdo-brightgreen" alt="Status: Concluído">
<img src="https://img.shields.io/badge/Python-3.11%20-blue.svg" alt="Python 3.9+">
<img src="https://img.shields.io/badge/Flask-2.0%20-black.svg" alt="Flask">
</p>
</div>

🚀 Demonstração Online
A aplicação está disponível para teste no seguinte link:

[analisador-email.onrender.com](https://analisador-email.onrender.com)

Vídeo de Apresentação: Assistir no <b>[YouTube](https://youtu.be/SMAO35yRlm8)</b>

📋 Sobre o Projeto
Este projeto é uma solução para o desafio proposto pela AutoU, que visa otimizar a gestão de emails numa empresa do setor financeiro. A aplicação automatiza a triagem de emails, classificando-os em Produtivo ou Improdutivo e gerando uma sugestão de resposta apropriada para cada categoria, liberando tempo da equipe para tarefas de maior valor.

O foco foi criar uma experiência de utilizador fluida, com uma interface limpa e funcionalidades que agregam valor, alinhada à identidade visual da AutoU.

✨ Features Principais
Classificação Inteligente: Utiliza a IA do Google Gemini para analisar o conteúdo textual.

Sugestão de Respostas: Gera respostas automáticas contextuais.

Upload de Ficheiros: Suporte para análise de emails em formato .txt e .pdf.

Interface Moderna: Design inspirado na identidade da AutoU, com tema "space-tech".

Modo Claro e Escuro: Adaptabilidade visual para preferência do utilizador.

Funcionalidade de Cópia: Botão para copiar a resposta sugerida com um clique.

Tratamento de Erros: A aplicação é resiliente e lida com limites de taxa da API de forma automática, tentando novamente antes de exibir um erro.

🛠️ Tecnologias Utilizadas
O projeto foi construído utilizando as seguintes tecnologias:

Backend: Python, Flask

Inteligência Artificial: Google Gemini API

Frontend: HTML5, CSS3, JavaScript

Framework CSS: Bootstrap 5

Bibliotecas Python: google-generativeai, PyPDF2, python-dotenv

⚙️ Como Executar Localmente
Siga os passos abaixo para configurar e executar o projeto no seu ambiente local.

Pré-requisitos
Python 3.9+

Git

Passos
Clone o repositório:

git clone [https://github.com/pedropompeu/autou-case-analisador-email.git](https://github.com/pedropompeu/autou-case-analisador-email.git)

cd autou-case-analisador-email

Crie e ative um ambiente virtual:

# Criar o ambiente
python -m venv venv

# Ativar no Windows
.\venv\Scripts\activate

# Ativar no macOS/Linux
source venv/bin/activate

Instale as dependências:

pip install -r requirements.txt

Configure a sua chave de API:

Crie um ficheiro chamado .env na raiz do projeto.

Adicione a sua chave da API do Google Gemini a este ficheiro:

GEMINI_API_KEY="SUA_CHAVE_API_AQUI"

Inicie o servidor Flask:

flask run

Acesse a aplicação:

Abra o seu navegador e acesse http://127.0.0.1:5000.

🤔 Decisões Técnicas
Uso da API do Gemini vs. NLP Tradicional: Optei por usar um modelo de linguagem avançado (LLM) como o Gemini em vez de técnicas de NLP mais antigas (remoção de stop words, stemming). Os LLMs modernos já são pré-treinados para entender o contexto e a semântica da linguagem natural, tornando o pré-processamento manual desnecessário e, por vezes, prejudicial ao resultado.

Lógica de Retentativa (Exponential Backoff): Implementei uma lógica de retentativa no backend para lidar com os limites de taxa da API do Gemini. Isso torna a aplicação mais robusta e melhora a experiência do utilizador, evitando falhas abruptas.

Design Inspirado na Identidade Visual: A interface foi cuidadosamente desenhada para refletir a identidade visual apresentada na página do case prático, demonstrando atenção ao detalhe e alinhamento com a cultura da empresa.