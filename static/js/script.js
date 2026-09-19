document.addEventListener('DOMContentLoaded', () => {

    // --- Seleção de Elementos do DOM ---
    const form = document.getElementById('email-form');
    const resultContainer = document.getElementById('result-container');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('button-text');
    const submitButton = form.querySelector('button[type="submit"]');

    const categoryBadge = document.getElementById('category-badge');
    const summaryText = document.getElementById('summary-text');
    const suggestedResponse = document.getElementById('suggested-response');
    const copyBtn = document.getElementById('copy-btn');

    const fileInput = document.getElementById('email-file');
    const filePreviewContainer = document.getElementById('file-preview-container');
    const fileNameDisplay = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file-btn');

    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;


    // --- Lógica do Upload de Ficheiro ---

    // Valida o ficheiro no momento da seleção e mostra/esconde a pré-visualização.
    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        filePreviewContainer.classList.add('d-none'); // Reseta a pré-visualização

        if (file) {
            // Validação de tamanho (2MB)
            if (file.size > 2 * 1024 * 1024) {  
                errorMessage.textContent = 'O ficheiro selecionado excede o limite de 2MB.';
                errorContainer.classList.remove('d-none');
                fileInput.value = ''; // Limpa o input
                return;
            }

            // Se o ficheiro for válido, mostra o nome
            errorContainer.classList.add('d-none');
            fileNameDisplay.textContent = file.name;
            filePreviewContainer.classList.remove('d-none');
        }
    });

    // Limpa a seleção do ficheiro ao clicar no botão "x".
    removeFileBtn.addEventListener('click', () => {
        fileInput.value = ''; 
        filePreviewContainer.classList.add('d-none'); 
    });


    // --- Lógica Principal: Submissão do Formulário ---

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Ativa o estado de carregamento da UI
        submitButton.disabled = true;
        spinner.classList.remove('d-none');
        buttonText.textContent = 'Analisando...';
        resultContainer.classList.add('d-none');
        errorContainer.classList.add('d-none');
        
        const formData = new FormData(form);

        try {
            // Envia os dados para o backend e aguarda a resposta
            const response = await fetch('/processar-email', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Ocorreu um erro desconhecido.');
            }
            
            // Preenche a UI com os resultados da análise
            categoryBadge.textContent = result.categoria;
            summaryText.textContent = result.resumo;
            suggestedResponse.textContent = result.sugestao_resposta;

            if (result.categoria === 'Produtivo') {
                categoryBadge.className = 'badge bg-produtivo';
            } else {
                categoryBadge.className = 'badge bg-secondary';
            }

            resultContainer.classList.remove('d-none');

        } catch (error) {
            errorMessage.textContent = error.message;
            errorContainer.classList.remove('d-none');
        } finally {
            // Restaura o estado original do botão, independentemente do resultado
            submitButton.disabled = false;
            spinner.classList.add('d-none');
            buttonText.textContent = 'Analisar Email';
        }
    });


    // --- Funcionalidades Extras da UI ---

    // Lida com o clique no botão de copiar
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(suggestedResponse.textContent).then(() => {
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="bi bi-check-lg"></i> Copiado!';
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
            }, 2000); // Retorna ao estado original após 2 segundos
        }).catch(err => {
            console.error('Erro ao copiar texto: ', err);
        });
    });

    // Lida com a alternância de tema (dark/light mode)
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

