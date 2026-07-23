export function initAiChat() {
    const form = document.getElementById('ai-chat-form');
    const input = document.getElementById('ai-input');
    const chatWindow = document.getElementById('chat-window');

    if (!form || !input || !chatWindow) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userMsg = input.value.trim();
        if (!userMsg) return;

        // Append User Message
        const userBubble = document.createElement('div');
        userBubble.style.marginBottom = '10px';
        userBubble.style.color = '#ffffff';
        userBubble.innerHTML = `<strong>Você:</strong> ${escapeHtml(userMsg)}`;
        chatWindow.appendChild(userBubble);

        input.value = '';
        chatWindow.scrollTop = chatWindow.scrollHeight;

        // Typing indicator
        const loadingBubble = document.createElement('div');
        loadingBubble.style.marginBottom = '10px';
        loadingBubble.style.color = '#c5c6c7';
        loadingBubble.style.fontStyle = 'italic';
        loadingBubble.innerHTML = `<em>Pensando (Gemma 2 9B)...</em>`;
        chatWindow.appendChild(loadingBubble);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        try {
            // Call API Gateway endpoint or fallback direct OpenRouter API
            const apiEndpoint = window.API_GATEWAY_URL || 'https://openrouter.ai/api/v1/chat/completions';
            let responseData;

            if (apiEndpoint.includes('openrouter.ai')) {
                // Direct OpenRouter request (Free Model: google/gemma-2-9b-it:free)
                const res = await fetch(apiEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'HTTP-Referer': window.location.href,
                        'X-Title': 'Rafael Portfolio AI'
                    },
                    body: JSON.stringify({
                        model: 'google/gemma-2-9b-it:free',
                        messages: [
                            {
                                role: 'system',
                                content: 'Você é o assistente virtual do portfólio de Rafael Carvalho, Data Scientist & Engenheiro de IA. Responda em Português de forma concisa e profissional.'
                            },
                            { role: 'user', content: userMsg }
                        ]
                    })
                });
                const data = await res.json();
                responseData = data.choices ? data.choices[0].message.content : (data.error?.message || 'Sem resposta do modelo.');
            } else {
                // Call AWS Lambda via API Gateway
                const res = await fetch(apiEndpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMsg, model: 'google/gemma-2-9b-it:free' })
                });
                const data = await res.json();
                responseData = data.reply || data.error || 'Sem resposta.';
            }

            chatWindow.removeChild(loadingBubble);

            const aiBubble = document.createElement('div');
            aiBubble.style.marginBottom = '12px';
            aiBubble.style.color = '#66fcf1';
            aiBubble.innerHTML = `<strong>Assistente Gemma:</strong> ${escapeHtml(responseData)}`;
            chatWindow.appendChild(aiBubble);

        } catch (err) {
            chatWindow.removeChild(loadingBubble);
            const errBubble = document.createElement('div');
            errBubble.style.marginBottom = '10px';
            errBubble.style.color = '#ff6b6b';
            errBubble.innerHTML = `<strong>Erro:</strong> ${escapeHtml(err.message)}`;
            chatWindow.appendChild(errBubble);
        }

        chatWindow.scrollTop = chatWindow.scrollHeight;
    });
}

function escapeHtml(str) {
    return str.replace(/[&<>"']/g, function(m) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
}
