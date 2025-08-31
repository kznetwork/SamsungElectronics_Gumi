// marked.js 설정: 링크가 새창에서 열리도록 설정
// 이 설정은 전역적으로 적용되므로, 앱 초기화와 분리할 수 있습니다.
const renderer = {
  link(href, title, text) {
    // marked.js의 기본 링크 렌더러를 호출합니다.
    const link = marked.Renderer.prototype.link.call(this, href, title, text);
    // 생성된 <a> 태그에 target="_blank"와 rel="noreferrer"를 추가합니다.
    return link.replace("<a", "<a target='_blank' rel='noreferrer' ");
  },
};

marked.use({
  renderer,
});

/**
 * 고유한 세션 ID를 생성합니다.
 * @returns {string} 생성된 세션 ID
 */
const generateSessionId = () => {
  const timestamp = Date.now();
  const randomString = Math.random().toString(36).substring(2, 9);
  return `session_${timestamp}_${randomString}`;
};

/**
 * 채팅 애플리케이션을 관리하는 모듈
 */
const ChatApp = {
  // DOM 요소들을 저장할 객체
  elements: {
    chatForm: null,
    chatInput: null,
    chatBox: null,
  },
  // 세션 ID
  sessionId: null,

  /**
   * 애플리케이션을 초기화합니다.
   */
  init() {
    // DOM 요소들을 찾아서 저장합니다.
    this.elements.chatForm = document.getElementById("chat-form");
    this.elements.chatInput = document.getElementById("chat-input");
    this.elements.chatBox = document.getElementById("chat-box");

    // 세션 ID를 생성하고 로그에 기록합니다.
    this.sessionId = generateSessionId();
    console.log("새로운 세션 ID:", this.sessionId);

    // 이벤트 리스너를 등록합니다.
    this.elements.chatForm.addEventListener(
      "submit",
      this.handleFormSubmit.bind(this)
    );
  },

  /**
   * 채팅 폼 제출 이벤트를 처리합니다.
   * @param {Event} e - 폼 제출 이벤트
   */
  async handleFormSubmit(e) {
    e.preventDefault();
    const message = this.elements.chatInput.value.trim();

    if (!message) {
      return;
    }

    // 사용자 메시지를 화면에 추가합니다.
    this.appendMessage("user", message);
    this.elements.chatInput.value = "";

    // 봇의 응답을 스트리밍하기 시작합니다.
    const botMessageElement = this.createMessageElement("bot");
    await this.streamBotResponse(message, botMessageElement);
  },

  /**
   * 서버로부터 봇의 응답을 스트리밍합니다.
   * @param {string} message - 사용자가 보낸 메시지
   * @param {HTMLElement} botMessageElement - 봇 메시지를 표시할 요소
   */
  async streamBotResponse(message, botMessageElement) {
    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          message: message,
          session_id: this.sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let content = "";

      // 스트림을 읽어서 화면에 점진적으로 표시합니다.
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        content += decoder.decode(value, { stream: true });
        botMessageElement.innerHTML = marked.parse(content);
        this.scrollToBottom();
      }
    } catch (error) {
      console.error("스트리밍 중 오류 발생:", error);
      botMessageElement.innerHTML =
        "죄송합니다. 메시지를 처리하는 중 오류가 발생했습니다.";
    }
  },

  /**
   * 새로운 메시지 요소를 생성하고 DOM에 추가합니다.
   * @param {string} sender - 메시지를 보낸 사람 ('user' 또는 'bot')
   * @returns {HTMLElement} 생성된 메시지 요소
   */
  createMessageElement(sender) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", `${sender}-message`);
    this.elements.chatBox.appendChild(messageElement);
    this.scrollToBottom();
    return messageElement;
  },

  /**
   * 메시지를 화면에 추가합니다.
   * @param {string} sender - 메시지를 보낸 사람
   * @param {string} text - 메시지 내용
   */
  appendMessage(sender, text) {
    const messageElement = this.createMessageElement(sender);
    messageElement.innerHTML = marked.parse(text);
  },

  /**
   * 채팅 박스를 맨 아래로 스크롤합니다.
   */
  scrollToBottom() {
    this.elements.chatBox.scrollTop = this.elements.chatBox.scrollHeight;
  },
};

// DOM이 로드되면 애플리케이션을 초기화합니다.
document.addEventListener("DOMContentLoaded", () => {
  ChatApp.init();
});
