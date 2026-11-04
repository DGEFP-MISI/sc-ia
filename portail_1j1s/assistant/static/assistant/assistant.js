document.addEventListener("DOMContentLoaded", function () {
    const assistant = document.getElementById("assistant-ia");
    const closeButton = document.getElementById("assistant-ia-close");
    const form = document.getElementById("assistant-ia-form");
    const input = document.getElementById("assistant-ia-input");
    const messages = document.getElementById("assistant-ia-messages");
    const submitButton = form?.querySelector('button[type="submit"]');
    const csrfToken = form?.querySelector(
        'input[name="csrfmiddlewaretoken"]'
    );

    if (
        !assistant ||
        !closeButton ||
        !form ||
        !input ||
        !messages ||
        !submitButton ||
        !csrfToken
    ) {
        return;
    }

    let previousFocus = null;
    let requestInProgress = false;
    let historyLoading = true;

    async function restoreConversation() {
        try {
            const response = await fetch("/assistant/history/", {
                method: "GET",
                credentials: "same-origin",
                cache: "no-store"
            });
    
            if (!response.ok) {
                throw new Error("Impossible de récupérer la conversation.");
            }
    
            const data = await response.json();
    
            if (!Array.isArray(data.messages)) {
                return;
            }
    
            data.messages.forEach(function (entry) {
                if (
                    entry.role === "user" &&
                    typeof entry.content === "string"
                ) {
                    addMessage(entry.content, "fr-text--md");
                }
    
                if (
                    entry.role === "assistant" &&
                    typeof entry.content === "string"
                ) {
                    const message = addMessage(entry.content, "fr-text--sm");
                
                    if (typeof entry.content_html === "string") {
                        message.innerHTML = entry.content_html;
                    }
                }
            });
        } catch (error) {
            console.warn("Impossible de restaurer la conversation.");
        }
    }

    // Ouvrir automatiquement l'assistant sur ordinateur.
    if (window.matchMedia("(min-width: 992px)").matches) {
        assistant.hidden = false;
    }

    
    function openAssistant() {
        previousFocus = document.activeElement;
        assistant.hidden = false;
        input.focus();
    }

    function closeAssistant() {
        assistant.hidden = true;

        if (previousFocus && previousFocus.isConnected) {
            previousFocus.focus();
        }
    }

    function addMessage(content, className) {
        const message = document.createElement("p");
        message.textContent = content;
        message.className = className;

        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;

        return message;
    }

    submitButton.disabled = true;

    restoreConversation().finally(function () {
        historyLoading = false;
        submitButton.disabled = false;
    });

    document.querySelectorAll("[data-assistant-open]").forEach(function (button) {
        button.addEventListener("click", openAssistant);
    });

    closeButton.addEventListener("click", closeAssistant);

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !assistant.hidden) {
            closeAssistant();
        }
    });

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const question = input.value.trim();

        if (!question || requestInProgress || historyLoading) {
            return;
        }

        requestInProgress = true;
        submitButton.disabled = true;

        addMessage(question, "fr-text--md");
        input.value = "";

        const waitingMessage = addMessage(
            "L'assistant prépare sa réponse…",
            "fr-text--sm"
        );

        try {
            const response = await fetch("/assistant/chat/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken.value
                },
                body: JSON.stringify({
                    message: question
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Une erreur est survenue."
                );
            }

            waitingMessage.innerHTML =
                data.answer_html || "L'assistant n'a pas retourné de réponse.";

        } catch (error) {
            waitingMessage.textContent =
                error.message || "Impossible de contacter l'assistant.";

        } finally {
            requestInProgress = false;
            submitButton.disabled = false;
            messages.scrollTop = messages.scrollHeight;
            input.focus();
        }
    });
});
