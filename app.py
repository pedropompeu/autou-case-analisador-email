import os
import time
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions
import PyPDF2
import io
import json

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar a chave da API do Gemini a partir do .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Chave da API do Gemini não encontrada. Verifique seu arquivo .env")
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limite de upload de arquivo de 2MB

def analyze_email_with_gemini(email_text):
    """
    Envia o texto do email para a API do Gemini com lógica de retentativa e prompt aprimorado.
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
    
    max_retries = 3
    delay = 15
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except exceptions.ResourceExhausted as e:
            if attempt < max_retries - 1:
                print(f"Rate limite atingido. Tentando novamente em {delay} segundos...")
                time.sleep(delay)
                delay *= 2.5 
            else:
                print("Máximo de retentativas atingido. Falha na chamada da API.")
                return {"error": "A API está sobrecarregada, tente novamente mais tarde."}
        except Exception as e:
            print(f"Erro na API do Gemini: {e}")
            error_message = str(e)
            if "API key not valid" in error_message:
                return {"error": "A chave da API do Gemini não é válida. Verifique a chave no arquivo .env."}
            return {"error": f"Ocorreu um erro ao comunicar com a IA: {error_message}"}


@app.route('/')
def index():
    """Renderiza a página principal."""
    return render_template('index.html')


@app.route('/processar-email', methods=['POST'])
def processar_email():
    """
    Processa o email recebido, combinando o texto do corpo e do anexo.
    """
    body_text = request.form.get('text', '').strip()
    attachment_text = ""
    
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        filename = file.filename.lower()

        try:
            if filename.endswith('.txt'):
                attachment_text = file.read().decode('utf-8')
            elif filename.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                for page in pdf_reader.pages:
                    attachment_text += page.extract_text()
            else:
                return jsonify({"error": "Formato de arquivo não suportado. Use .txt ou .pdf."}), 400
        except Exception as e:
            return jsonify({"error": f"Erro ao processar o arquivo: {e}"}), 500

    # Combinar o texto do corpo e do anexo
    full_email_text = body_text
    if attachment_text:
        full_email_text += f"\n\n--- CONTEÚDO DO ANEXO ---\n{attachment_text}"

    if not full_email_text.strip():
        return jsonify({"error": "Nenhum texto ou arquivo válido foi enviado."}), 400

    analysis_result = analyze_email_with_gemini(full_email_text)

    # Verifica se a função de análise já retornou um dicionário de erro (ex: API sobrecarregada)
    if isinstance(analysis_result, dict) and 'error' in analysis_result:
        # Se for, retorna-o diretamente como um JSON de erro.
        return jsonify(analysis_result), 503
    
    try:
        # Se não for um erro, prossegue como normal
        json.loads(analysis_result)
        return analysis_result, 200, {'Content-Type': 'application/json'}
    except (json.JSONDecodeError, TypeError):
        # Este bloco trata o caso de a IA retornar um JSON mal formatado
        return jsonify({"error": "A resposta da IA não foi um JSON válido."}), 500

if __name__ == '__main__':
    app.run(debug=True)

