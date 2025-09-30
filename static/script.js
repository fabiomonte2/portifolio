document.addEventListener('DOMContentLoaded', function() {
    const messageBox = document.getElementById('message-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    
    function addMessage(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        
        const avatarImg = document.createElement('img');
        avatarImg.src = isUser ? 
            "{{ url_for('static', filename='senaguinho.png') }}" : 
            "{{ url_for('static', filename='max.png') }}";
        avatarImg.alt = isUser ? 'Usuário' : 'Max';
        
        avatarDiv.appendChild(avatarImg);
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        
        const contentP = document.createElement('p');
        contentP.textContent = text;
        
        contentDiv.appendChild(contentP);
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        messageBox.appendChild(messageDiv);
        messageBox.scrollTop = messageBox.scrollHeight;
    }
    
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        addMessage(message, true);
        userInput.value = '';
        
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mensagem: message })
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.resposta, false);
        })
        .catch(error => {
            console.error('Erro:', error);
            addMessage('Desculpe, ocorreu um erro. Tente novamente.', false);
        });
    }
    
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});