document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('email-form');
    const resultContainer = document.getElementById('result-container');
    const errorContainer = document.getElementById('error-container');
    const categoryBadge = document.getElementById('category-badge');
    const suggestedResponse = document.getElementById('suggested-response');
    const errorMessage = document.getElementById('error-message');
    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('button-text');
    const copyBtn = document.getElementById('copy-btn');
    const copyBtnText = document.getElementById('copy-btn-text');
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('i');
    const htmlElement = document.documentElement;

    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-bs-theme', savedTheme);
    themeIcon.className = savedTheme === 'dark' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
    
    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        htmlElement.setAttribute('data-bs-theme', newTheme);
        themeIcon.className = newTheme === 'dark' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
        localStorage.setItem('theme', newTheme);
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        resultContainer.classList.add('d-none');
        errorContainer.classList.add('d-none');
        spinner.classList.remove('d-none');
        buttonText.textContent = 'Analisando...';
        form.querySelector('button').disabled = true;
        
        const formData = new FormData(form);

        try {
            const response = await fetch('/processar-email', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Ocorreu um erro desconhecido.');
            }
            
            // O resultado da OpenAI pode vir como uma string JSON, então precisamos parsear de novo
            const data = typeof result === 'string' ? JSON.parse(result) : result;
            
            categoryBadge.textContent = data.categoria;
            if (data.categoria === 'Produtivo') {
                categoryBadge.className = 'badge bg-success';
            } else {
                categoryBadge.className = 'badge bg-secondary';
            }

            suggestedResponse.textContent = data.sugestao_resposta;
            resultContainer.classList.remove('d-none');

        } catch (error) {
            errorMessage.textContent = error.message;
            errorContainer.classList.remove('d-none');
        } finally {
            spinner.classList.add('d-none');
            buttonText.textContent = 'Analisar Email';
            form.querySelector('button').disabled = false;
        }
    });
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(suggestedResponse.textContent).then(() => {
            const originalIcon = copyBtn.querySelector('i').className;
            copyBtn.querySelector('i').className = 'bi bi-check-lg';
            copyBtnText.textContent = 'Copiado!';

            setTimeout(() => {
                copyBtn.querySelector('i').className = originalIcon;
                copyBtnText.textContent = 'Copiar';
            }, 2000);
        }).catch(err => {
            console.error('Erro ao copiar texto: ', err);
            alert('Falha ao copiar o texto. Por favor, copie manualmente.');
        });
    });
});
