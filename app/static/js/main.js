// Global JS for Digi'innova. Simulation

document.addEventListener("DOMContentLoaded", () => {
    // 1. Gestion des onglets de connexion / inscription
    const tabs = document.querySelectorAll(".auth-tab");
    const forms = document.querySelectorAll(".auth-form");

    if (tabs.length > 0 && forms.length > 0) {
        tabs.forEach(tab => {
            tab.addEventListener("click", () => {
                const target = tab.dataset.tab;

                // Désactiver tous les onglets
                tabs.forEach(t => t.classList.remove("active"));
                tab.classList.add("active");

                // Cacher tous les formulaires
                forms.forEach(f => f.classList.remove("active"));
                document.getElementById(`${target}-form`).classList.add("active");
                
                // Cacher les alertes en changeant d'onglet
                const alerts = document.querySelectorAll(".form-alert");
                alerts.forEach(a => a.style.display = "none");
            });
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

    // 2. Soumission asynchrone de l'inscription
    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const alertBox = document.getElementById("register-alert");
            alertBox.style.display = "none";

            const username = document.getElementById("reg-username").value.strip ? document.getElementById("reg-username").value.strip() : document.getElementById("reg-username").value.trim();
            const email = document.getElementById("reg-email").value.strip ? document.getElementById("reg-email").value.strip() : document.getElementById("reg-email").value.trim();
            const password = document.getElementById("reg-password").value;

            try {
                const response = await fetch("/auth/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await parseJsonResponse(response);

                if (!response.ok) {
                    throw new Error(data.detail || "Une erreur est survenue lors de l'inscription.");
                }

                // Succès : Afficher un message et basculer sur l'onglet connexion
                alertBox.style.background = "rgba(0, 200, 83, 0.15)";
                alertBox.style.borderColor = "rgba(0, 200, 83, 0.4)";
                alertBox.style.color = "#a7ffeb";
                alertBox.textContent = "Inscription réussie ! Vous pouvez maintenant vous connecter.";
                alertBox.style.display = "block";

                registerForm.reset();

                // Bascule automatique vers Connexion après 1.5s
                setTimeout(() => {
                    document.querySelector('[data-tab="login"]').click();
                    // Transférer l'identifiant pour aider l'utilisateur
                    document.getElementById("log-identifier").value = username;
                }, 1500);

            } catch (err) {
                alertBox.style.background = "rgba(110, 12, 37, 0.2)";
                alertBox.style.borderColor = "rgba(110, 12, 37, 0.4)";
                alertBox.style.color = "#ff8fa5";
                alertBox.textContent = err.message;
                alertBox.style.display = "block";
            }
        });
    }

    // 3. Soumission asynchrone de la connexion
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const alertBox = document.getElementById("login-alert");
            alertBox.style.display = "none";

            const identifier = document.getElementById("log-identifier").value.trim();
            const password = document.getElementById("log-password").value;

            try {
                const response = await fetch("/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username_or_email: identifier, password })
                });

                const data = await parseJsonResponse(response);

                if (!response.ok) {
                    throw new Error(data.detail || "Identifiants incorrects.");
                }

                // Connexion réussie, redirection vers le tableau de bord
                window.location.href = "/dashboard";

            } catch (err) {
                alertBox.textContent = err.message;
                alertBox.style.display = "block";
            }
        });
    }

    // Accordéons sur la page de résultats
    const qaCards = document.querySelectorAll(".qa-card");
    if (qaCards.length > 0) {
        qaCards.forEach(card => {
            const header = card.querySelector(".qa-header");
            header.addEventListener("click", () => {
                card.classList.toggle("open");
            });
        });
    }
});
