// Logic for the interactive mock interview simulator (Digi'innova.)

document.addEventListener("DOMContentLoaded", () => {
    // S'assurer qu'on est bien sur la page de simulation d'entretien
    const chatMessages = document.getElementById("chat-messages");
    if (!chatMessages) return;

    const sessionDataEl = document.getElementById("session-data");
    const sessionId = parseInt(sessionDataEl.dataset.sessionId);
    const jobTitle = sessionDataEl.dataset.jobTitle;

    // Charger les questions injectées
    const questions = JSON.parse(sessionDataEl.dataset.questionsJson);

    let currentQuestionIndex = 0;
    const totalQuestions = questions.length;

    const answerTextarea = document.getElementById("candidate-answer");
    const sendButton = document.getElementById("btn-send");
    const charCounter = document.getElementById("char-count");
    const steps = document.querySelectorAll(".step-item");
    const loadingScreen = document.getElementById("loading-screen");
    const loadingStatusText = document.getElementById("loading-status-text");

    // 1. Initialiser le compteur de caractères
    if (answerTextarea) {
        answerTextarea.addEventListener("input", () => {
            const count = answerTextarea.value.length;
            charCounter.textContent = `${count} / 1500`;
            
            // Activer ou désactiver le bouton envoyer selon le contenu
            sendButton.disabled = count.trim ? count.trim() === 0 : count === 0;
        });

        // Envoyer la réponse avec Ctrl+Entrée ou Entrée (si non vide)
        answerTextarea.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                if (answerTextarea.value.trim().length > 0) {
                    sendAnswer();
                }
            }
        });
    }

    async function parseJsonResponse(response) {
        try {
            return await response.json();
        } catch (err) {
            const text = await response.text().catch(() => "");
            return { detail: text || response.statusText || "Réponse serveur invalide." };
        }
    }

    if (sendButton) {
        sendButton.addEventListener("click", sendAnswer);
    }

    // 2. Lancer la première question au chargement de l'écran
    initInterview();

    function initInterview() {
        if (totalQuestions === 0) {
            appendSystemMessage("Erreur: Aucune question n'a été initialisée pour cet entretien.");
            return;
        }

        // Afficher l'avatar et un message d'accueil initial de l'IA
        showAITypingIndicator();

        setTimeout(() => {
            hideAITypingIndicator();
            appendAIMessage(`Bonjour ! Bienvenue dans cette simulation d'entretien Digi'innova pour le poste de **${jobTitle}**.\n\nJe suis votre recruteur virtuel. Nous allons procéder à un échange de ${totalQuestions} questions. Commençons tout de suite.\n\n**Question 1 :** ${questions[0].question_text}`);
            
            // Activer l'étape 1
            updateSidebarProgress(0);
            enableInput();
        }, 1500);
    }

    // 3. Soumettre une réponse
    async function sendAnswer() {
        const text = answerTextarea.value.trim();
        if (!text) return;

        // Désactiver la saisie
        disableInput();

        // 1. Ajouter le message du candidat à l'écran
        appendCandidateMessage(text);
        answerTextarea.value = "";
        charCounter.textContent = "0 / 1500";

        // Récupérer les infos de la question en cours
        const currentQuestion = questions[currentQuestionIndex];

        try {
            // 2. Envoyer la réponse à l'API backend
            const response = await fetch(`/api/interviews/${sessionId}/answer`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question_id: currentQuestion.id,
                    answer_text: text
                })
            });

            const data = await parseJsonResponse(response);

            if (!response.ok) {
                throw new Error(data.detail || "Erreur de transmission de la réponse.");
            }

            // Marquer l'étape latérale en complétée
            markSidebarStepCompleted(currentQuestionIndex);

            // Passer à la question suivante
            currentQuestionIndex++;

            if (currentQuestionIndex < totalQuestions) {
                // Poser la question suivante
                showAITypingIndicator();
                setTimeout(() => {
                    hideAITypingIndicator();
                    
                    const nextQ = questions[currentQuestionIndex];
                    appendAIMessage(`Merci pour votre réponse. Passons à la question suivante.\n\n**Question ${currentQuestionIndex + 1} :** ${nextQ.question_text}`);
                    
                    updateSidebarProgress(currentQuestionIndex);
                    enableInput();
                }, 1800);
            } else {
                // Entretien terminé, lancer l'évaluation
                showAITypingIndicator();
                setTimeout(() => {
                    hideAITypingIndicator();
                    appendAIMessage("Toutes mes félicitations ! Nous venons de terminer notre échange. Je vais maintenant procéder à l'analyse complète de vos réponses. Cela prendra quelques instants...");
                    
                    // Lancer la routine de chargement d'évaluation
                    triggerEvaluation();
                }, 1500);
            }

        } catch (err) {
            appendSystemMessage(`Erreur de connexion : ${err.message}. Veuillez réessayer en renvoyant votre message.`);
            enableInput();
        }
    }

    // 4. Lancer l'analyse et l'évaluation finale
    async function triggerEvaluation() {
        // Afficher l'écran de chargement plein écran
        loadingScreen.style.display = "flex";
        
        // Notifications de progression simulées pour un effet premium
        const progressMessages = [
            "Analyse sémantique de vos réponses...",
            "Évaluation de l'adéquation avec le profil recherché...",
            "Calcul des scores thématiques (communication, clarté)...",
            "Rédaction des conseils de correction sur mesure...",
            "Finalisation du rapport d'entretien Digi'innova..."
        ];

        let msgIdx = 0;
        const intervalId = setInterval(() => {
            if (msgIdx < progressMessages.length) {
                loadingStatusText.textContent = progressMessages[msgIdx];
                msgIdx++;
            }
        }, 3000);

        try {
            // Appeler l'API d'évaluation finale
            const response = await fetch(`/api/interviews/${sessionId}/evaluate`, {
                method: "POST"
            });

            const data = await parseJsonResponse(response);

            clearInterval(intervalId);

            if (!response.ok) {
                throw new Error(data.detail || "L'évaluation par l'IA a échoué.");
            }

            loadingStatusText.textContent = "Évaluation terminée ! Redirection vers vos résultats...";

            // Redirection après 1s de succès
            setTimeout(() => {
                window.location.href = `/interview/${sessionId}/results`;
            }, 1000);

        } catch (err) {
            clearInterval(intervalId);
            loadingScreen.style.display = "none";
            appendSystemMessage(`Erreur d'évaluation : ${err.message}. Vous pouvez rafraîchir la page et cliquer sur le bouton de fin d'entretien pour relancer l'analyse.`);
        }
    }

    // ==========================================================================
    // UTILS : Manipulation du Chat et Dom
    // ==========================================================================

    function appendAIMessage(text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = "message ai";
        
        // Convertir le markdown simple (comme les gras **) en HTML
        const htmlContent = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');

        msgDiv.innerHTML = `
            <span class="message-sender">Recruteur Digi'innova</span>
            <div class="message-bubble">${htmlContent}</div>
        `;
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendCandidateMessage(text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = "message candidate";
        
        // Sécuriser les entrées utilisateur
        const safeText = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, '<br>');

        msgDiv.innerHTML = `
            <span class="message-sender">Vous</span>
            <div class="message-bubble">${safeText}</div>
        `;
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendSystemMessage(text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = "message system";
        msgDiv.style.alignSelf = "center";
        msgDiv.style.maxWidth = "90%";
        msgDiv.innerHTML = `
            <div class="message-bubble" style="background: rgba(110, 12, 37, 0.2); border: 1px solid rgba(110, 12, 37, 0.4); color: #ff8fa5; font-size: 13px; text-align: center; border-radius: 8px;">
                ${text}
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function showAITypingIndicator() {
        const typingDiv = document.createElement("div");
        typingDiv.className = "message ai typing-indicator-wrapper";
        typingDiv.innerHTML = `
            <span class="message-sender">Recruteur Digi'innova</span>
            <div class="message-bubble" style="padding: 8px 12px; background: rgba(10, 11, 84, 0.2);">
                <div class="typing-indicator">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    function hideAITypingIndicator() {
        const indicator = chatMessages.querySelector(".typing-indicator-wrapper");
        if (indicator) {
            indicator.remove();
        }
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function enableInput() {
        answerTextarea.disabled = false;
        sendButton.disabled = answerTextarea.value.trim().length === 0;
        answerTextarea.focus();
    }

    function disableInput() {
        answerTextarea.disabled = true;
        sendButton.disabled = true;
    }

    // Gestion du panneau latéral
    function updateSidebarProgress(index) {
        steps.forEach((step, i) => {
            if (i === index) {
                step.classList.add("active");
            } else {
                step.classList.remove("active");
            }
        });
    }

    function markSidebarStepCompleted(index) {
        if (steps[index]) {
            steps[index].classList.remove("active");
            steps[index].classList.add("completed");
        }
    }
});
