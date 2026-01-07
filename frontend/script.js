const API_URL = 'http://localhost:8000';

const fileElem = document.getElementById('fileElem');
const fileList = document.getElementById('file-list');
const uploadBtn = document.getElementById('upload-btn');
const dropArea = document.getElementById('drop-area');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');
const clearBtn = document.getElementById('clear-btn');
const logoutBtn = document.getElementById('logout-btn');

// Tabs
const navBtns = document.querySelectorAll('.nav-btn');
const viewSections = document.querySelectorAll('.view-section');

// Analysis
const analyzeBtn = document.getElementById('analyze-btn');
const analysisInput = document.getElementById('analysis-input');
const analysisResult = document.getElementById('analysis-result');

let selectedFiles = [];
let authToken = localStorage.getItem('token');

// Redirect if needed
const isAuthPage = document.body.classList.contains('auth-page');
if (!authToken && !isAuthPage) {
    window.location.href = '/static/login.html';
}
if (authToken && isAuthPage) {
    window.location.href = '/';
}

// Auth Logic (Login/Signup Pages)
const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');
const authMsg = document.getElementById('auth-msg');

if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const res = await fetch(`${API_URL}/token`, { method: 'POST', body: formData });
            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || 'Login failed');
            }
            const data = await res.json();
            localStorage.setItem('token', data.access_token);
            window.location.href = '/';
        } catch (err) {
            authMsg.textContent = err.message;
            authMsg.style.color = '#ef4444';
        }
    });
}

if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const res = await fetch(`${API_URL}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || 'Registration failed');
            }
            authMsg.textContent = 'Account created! Redirecting to login...';
            authMsg.style.color = '#10b981';
            setTimeout(() => window.location.href = '/static/login.html', 1500);
        } catch (err) {
            authMsg.textContent = err.message;
            authMsg.style.color = '#ef4444';
        }
    });
}

// Main App Logic
if (!isAuthPage) {

    // Tab Navigation
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            navBtns.forEach(b => b.classList.remove('active'));
            viewSections.forEach(s => s.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(btn.dataset.target).classList.add('active');
        });
    });

    // Logout
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('token');
            window.location.href = '/static/login.html';
        });
    }

    // Drag & Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('highlight'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('highlight'), false);
    });

    dropArea.addEventListener('drop', handleDrop, false);
    dropArea.addEventListener('click', () => fileElem.click());
    fileElem.addEventListener('change', handleFiles);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ target: { files: files } });
    }

    function handleFiles(e) {
        const files = Array.from(e.target.files);
        selectedFiles = [...selectedFiles, ...files];
        updateFileList();
        uploadBtn.disabled = selectedFiles.length === 0;
    }

    function updateFileList() {
        fileList.innerHTML = '';
        selectedFiles.forEach((file) => {
            const div = document.createElement('div');
            div.className = 'file-item';
            div.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
            fileList.appendChild(div);
        });
    }

    // Upload
    uploadBtn.addEventListener('click', async () => {
        if (selectedFiles.length === 0) return;

        uploadBtn.disabled = true;
        uploadBtn.textContent = 'Uploading...';

        // VISUAL CLEAR: Wipe chat history because backend wiped DB
        chatMessages.innerHTML = '';
        appendMessage('system', 'Clearing old context...');

        for (const file of selectedFiles) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                await fetchAuth(`${API_URL}/upload`, {
                    method: 'POST',
                    body: formData
                });
            } catch (error) {
                console.error(error);
                appendMessage('system error', `Failed to upload ${file.name}`);
            }
        }

        selectedFiles = [];
        updateFileList();
        uploadBtn.textContent = 'Upload Files';
        uploadBtn.disabled = true;

        // Confirmation Message
        appendMessage('system', 'Old memory wiped! 🧠✨');
        appendMessage('system', 'New file ready for questions.');
    });

    // Chat
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        appendMessage('user', text);
        userInput.value = '';

        const loadingId = appendMessage('bot', 'Thinking...');

        try {
            const data = await fetchAuth(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: text })
            });
            updateMessage(loadingId, data.answer);
        } catch (error) {
            updateMessage(loadingId, `Error: ${error.message}`);
            document.getElementById(loadingId).closest('.message').classList.add('error');
        }
    });

    /* Removed manual Clear DB button logic, as it is now automatic on upload */

    // Analysis
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            const text = analysisInput.value.trim();
            if (!text) return;

            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'Analyzing...';
            analysisResult.innerHTML = '';

            try {
                const data = await fetchAuth(`${API_URL}/analyze`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });

                // Render Results
                let scoreClass = 'low';
                if (data.ai_likelihood_score > 70) scoreClass = 'high';
                else if (data.ai_likelihood_score > 30) scoreClass = 'med';

                analysisResult.innerHTML = `
                    <div class="score-display">
                        <div class="score-badge ${scoreClass}">${data.ai_likelihood_score}%</div>
                        <div>
                            <strong>AI Probability</strong>
                            <p>${data.ai_likelihood_reasoning}</p>
                        </div>
                    </div>
                    
                    <div style="margin-top: 2rem;">
                        <h3>Corrected Text</h3>
                        <div class="corrected-text">${data.grammar_corrected}</div>
                    </div>

                    <div style="margin-top: 1rem;">
                        <h3>Grammar Issues Found</h3>
                        <ul class="grammar-list">
                            ${data.grammar_errors.map(err => `<li>${err}</li>`).join('')}
                        </ul>
                    </div>
                `;

            } catch (err) {
                analysisResult.textContent = `Error: ${err.message}`;
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = 'Analyze Text';
            }
        });
    }

}

// Auth Fetch Helper
async function fetchAuth(url, options = {}) {
    if (!options.headers) options.headers = {};
    if (!(options.body instanceof FormData)) {
        options.headers['Authorization'] = `Bearer ${authToken}`;
    } else {
        // For FormData, let the browser set Content-Type, but add Auth in a way that works?
        // Actually, Authorization header is standard.
        // XHR/Fetch handles FormData content-type automatically.
        options.headers['Authorization'] = `Bearer ${authToken}`;
    }

    // NOTE: If body is FormData, do NOT set Content-Type manually to json.

    const res = await fetch(url, options);
    if (res.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/static/login.html';
        throw new Error('Session expired');
    }
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Request failed');
    }
    return res.json();
}

// UI Helpers
function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    const id = 'msg-' + Date.now();

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.id = id;
    bubble.textContent = text;

    msgDiv.appendChild(bubble);
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function updateMessage(id, text) {
    const bubble = document.getElementById(id);
    if (bubble) {
        bubble.innerHTML = text.replace(/\n/g, '<br>');
    }
}
