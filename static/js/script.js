document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('email-form');
    const resultContainer = document.getElementById('result-container');
    const errorContainer = document.getElementById('error-container');
    
    // Elementos do resultado
    const categoryBadge = document.getElementById('category-badge');
    const summaryText = document.getElementById('summary-text'); // Referência para o novo campo de resumo
    const suggestedResponse = document.getElementById('suggested-response');
    const copyBtn = document.getElementById('copy-btn');
    
    // Elementos de estado da UI
    const errorMessage = document.getElementById('error-message');
    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('button-text');

    // Lógica de submissão do formulário
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Resetar a interface
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
            
            const data = typeof result === 'string' ? JSON.parse(result) : result;
            
            // Preencher os resultados na interface
            categoryBadge.textContent = data.categoria;
            summaryText.textContent = data.resumo; // Preenche o novo campo de resumo
            suggestedResponse.textContent = data.sugestao_resposta;

            // Estilizar o badge da categoria com base na resposta
            if (data.categoria === 'Produtivo') {
                categoryBadge.className = 'badge bg-produtivo';
            } else {
                categoryBadge.className = 'badge bg-secondary';
            }

            resultContainer.classList.remove('d-none');

        } catch (error) {
            errorMessage.textContent = error.message;
            errorContainer.classList.remove('d-none');
        } finally {
            // Restaurar o estado do botão
            spinner.classList.add('d-none');
            buttonText.textContent = 'Analisar Email';
            form.querySelector('button').disabled = false;
        }
    });

    // Lógica para o botão de copiar
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(suggestedResponse.textContent).then(() => {
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="bi bi-check-lg"></i> Copiado!';
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
            }, 2000);
        }).catch(err => {
            console.error('Erro ao copiar texto: ', err);
        });
    });

    // Lógica para alternar o tema (dark/light mode)
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const sunIcon = '<i class="bi bi-sun-fill"></i>';
    const moonIcon = '<i class="bi bi-moon-fill"></i>';

    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-bs-theme');
        if (currentTheme === 'dark') {
            htmlElement.setAttribute('data-bs-theme', 'light');
            themeToggle.innerHTML = moonIcon;
        } else {
            htmlElement.setAttribute('data-bs-theme', 'dark');
            themeToggle.innerHTML = sunIcon;
        }
    });
});

