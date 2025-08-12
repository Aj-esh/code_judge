document.addEventListener("DOMContentLoaded", () => {
    document.querySelector(".code-icon").textContent = "</>";
    const testcaseButton = document.getElementById("ctestcase-btn");
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");
    const aiFeedbackButton = document.querySelector('[data-tab="ai-feedback-tab"]');


    const codeEditor = document.querySelector(".code-editor textarea");
    const submitButton = document.getElementById("submit-btn");
    const runButton = document.getElementById("run-btn");
    
    if (testcaseButton) {
        const svgIcon = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <rect y="4" width="20" height="2" rx="1"></rect>
                <rect y="11" width="20" height="2" rx="1"></rect>
            </svg>
        `;
        testcaseButton.querySelector(".svg-icon").innerHTML = svgIcon;
    }

    if (aiFeedbackButton) {
        aiFeedbackButton.innerHTML = "✨";
    }

    // Handle keyboard shortcuts - tab key
    document.addEventListener("keydown", (event) => {
        // Tab -> Space * 4 in code editor
        if (event.key === "Tab" && document.activeElement === codeEditor) {
            event.preventDefault();
            const start = codeEditor.selectionStart;
            const end = codeEditor.selectionEnd;
            codeEditor.value =
                codeEditor.value.substring(0, start) +
                "    " + // Insert 4 spaces
                codeEditor.value.substring(end);
            codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
        }

        // Ctrl+Enter -> Submit
        if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
            event.preventDefault();
            submitButton.click();
        }

        // Alt+Enter -> Run
        if (event.altKey && event.key === "Enter") {
            event.preventDefault();
            runButton.click();
        }

        // Alt+. -> Switch tabs between Chat and Problem
        if (event.altKey && event.key === ".") {
            event.preventDefault();
            const activeTab = document.querySelector(".tab-btn.active");
            const activePane = document.querySelector(".tab-pane.active");
            let nextTab, nextPane;

            if (activeTab.dataset.tab === "problem-tab") {
                nextTab = document.querySelector('[data-tab="chat-tab"]');
                nextPane = document.getElementById("chat-tab");
            } else if (activeTab.dataset.tab === "chat-tab") {
                nextTab = document.querySelector('[data-tab="problem-tab"]');
                nextPane = document.getElementById("problem-tab");
            }

            if (nextTab && nextPane) {
                tabButtons.forEach((btn) => btn.classList.remove("active"));
                tabPanes.forEach((pane) => pane.classList.remove("active"));

                nextTab.classList.add("active");
                nextPane.classList.add("active");
            }
        }
    });

    tabButtons.forEach((button) => {
        button.addEventListener("click", () => {
            // Remove active class from all buttons and panes
            tabButtons.forEach((btn) => btn.classList.remove("active"));
            tabPanes.forEach((pane) => pane.classList.remove("active"));

            // Add active class to the clicked button and corresponding pane
            button.classList.add("active");
            const targetTab = document.getElementById(button.dataset.tab);
            if (targetTab) {
                targetTab.classList.add("active");
            }
        });
    });
    
});


// backend calls
function handleAction(action) {
    const pid = document.querySelector(".problem-solving-container").dataset.tab;
    const code = document.querySelector(".code-editor textarea").value;
    const language = document.querySelector(".language-selector").value;
    const cinput = document.querySelector(".code-input-box textarea").value;
    
    // Make API call based on action
    fetch(`/problem/api/${pid}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken("csrftoken"),
        },
        body: JSON.stringify({
            action: action,
            code: code,
            language: language,
            cinput: cinput,
        }),
    })
    .then((response) => {
        if(!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
    })
    .then((data) => {
        if (data.error) {
            alert(data.error);
        } else {
            updateOutput(data);
        }
    })
    .catch((error) => {
        console.log("Error:", error);
    });
}

// helper function to get CSRF token
function getCSRFToken(name) {
    const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]");
    return csrftoken.value;
}

// update output section dynamically
function updateOutput(data) {

    // Update status
    if (data.status) {
        const statusPane = document.getElementById("status-tab");
        if (statusPane) {
            statusPane.querySelector(".status").textContent = data.status;
        }
    }

    // Update output
    if (data.coutput) {
        const outputPane = document.getElementById("output-tab");
        if (outputPane) {
            outputPane.querySelector(".coutput").textContent = data.coutput;
        }
    }

    // Update error
    if (data.cerror) {
        const errorPane = document.getElementById("error-tab");
        if (errorPane) {
            errorPane.querySelector(".cerror").textContent = data.cerror;
        }
    }

    // Update AI feedback
    if (data.ai_feedback) {
        const aiFeedbackPane = document.getElementById("ai-feedback-tab");
        if (aiFeedbackPane) {
            aiFeedbackPane.querySelector(".ai-feedback").textContent = data.ai_feedback;
        }
    }

    // Show the output section if hidden
    if (outputSection) {
        outputSection.style.display = "block";
    }
};

document.addEventListener("DOMContentLoaded", () => {
    const runButton = document.getElementById("run-btn");
    const submitButton = document.getElementById("submit-btn");
    const testcaseButton = document.getElementById("ctestcase-btn");

    if (runButton) {
        runButton.addEventListener("click", (event) => {
            event.preventDefault();
            handleAction("run");
        });
    }

    if (submitButton) {
        submitButton.addEventListener("click", (event) => {
            event.preventDefault();
            handleAction("submit");
        });
    }

    if (testcaseButton) {
        testcaseButton.addEventListener("click", (event) => {
            event.preventDefault();
            handleAction("testcase");
        });
    }
});

