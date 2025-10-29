/**
 * Retrieves the CSRF token from a meta tag or a cookie.
 * @param {string} name - The name of the cookie to look for.
 * @returns {string|null} The CSRF token value.
 */
function getCSRFToken(name) {
    const csrfTokenInput = document.querySelector(`[name=csrfmiddlewaretoken]`);
    if (csrfTokenInput) {
        return csrfTokenInput.value;
    }
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Sets the active tab and corresponding content pane.
 * @param {HTMLElement} tabSelector - The container for the tab buttons.
 * @param {HTMLElement} targetButton - The tab button to activate.
 */
function setActiveTab(tabSelector, targetButton) {
    if (!tabSelector || !targetButton) return;

    const contentSelector = tabSelector.dataset.content;
    const contentContainer = contentSelector ? document.querySelector(contentSelector) : null;
    if (!contentContainer) return;

    tabSelector.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    targetButton.classList.add('active');

    contentContainer.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
        pane.style.display = 'none';
    });

    const targetPane = contentContainer.querySelector(targetButton.dataset.target);
    if (targetPane) {
        targetPane.classList.add('active');
        targetPane.style.display = 'block';
    }
}

/**
 * Initializes a tab system.
 * @param {HTMLElement} tabSelector - The container for the tab buttons.
 * @returns {function(HTMLElement): void} A function to programmatically set an active tab.
 */
function setupTabs(tabSelector) {
    if (!tabSelector) return () => {};

    const initialButton = tabSelector.querySelector('.tab-btn.active') || tabSelector.querySelector('.tab-btn');
    if (initialButton) {
        setActiveTab(tabSelector, initialButton);
    }

    tabSelector.addEventListener('click', (event) => {
        const button = event.target.closest('.tab-btn');
        if (button && tabSelector.contains(button)) {
            event.preventDefault();
            setActiveTab(tabSelector, button);
        }
    });

    return (button) => setActiveTab(tabSelector, button);
}

/**
 * Updates the output section with data from an API response.
 * @param {object} data - The response data containing status, output, error, etc.
 */
function updateOutput(data) {
    const outputSection = document.querySelector(".output-section");
    if (!outputSection) return;

    const tabSelector = outputSection.querySelector(".tab-selector");
    const contentContainer = document.querySelector(tabSelector?.dataset.content);
    if (!tabSelector || !contentContainer) return;

    // Hide all tabs and panes initially
    tabSelector.querySelectorAll(".tab-btn").forEach(btn => {
        btn.style.display = 'none';
        btn.classList.remove('active');
    });
    contentContainer.querySelectorAll(".tab-pane").forEach(pane => {
        pane.style.display = 'none';
        pane.classList.remove('active');
    });

    let firstVisibleButton = null;

    const dataMap = {
        status: { target: '#status-pane', class: '.status' },
        coutput: { target: '#output-pane', class: '.coutput' },
        cerror: { target: '#error-pane', class: '.cerror' },
        ai_feedback: { target: '#ai-feedback-pane', class: '.ai-feedback' }
    };

    for (const key in dataMap) {
        if (data[key]) {
            const { target, class: className } = dataMap[key];
            const tabBtn = tabSelector.querySelector(`[data-target="${target}"]`);
            const pane = contentContainer.querySelector(target);
            if (tabBtn && pane) {
                pane.querySelector(className).textContent = data[key];
                tabBtn.style.display = 'inline-block';
                if (!firstVisibleButton) {
                    firstVisibleButton = tabBtn;
                }
            }
        }
    }

    if (firstVisibleButton) {
        setActiveTab(tabSelector, firstVisibleButton);
        outputSection.style.display = "block";
    }
}

/**
 * Handles API actions like 'run', 'submit', 'testcase'.
 * @param {string} action - The action to perform.
 */
