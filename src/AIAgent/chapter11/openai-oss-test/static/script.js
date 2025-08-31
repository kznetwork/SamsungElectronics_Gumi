class ChatManager {
    constructor() {
        this.conversationId = null;
        this.isStreaming = false;
        this.currentMessageDiv = null;
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.temperatureInput = document.getElementById('temperature');
        this.streamingToggle = document.getElementById('streamingToggle');
        
        this.init();
    }
    
    init() {
        // 입력 이벤트 설정
        this.messageInput.addEventListener('keydown', (e) => this.handleKeyPress(e));
        this.messageInput.addEventListener('input', () => this.handleInput());
        
        // Temperature 값 표시
        this.temperatureInput.addEventListener('input', (e) => {
            document.querySelector('.temperature-value').textContent = e.target.value;
        });
        
        // 서버 상태 확인
        this.checkServerStatus();
        setInterval(() => this.checkServerStatus(), 30000); // 30초마다 확인
        
        // 초기 상태 설정
        this.updateSendButton();
    }
    
    async checkServerStatus() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            const statusDot = document.querySelector('.status-dot');
            const statusText = document.querySelector('.status-text');
            
            if (data.gpt_oss_status === 'connected') {
                statusDot.classList.remove('disconnected');
                statusText.textContent = '연결됨';
            } else {
                statusDot.classList.add('disconnected');
                statusText.textContent = '연결 끊김';
            }
        } catch (error) {
            const statusDot = document.querySelector('.status-dot');
            const statusText = document.querySelector('.status-text');
            statusDot.classList.add('disconnected');
            statusText.textContent = '오류';
        }
    }
    
    handleKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }
    
    handleInput() {
        // 자동 높이 조절
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        
        // 문자 수 표시
        const charCount = this.messageInput.value.length;
        document.getElementById('charCount').textContent = charCount;
        
        // 전송 버튼 상태 업데이트
        this.updateSendButton();
    }
    
    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isStreaming;
    }
    
    addMessage(role, content, streaming = false) {
        // 환영 메시지 제거
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = streaming ? 'message-content streaming' : 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        
        this.scrollToBottom();
        return contentDiv;
    }
    
    async sendMessageWithStreaming(message, temperature) {
        try {
            const response = await fetch('/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    temperature: temperature,
                    conversation_id: this.conversationId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            this.currentMessageDiv = this.addMessage('assistant', '', true);
            
            let buffer = '';
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                
                buffer = lines.pop() || '';
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            
                            if (data.type === 'stream') {
                                this.currentMessageDiv.textContent += data.content;
                                this.scrollToBottom();
                            } else if (data.type === 'done') {
                                this.currentMessageDiv.classList.remove('streaming');
                                this.currentMessageDiv = null;
                                this.isStreaming = false;
                                this.updateSendButton();
                                this.setStatus('준비됨', '');
                            } else if (data.type === 'error') {
                                console.error('Error:', data.content);
                                this.setStatus('오류 발생', 'error');
                                this.isStreaming = false;
                                this.updateSendButton();
                                if (this.currentMessageDiv) {
                                    this.currentMessageDiv.classList.remove('streaming');
                                    this.currentMessageDiv.textContent += ' [오류 발생]';
                                }
                            }
                        } catch (e) {
                            console.error('Parse error:', e);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Streaming error:', error);
            this.setStatus('오류 발생', 'error');
            this.isStreaming = false;
            this.updateSendButton();
            if (this.currentMessageDiv) {
                this.currentMessageDiv.classList.remove('streaming');
                this.currentMessageDiv.textContent += ' [연결 오류]';
            }
        }
    }
    
    async sendMessageWithoutStreaming(message, temperature) {
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    temperature: temperature,
                    conversation_id: this.conversationId
                })
            });
            
            const data = await response.json();
            this.addMessage('assistant', data.response);
            
            if (!this.conversationId) {
                this.conversationId = data.conversation_id;
            }
            
            this.isStreaming = false;
            this.updateSendButton();
            this.setStatus('준비됨', '');
            
        } catch (error) {
            console.error('Error:', error);
            this.setStatus('오류 발생', 'error');
            this.isStreaming = false;
            this.updateSendButton();
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || this.isStreaming) return;
        
        // 사용자 메시지 표시
        this.addMessage('user', message);
        
        // 온도 값 가져오기
        const temperature = parseFloat(this.temperatureInput.value);
        
        // 스트리밍 옵션 확인
        const useStreaming = this.streamingToggle.checked;
        
        // 입력 초기화 및 버튼 비활성화
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        document.getElementById('charCount').textContent = '0';
        this.isStreaming = true;
        this.updateSendButton();
        this.setStatus('응답 생성 중...', 'streaming');
        
        // 메시지 전송
        if (useStreaming) {
            await this.sendMessageWithStreaming(message, temperature);
        } else {
            await this.sendMessageWithoutStreaming(message, temperature);
        }
    }
    
    sendSuggestedPrompt(prompt) {
        this.messageInput.value = prompt;
        this.handleInput();
        this.sendMessage();
    }
    
    async resetChat() {
        if (this.conversationId) {
            await fetch(`/chat/reset/${this.conversationId}`, { method: 'POST' });
        }
        
        this.conversationId = null;
        this.chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>👋 안녕하세요!</h2>
                <p>GPT-OSS와 대화를 시작해보세요.</p>
                <div class="suggested-prompts">
                    <button class="prompt-chip" onclick="chatManager.sendSuggestedPrompt('안녕하세요! 자기소개를 해주세요.')">
                        자기소개 부탁해요
                    </button>
                    <button class="prompt-chip" onclick="chatManager.sendSuggestedPrompt('파이썬으로 Hello World를 출력하는 방법을 알려주세요.')">
                        Python Hello World
                    </button>
                    <button class="prompt-chip" onclick="chatManager.sendSuggestedPrompt('오늘 날씨가 어때요?')">
                        날씨 물어보기
                    </button>
                </div>
            </div>
        `;
        this.currentMessageDiv = null;
        this.isStreaming = false;
        this.updateSendButton();
        this.setStatus('준비됨', '');
    }
    
    setStatus(text, className) {
        const statusBar = document.getElementById('statusBar');
        const status = document.getElementById('status');
        status.textContent = text;
        statusBar.className = `status-bar ${className}`;
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// 초기화
const chatManager = new ChatManager();