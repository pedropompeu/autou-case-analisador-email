import os
import time
import io
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions
import PyPDF2

load_dotenv()

# Carrega e valida a chave da API do Gemini a partir das variáveis de ambiente
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Chave da API do Gemini não encontrada. Verifique seu ficheiro .env")
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Define um limite de upload de 2MB

# --- Lógica Principal da IA ---

def analyze_email_with_gemini(email_text: str) -> dict | str:
    """
    Envia o texto do email para a API do Gemini, com lógica de retentativa.

    Args:
        email_text (str): O conteúdo completo do email a ser analisado.

    Returns:
        dict | str: O resultado da IA como uma string JSON em caso de sucesso,
                    ou um dicionário de erro em caso de falha.
    """
    if not email_text or not email_text.strip():
        return {"error": "O texto do email está vazio."}

    generation_config = {
        "response_mime_type": "application/json",
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest", 
        generation_config=generation_config
    )

    prompt = f"""
    Analise o conteúdo do email a seguir e retorne uma análise estruturada em formato JSON.

    O JSON de saída deve ter três chaves:
    1. "categoria": Classifique o email como "Produtivo" ou "Improdutivo".
       - "Produtivo": Emails que exigem uma ação (solicitações, dúvidas, relatórios, documentações, etc.).
       - "Improdutivo": Emails que não necessitam de ação (felicitações, spam, etc.).
    2. "resumo": Crie um resumo conciso de uma frase sobre o que se trata o email.
    3. "sugestao_resposta": 
       - Se a categoria for "Produtivo", elabore uma resposta curta e profissional que possa ser usada como ponto de partida.
       - Se a categoria for "Improdutivo", o valor desta chave deve ser "Nenhuma ação necessária.".

    Email para analisar:
    ---
    {email_text}
    ---

    Retorne apenas o objeto JSON.
    """
    
    # Lógica de retentativa para lidar com os limites da API (Rate Limit)
    max_retries = 3
    delay = 15
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except exceptions.ResourceExhausted:
            if attempt < max_retries - 1:
                print(f"Rate limit atingido. Tentando novamente em {delay} segundos...")
                time.sleep(delay)
                delay *= 2.5 
            else:
                print("Máximo de retentativas atingido. Falha na chamada da API.")
                return {"error": "A API está sobrecarregada, tente novamente mais tarde."}
        except Exception as e:
            print(f"Erro inesperado na API do Gemini: {e}")
            return {"error": f"Ocorreu um erro ao comunicar com a IA."}

# --- Rotas da Aplicação (Endpoints) ---

@app.route('/')
def index() -> str:
    """Renderiza a página principal da aplicação (index.html)."""
    return render_template('index.html')


@app.route('/processar-email', methods=['POST'])
def processar_email():
    """
    Recebe os dados do formulário, processa o texto e o ficheiro,
    chama a função de análise da IA e retorna o resultado formatado.
    """
    body_text = request.form.get('text', '').strip()
    attachment_text = ""
    
    # Processa o ficheiro de anexo, se existir
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        try:
            if file.filename.lower().endswith('.txt'):
                attachment_text = file.read().decode('utf-8')
            elif file.filename.lower().endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                attachment_text = "".join(page.extract_text() for page in pdf_reader.pages)
            else:
                return jsonify({"error": "Formato de ficheiro não suportado. Use .txt ou .pdf."}), 400
        except Exception as e:
            print(f"Erro ao processar o ficheiro: {e}")
            return jsonify({"error": "Ocorreu um erro ao processar o ficheiro."}), 500

    # Combina o texto do corpo e do anexo para uma análise completa
    full_email_text = body_text
    if attachment_text:
        full_email_text += f"\n\n--- CONTEÚDO DO ANEXO ---\n{attachment_text}"

    if not full_email_text.strip():
        return jsonify({"error": "Nenhum texto ou ficheiro válido foi enviado."}), 400

    analysis_result = analyze_email_with_gemini(full_email_text)

    # Trata a resposta para o frontend, diferenciando sucesso de erro
    if isinstance(analysis_result, dict) and 'error' in analysis_result:
        return jsonify(analysis_result), 503  # Retorna erro de serviço indisponível
    
    try:
        json.loads(analysis_result)
        return analysis_result, 200, {'Content-Type': 'application/json'}
    except (json.JSONDecodeError, TypeError):
        return jsonify({"error": "A resposta da IA não foi um JSON válido."}), 500

if __name__ == '__main__':
    app.run(debug=True)

