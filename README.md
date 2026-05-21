# Digi'innova. - Plateforme de Simulation d'Entretien IA 🎯

Une plateforme web moderne, élégante et ultra-généralisée codée en **Python** avec **FastAPI** pour s'entraîner aux entretiens d'embauche. L'application génère automatiquement des questions sur mesure pour n'importe quel poste cible, offre une interface de chat interactive et produit un rapport de performance complet avec notes et conseils personnalisés (propulsé par **Google Gemini AI**).

---

## 🎨 Charte Graphique (Identité Digi'innova.)
Le design visuel de l'application a été conçu de manière sur mesure à partir de la charte de couleur du logo :
* **Bleu Indigo / Navy de Marque** (`#0a0b54`) : Couleur de base structurant les cartes, les en-têtes et les arrière-plans.
* **Orange de Marque** (`#ff6700`) : Utilisé pour les boutons d'action primaire, les scores thématiques, les bordures d'inputs actives et les accents lumineux (glow).
* **Bordeaux / Marron de Marque** (`#6e0c25`) : Présent sous forme de blobs lumineux floutés en arrière-plan, de bannières d'alerte et de surbrillances.
* **Esthétique** : Mode sombre premium avec des effets de verre (glassmorphisme), des micro-animations de messages et des cercles de progression lumineux.

---

## 🚀 Fonctionnalités Clés
1. **Généralisation Totale** : Indiquez **n'importe quel poste** (ex: Développeur Python Backend, Consultant en Stratégie, Chargé de Recrutement). L'application s'adapte immédiatement sans aucune restriction !
2. **Questions Auto-programmées** : Dès la création de la simulation, l'IA pré-programme et génère 5 questions réalistes et stimulantes selon le profil ciblé.
3. **Simulation Textuelle interactive** : Un chat fluide et moderne avec indicateur d'activité ("l'IA recruteuse écrit...") et affichage dynamique des questions une à une pour éviter toute distraction.
4. **Évaluation Détaillée par IA** : Une fois l'entretien complété, l'IA produit une note globale (sur 100), une synthèse, les forces/axes d'amélioration et un feedback spécifique pour chacune de vos réponses (avec des formulations suggérées) dans un système d'accordéons interactifs.
5. **Mode Démo Robuste** : Si aucune clé API n'est fournie, l'application bascule automatiquement et gracieusement sur un **simulateur local intelligent** (mode démo). L'application est donc 100% testable immédiatement !

---

## 📂 Architecture du Projet
```text
simulation/
│
├── app/
│   ├── main.py                 # Fichier d'entrée FastAPI
│   ├── config.py               # Chargement et validation des variables (.env)
│   ├── database.py             # Sessions SQLAlchemy (SQLite)
│   │
│   ├── models/                 # Modèles de base de données (User, Session, Questions)
│   ├── schemas/                # Schémas de validation Pydantic
│   ├── routers/                # Contrôleurs et Routes (Vues HTML, Authentification, API Entretien)
│   ├── services/               # Intégration IA (SDK Google GenAI & Fallback local)
│   │
│   ├── static/                 # Ressources publiques (CSS Premium, JS Interactif)
│   └── templates/              # Templates HTML Jinja2 (Base, Accueil, Dashboard, Chat, Résultats)
│
├── requirements.txt            # Dépendances Python
├── .env                        # Variables d'environnement secrètes (.env.example fourni)
├── run.py                      # Script de lancement rapide du serveur
└── README.md                   # Ce guide
```

---

## ⚙️ Installation & Démarrage Rapide

### 1. Prérequis
Assurez-vous d'avoir **Python 3.9** ou version supérieure installé sur votre machine.

### 2. Cloner ou Ouvrir le Projet
Ouvrez votre invite de commande (PowerShell sur Windows) dans le répertoire du projet :
```powershell
cd c:\xampp\htdocs\simulation
```

### 3. Créer et Activer un Environnement Virtuel
```powershell
python -m venv venv
# Activation sous Windows
.\venv\Scripts\Activate
```

### 4. Installer les Dépendances
```powershell
pip install -r requirements.txt
```

### 5. Configurer la Clé API Gemini (Optionnel mais recommandé pour l'IA réelle)
Créez ou modifiez le fichier `.env` à la racine et renseignez votre clé obtenue gratuitement sur [Google AI Studio](https://aistudio.google.com/) :
```ini
GEMINI_API_KEY=votre_cle_api_gemini_ici
```

### 6. Lancer l'Application
Démarrez le serveur de développement en exécutant le script :
```powershell
python run.py
```
Le serveur démarrera automatiquement sur **[http://127.0.0.1:8000](http://127.0.0.1:8000)**. Ouvrez cette adresse dans votre navigateur préféré !

---

## 🛡️ Sécurité & Cookies
L'application utilise un système d'authentification basé sur des **tokens JWT stockés dans des cookies sécurisés HTTP-Only**. Cela garantit qu'aucune information d'authentification sensible n'est lisible via JavaScript client-side, protégeant ainsi vos candidats contre les failles de type XSS.
