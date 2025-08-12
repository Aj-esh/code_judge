// Helper function to get CSRF token for Django POST requests
function getCSRFToken(name) {
    const csrfTokenInput = document.querySelector("[name=csrfmiddlewaretoken]");
    if (csrfTokenInput) {
        return csrfTokenInput.value;
    }
    // Fallback for cookie method
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

// Dynamically updates the output section with data from the backend
function updateOutput(data) {
    const outputSection = document.querySelector(".output-section");
    if (!outputSection) return; // Guard clause if the element doesn't exist

    const tabButtons = outputSection.querySelectorAll(".tab-btn");
    const tabPanes = outputSection.querySelectorAll(".tab-pane");

    // Reset the state by hiding all tabs and panes in the output section
    tabButtons.forEach(btn => {
        btn.style.display = 'none';
        btn.classList.remove('active');
    });
    tabPanes.forEach(pane => {
        pane.style.display = 'none';
        pane.classList.remove('active');
    });

    let firstVisibleTab = null;

    // For each piece of data, populate the content and make its tab visible
    if (data.status) {
        const tabBtn = outputSection.querySelector('[data-tab="status-tab"]');
        const pane = document.getElementById("status-tab");
        pane.querySelector(".status").textContent = data.status;
        tabBtn.style.display = 'inline-block';
        if (!firstVisibleTab) firstVisibleTab = tabBtn;
    }
    if (data.coutput) {
        const tabBtn = outputSection.querySelector('[data-tab="output-tab"]');
        const pane = document.getElementById("output-tab");
        pane.querySelector(".coutput").textContent = data.coutput;
        tabBtn.style.display = 'inline-block';
        if (!firstVisibleTab) firstVisibleTab = tabBtn;
    }
    if (data.cerror) {
        const tabBtn = outputSection.querySelector('[data-tab="error-tab"]');
        const pane = document.getElementById("error-tab");
        pane.querySelector(".cerror").textContent = data.cerror;
        tabBtn.style.display = 'inline-block';
        if (!firstVisibleTab) firstVisibleTab = tabBtn;
    }
    if (data.ai_feedback) {
        const tabBtn = outputSection.querySelector('[data-tab="ai-feedback-tab"]');
        const pane = document.getElementById("ai-feedback-tab");
        pane.querySelector(".ai-feedback").textContent = data.ai_feedback;
        tabBtn.style.display = 'inline-block';
        if (!firstVisibleTab) firstVisibleTab = tabBtn;
    }

    // Activate the first tab that has new content
    if (firstVisibleTab) {
        firstVisibleTab.classList.add('active');
        const activePane = document.getElementById(firstVisibleTab.dataset.tab);
        if (activePane) {
            activePane.style.display = 'block';
            activePane.classList.add('active');
        }
    }

    // Make the entire output section visible if any data was processed
    if (data.status || data.coutput || data.cerror || data.ai_feedback) {
        outputSection.style.display = "block";
    }
}

// Handles backend API calls for "run", "submit", and "testcase" actions
function handleAction(action) {
    const container = document.querySelector(".problem-solving-container");
    if (!container) return;

    const pid = container.dataset.tab;
    const code = document.querySelector(".code-editor textarea").value;
    const language = document.querySelector(".language-selector select").value;
    const cinput = document.querySelector(".code-input-box textarea").value;

    // Make the API call
    fetch(`/problem/api/${pid}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken("csrftoken"),
        },
        body: JSON.stringify({ action, code, language, cinput }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            updateOutput({ cerror: data.error }); // Display backend error in the UI
        } else {
            updateOutput(data);
        }
    })
    .catch(error => {
        console.error("Fetch Error:", error);
        updateOutput({ cerror: `An error occurred: ${error.message}` });
    });
}

// =================================================================================
document.addEventListener("DOMContentLoaded", () => {
    // --- Element Selectors ---
    const codeEditor = document.querySelector(".code-editor textarea");
    const runButton = document.getElementById("run-btn");
    const submitButton = document.getElementById("submit-btn");
    const ctestcaseButton = document.getElementById("ctestcase-btn");

    // --- Initial UI Setup (Run Once) ---
    const codeIcon = document.querySelector(".code-icon");
    if (codeIcon) codeIcon.textContent = "</>";

    const testcaseButtonIconContainer = document.querySelector("#ctestcase-btn .svg-icon");
    if (testcaseButtonIconContainer) {
        testcaseButtonIconContainer.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <rect y="4" width="20" height="2" rx="1"></rect>
                <rect y="11" width="20" height="2" rx="1"></rect>
            </svg>
        `;
    }

    // --- Event Listeners (Attach Once) ---

    // Action Buttons
    if (runButton) runButton.addEventListener("click", (e) => { e.preventDefault(); handleAction("run"); });
    if (submitButton) submitButton.addEventListener("click", (e) => { e.preventDefault(); handleAction("submit"); });
    if (ctestcaseButton) ctestcaseButton.addEventListener("click", (e) => { e.preventDefault(); handleAction("testcase"); });

    // Scoped Tab Switching Logic (Handles both main and output tabs correctly)
    document.querySelectorAll(".tab-selector").forEach(tabContainer => {
        tabContainer.addEventListener("click", (event) => {
            if (event.target.matches('.tab-btn')) {
                const clickedButton = event.target;
                const tabButtons = tabContainer.querySelectorAll(".tab-btn");
                const contentContainer = tabContainer.nextElementSibling;

                // Deactivate all sibling buttons and hide all sibling panes
                tabButtons.forEach(btn => btn.classList.remove("active"));
                if (contentContainer) {
                    contentContainer.querySelectorAll(".tab-pane").forEach(pane => {
                        pane.classList.remove("active");
                        pane.style.display = "none";
                    });
                }

                // Activate the clicked button and its corresponding pane
                clickedButton.classList.add("active");
                const targetPane = document.getElementById(clickedButton.dataset.tab);
                if (targetPane) {
                    targetPane.classList.add("active");
                    targetPane.style.display = "block";
                }
            }
        });
    });

    // Keyboard Shortcuts
    document.addEventListener("keydown", (event) => {
        // Tab -> 4 spaces in code editor
        if (event.key === "Tab" && document.activeElement === codeEditor) {
            event.preventDefault();
            const start = codeEditor.selectionStart;
            const end = codeEditor.selectionEnd;
            codeEditor.value = codeEditor.value.substring(0, start) + "    " + codeEditor.value.substring(end);
            codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
        }

        // Ctrl+Enter -> Submit
        if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
            event.preventDefault();
            if (submitButton) submitButton.click();
        }

        // Alt+Enter -> Run
        if (event.altKey && event.key === "Enter") {
            event.preventDefault();
            if (runButton) runButton.click();
        }
    });
});