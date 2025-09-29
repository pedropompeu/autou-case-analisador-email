document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('email-form');
    const resultContainer = document.getElementById('result-container');
    const errorContainer = document.getElementById('error-container');
    const categoryBadge = document.getElementById('category-badge');
    const suggestedResponse = document.getElementById('suggested-response');
    const errorMessage = document.getElementById('error-message');
    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('button-text');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Resetar estados
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
            
            // Exibir resultados
            categoryBadge.textContent = data.categoria;
            if (data.categoria === 'Produtivo') {
                categoryBadge.className = 'badge bg-success';
            } else {
                categoryBadge.className = 'badge bg-secondary';
            }

            suggestedResponse.textContent = data.sugestao_resposta;
            resultContainer.classList.remove('d-none');

        } catch (error) {
            // Exibir erro
            errorMessage.textContent = error.message;
            errorContainer.classList.remove('d-none');
        } finally {
            // Restaurar botão
            spinner.classList.add('d-none');
            buttonText.textContent = 'Analisar Email';
            form.querySelector('button').disabled = false;
        }
    });
});