function handleAction(action, editor) {
    const container = document.querySelector(".problem-solving-container");
    const languageSelect = document.querySelector(".language-selector select");
    const inputArea = document.querySelector(".code-input-box textarea");

    if (!container || !editor || !languageSelect) return;

    const pid = container.dataset.tab;
    const code = editor.getValue();
    const language = languageSelect.value;
    const cinput = inputArea ? inputArea.value : "";

    fetch(`/problem/api/${pid}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken("csrftoken"),
        },
        body: JSON.stringify({ action, code, language, cinput }),
    })
    .then(response => response.ok ? response.json() : Promise.reject(response))
    .then(data => {
        updateOutput(data.error ? { cerror: data.error } : data);
    })
    .catch(error => {
        console.error("Fetch Error:", error);
        updateOutput({ cerror: "An error occurred while processing your request." });
    });
}

/**
 * Main application entry point.
 */
document.addEventListener("DOMContentLoaded", async () => {
    // --- Element Selectors ---
    const editorDiv = document.getElementById("editor");
    const codeTextarea = document.querySelector('textarea[name="code"]');
    const mainTabSelector = document.querySelector("#main-tab-selector");
    const outputTabSelector = document.querySelector(".output-section .tab-selector");
    const problemContainer = document.querySelector(".problem-solving-container");
    const createChatSessionBtn = document.getElementById('create-chat-session-btn');
    const chatspaceTabButton = mainTabSelector?.querySelector('[data-target="#chatspace-tab"]');
    const shareContainer = document.getElementById('share-container');
    const shareUrlInput = document.getElementById('share-url');
    const copyUrlBtn = document.getElementById('copy-url-btn');
    const chatLog = document.getElementById('chat-log');
    const chatMessageInput = document.getElementById('chat-message-input');
    const chatMessageSubmit = document.getElementById('chat-message-submit');
    const languageSelect = document.querySelector(".language-selector select");

    // --- State Variables ---
    let chatSocket = null;
    let chatspaceUUID = new URLSearchParams(window.location.search).get('cs');
    const problemId = problemContainer?.dataset.tab;

    // --- Initialization ---
    if (!editorDiv || !codeTextarea) {
        console.error("Monaco Editor container or textarea not found. Aborting script.");
        return;
    }

    const editor = await initializeMonacoEditor(editorDiv, codeTextarea, languageSelect);
    if (!editor) {
        console.error("Failed to initialize Monaco Editor.");
        return;
    }

    const setActiveMainTab = setupTabs(mainTabSelector);
    setupTabs(outputTabSelector);
    initializeActionButtons(editor);
    initializeChatspace(setActiveMainTab);



    // --- Function Definitions ---

    function initializeMonacoEditor(editorDiv, textarea, languageSelect) {
    return new Promise((resolve) => {
        if (typeof require === 'undefined') {
            console.error("Monaco loader not found.");
            resolve(null);
            return;
        }

        require.config({ paths: { 'vs': 'https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs' }});
        require(['vs/editor/editor.main'], () => {
            const editor = monaco.editor.create(editorDiv, {
                value: textarea.value || "# Your code here\n",
                language: languageSelect.value,
                theme: 'vs-light',
                automaticLayout: true,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                wordWrap: 'on',
            });

            // Sync editor content to the hidden textarea on change
            editor.onDidChangeModelContent(() => {
                textarea.value = editor.getValue();
            });

            // Change editor language when the dropdown changes
            languageSelect.addEventListener('change', () => {
                monaco.editor.setModelLanguage(editor.getModel(), languageSelect.value);
            });

            resolve(editor);
        });
    });
}

    function initializeActionButtons(editor) {
        document.getElementById("run-btn")?.addEventListener("click", (e) => { e.preventDefault(); handleAction("run", editor); });
        document.getElementById("submit-btn")?.addEventListener("click", (e) => { e.preventDefault(); handleAction("submit", editor); });
        document.getElementById("ctestcase-btn")?.addEventListener("click", (e) => { e.preventDefault(); handleAction("testcase", editor); });
    }

    function initializeChatspace() {
        // If a chatspace ID is already in the URL, initialize the chat immediately.
        if (chatspaceUUID) {
            showShareUI(true); // Pass true to show the full chat UI
            setupWebSocket(chatspaceUUID);
            if (chatspaceTabButton) {
                setActiveMainTab(chatspaceTabButton);
            }
        }

        // Handle the creation of a new session.
        if (createChatSessionBtn) {
            createChatSessionBtn.addEventListener('click', () => {
                fetch('/problem/api/chatspace/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken('csrftoken'),
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.chatspace_uuid) {
                        chatspaceUUID = data.chatspace_uuid;
                        const newUrl = `${window.location.pathname}?cs=${chatspaceUUID}`;
                        history.pushState({ path: newUrl }, '', newUrl);
                        showShareUI(false); // Pass false to only show the URL to copy
                    }
                })
                .catch(error => console.error('Error creating chat session:', error));
            });
        }

        if (copyUrlBtn) {
            copyUrlBtn.addEventListener('click', () => {
                navigator.clipboard.writeText(shareUrlInput.value)
                    .then(() => {
                        copyUrlBtn.textContent = 'Copied!';
                        // Once copied, activate the WebSocket and show the chat interface.
                        setupWebSocket(chatspaceUUID);
                        document.getElementById('chat-log').style.display = 'block';
                        document.querySelector('#chat-message-input').parentElement.style.display = 'flex';
                        setTimeout(() => { copyUrlBtn.textContent = 'Copy'; }, 2000);
                    })
                    .catch(err => console.error('Failed to copy URL:', err));
            });
        }

        if (chatMessageSubmit) {
            chatMessageSubmit.addEventListener('click', sendChatMessage);
            chatMessageInput?.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') sendChatMessage();
            });
        }
    }

    function uuidv4() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    function showShareUI(showFullChat) {
        if (shareContainer && shareUrlInput) {
            shareUrlInput.value = window.location.href;
            shareContainer.style.display = 'block';
            if (createChatSessionBtn) createChatSessionBtn.style.display = 'none';

            // Conditionally show the chat log and input based on the state
            const chatLog = document.getElementById('chat-log');
            const chatInput = document.querySelector('#chat-message-input').parentElement;
            if (showFullChat) {
                chatLog.style.display = 'block';
                chatInput.style.display = 'flex';
            } else {
                chatLog.style.display = 'none';
                chatInput.style.display = 'none';
            }
        }
    }

    function appendChatMessage(message, type = 'normal') {
        if (!chatLog) return;
        const entry = document.createElement('div');
        entry.textContent = message;
        if (type === 'system') {
            entry.style.fontStyle = 'italic';
            entry.style.color = '#666';
        }
        chatLog.appendChild(entry);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function sendChatMessage() {
        if (!chatMessageInput) return;
        const message = chatMessageInput.value.trim();
        if (message && chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify({ type: 'chat_message', message }));
            chatMessageInput.value = '';
        }
    }

    function setupWebSocket(uuid) {
        if (!problemId || !uuid) return;
        if (chatSocket) chatSocket.close();

        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        chatSocket = new WebSocket(`${protocol}://${window.location.host}/ws/problem/${problemId}/${uuid}/`);

        chatSocket.onopen = () => console.log('Chat socket connected.');
        chatSocket.onclose = () => {
            console.warn('Chat socket closed.');
            chatSocket = null;
        };
        chatSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            switch (data.type) {
                case 'chat_message':
                    if (typeof data.message === 'string') {
                        appendChatMessage(data.message);
                    }
                    break;
                case 'system':
                    if (data.message) {
                        appendChatMessage(`[system] ${data.message}`, 'system');
                    }
                    break;
            }
        };
    }
});