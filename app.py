import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2
import io
import json

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Chave da API do Gemini não encontrada. Verifique seu arquivo .env")
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

def analyze_email_with_gemini(email_text):
    """
    Envia o texto do email para a API do Gemini para classificação e sugestão de resposta.
    """
    if not email_text or not email_text.strip():
        return {"error": "O texto do email está vazio."}

    generation_config = {
        "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
    model_name="gemini-pro-latest", 
    generation_config=generation_config
)

    prompt = f"""
    Analise o conteúdo do email a seguir e retorne uma análise estruturada em formato JSON.
Erro: Failed to fetch
    O JSON de saída deve ter duas chaves:
    1. "categoria": Classifique o email como "Produtivo" ou "Improdutivo".
       - "Produtivo": Emails que exigem uma ação (solicitações, dúvidas, etc.).
       - "Improdutivo": Emails que não necessitam de ação (felicitações, spam, etc.).
    2. "sugestao_resposta": Crie uma sugestão de resposta curta e profissional. Para emails improdutivos, a resposta pode ser "Nenhuma ação necessária.".

    Email para analisar:
    ---
    {email_text}
    ---

    Retorne apenas o objeto JSON.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
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
    Processa o email recebido via texto ou upload de arquivo.
    """
    email_text = ""
    
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        filename = file.filename.lower()

        try:
            if filename.endswith('.txt'):
                email_text = file.read().decode('utf-8')
            elif filename.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                for page in pdf_reader.pages:
                    email_text += page.extract_text()
            else:
                return jsonify({"error": "Formato de arquivo não suportado. Use .txt ou .pdf."}), 400
        except Exception as e:
            return jsonify({"error": f"Erro ao processar o arquivo: {e}"}), 500

    else:
        email_text = request.form.get('text', '')

    if not email_text.strip():
        return jsonify({"error": "Nenhum texto ou arquivo válido foi enviado."}), 400

    analysis_result_str = analyze_email_with_gemini(email_text)

    try:
        json.loads(analysis_result_str)
        return analysis_result_str, 200, {'Content-Type': 'application/json'}
    except (json.JSONDecodeError, TypeError):
        if isinstance(analysis_result_str, dict) and 'error' in analysis_result_str:
            return jsonify(analysis_result_str), 500
        return jsonify({"error": "A resposta da IA não foi um JSON válido."}), 500


@app.route('/list-models')
def list_models():
    """Lista os modelos disponíveis que sua API pode acessar."""
    try:
        models_list = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models_list.append(m.name)
        return jsonify({"available_models": models_list})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(debug=True)

