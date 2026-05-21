import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Tente d'importer le client Gemini officiel
HAS_GEMINI_SDK = False
try:
    from google import genai
    from google.genai import types
    HAS_GEMINI_SDK = True
except ImportError:
    logger.warning("Le package google-genai n'est pas disponible. Mode Démo actif.")

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        self.is_mock = True

        if HAS_GEMINI_SDK and self.api_key and self.api_key.strip():
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.is_mock = False
                logger.info("Service Gemini IA initialisé avec succès en mode réel.")
            except Exception as e:
                logger.error(f"Erreur d'initialisation du client Gemini : {e}. Passage en mode Démo.")
        else:
            logger.info("Clé API Gemini absente ou invalide. Utilisation du mode Démo (Mock).")

    def generate_questions(self, job_title: str, job_description: str = "", count: int = 5) -> list[str]:
        """
        Génère une liste de questions d'entretien adaptées au poste spécifié.
        """
        if self.is_mock:
            return self._generate_mock_questions(job_title, count)

        prompt = f"""
        Tu es un recruteur expert et chevronné.
        Pour le poste : "{job_title}"
        {f"Description du poste / contexte supplémentaire : {job_description}" if job_description else ""}

        Analyse le rôle, identifie les compétences attendues et génère exactement {count} questions d'entretien réalistes, professionnelles et ciblées.

        Exigences :
        - Rédige les questions en français, claires et orientées métier.
        - Inclue 1-2 questions situationnelles ou comportementales avec un contexte concret.
        - Inclue 1-2 questions techniques ou opérationnelles liées aux missions.
        - Inclue au moins 1 question sur la motivation, l'adéquation culturelle ou l'ambition du candidat.
        - Si le poste est de niveau junior, intermédiaire ou senior, adapte le niveau des questions.

        Exemples de questions attendues :
        - "Décrivez une situation où vous avez dû gérer un conflit d'équipe et comment vous l'avez résolu."
        - "Comment priorisez-vous vos tâches quand les demandes sont nombreuses et contradictoires ?"
        - "Qu'est-ce qui vous motive le plus dans un poste comme celui-ci ?"

        Format de réponse requis :
        Renvoie uniquement un tableau JSON contenant des chaînes de caractères, sous cette forme exacte :
        [
          "Question 1...",
          "Question 2...",
          "Question 3...",
          "Question 4...",
          "Question 5..."
        ]
        Ne mets aucune introduction, aucune explication, ni de balises de code Markdown. Renvoie juste le JSON brut.
        """

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            # Nettoyage et chargement du JSON
            content = response.text.strip()
            # Nettoie d'éventuelles balises markdown résiduelles si le LLM n'a pas obéi à 100%
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            questions = json.loads(content.strip())
            if isinstance(questions, list) and len(questions) > 0:
                return [str(q) for q in questions[:count]]
        except Exception as e:
            logger.error(f"Erreur lors de la génération de questions par Gemini : {e}. Utilisation du fallback.")
            
        return self._generate_mock_questions(job_title, count)

    def evaluate_interview(self, job_title: str, qa_list: list[dict]) -> dict:
        """
        Analyse les réponses fournies par le candidat et génère un rapport d'évaluation complet.
        Chaque élément de qa_list contient : {"question_index": int, "question": str, "answer": str}
        """
        if self.is_mock:
            return self._evaluate_mock_interview(job_title, qa_list)

        # Formater l'échange pour l'IA
        exchange_str = ""
        for item in qa_list:
            exchange_str += f"Question {item['question_index'] + 1}: {item['question']}\n"
            exchange_str += f"Réponse du candidat: {item['answer']}\n\n"

        prompt = f"""
        Tu es un recruteur expert. Pour le poste de : "{job_title}", identifie les compétences clés attendues et évalue l'entretien ci-dessous.

        Critères d'évaluation :
        - Clarté de la réponse.
        - Pertinence métier.
        - Exemples concrets ou résultats chiffrés.
        - Structure et logique de la réponse (méthode STAR ou équivalent).

        Voici les questions posées et les réponses données par le candidat :
        {exchange_str}

        Pour chaque réponse, explique ce qui fonctionnait bien, ce qui manquait et propose une amélioration concrète.

        Format de réponse requis :
        Renvoie uniquement un objet JSON valide et strict, sans texte additionnel.

        {{
          "overall_score": 75,
          "feedback_summary": "Résumé de 3 à 4 phrases sur la performance globale du candidat.",
          "strengths": "Points forts clés identifiés.",
          "improvements": "Axes d'amélioration principaux.",
          "question_feedbacks": [
            {{
              "question_index": 0,
              "score": 80,
              "feedback": "Commentaire précis sur la réponse, avantages et suggestions."
            }}
          ]
        }}
        """

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            content = response.text.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]

            result = json.loads(content.strip())
            return result
        except Exception as e:
            logger.error(f"Erreur d'évaluation par Gemini : {e}. Utilisation du fallback Démo.")

        return self._evaluate_mock_interview(job_title, qa_list)

    def _generate_mock_questions(self, job_title: str, count: int) -> list[str]:
        """Fallback local pour générer des questions si Gemini n'est pas configuré."""
        logger.info("Génération de questions simulées (Mode Démo).")
        base_questions = [
            f"Pouvez-vous vous présenter et m'expliquer ce qui vous motive particulièrement à postuler pour le poste de {job_title} ?",
            f"Quelles sont, selon vous, les trois compétences techniques les plus cruciales pour réussir en tant que {job_title}, et comment les appliquez-vous ?",
            f"Décrivez une situation professionnelle difficile ou conflictuelle que vous avez rencontrée dans un rôle similaire à {job_title}, et comment vous l'avez résolue.",
            f"Comment organisez-vous votre travail au quotidien pour gérer des priorités multiples et respecter des délais serrés ?",
            f"Où vous voyez-vous professionnellement d'ici 3 à 5 ans, et en quoi ce poste de {job_title} s'inscrit-il dans votre plan de carrière ?"
        ]
        # Ajustement du nombre de questions demandées
        if count <= len(base_questions):
            return base_questions[:count]
        else:
            # Remplissage si on demande plus de questions
            extra_questions = [
                f"Quelle est votre approche face à un changement soudain de cahier des charges ou de directives de la direction ?",
                f"Quels sont vos points forts majeurs et, à l'inverse, un axe d'amélioration sur lequel vous travaillez actuellement ?"
            ]
            return (base_questions + extra_questions)[:count]

    def _evaluate_mock_interview(self, job_title: str, qa_list: list[dict]) -> dict:
        """Fallback local pour l'évaluation en mode Démo."""
        logger.info("Évaluation simulée (Mode Démo).")
        
        # Calcul d'un score fictif basé sur la longueur des réponses pour donner un effet interactif
        question_feedbacks = []
        total_score = 0
        
        for item in qa_list:
            ans_len = len(item['answer']) if item['answer'] else 0
            if ans_len == 0:
                score = 10
                fb = "Vous n'avez pas répondu à cette question. Il est capital de toujours formuler une réponse, même partielle, pour montrer votre réflexion."
            elif ans_len < 30:
                score = 45
                fb = "Votre réponse est très courte. Essayez de structurer votre discours en utilisant la méthode STAR (Situation, Tâche, Action, Résultat) pour donner du contexte et illustrer vos propos par des exemples concrets."
            elif ans_len < 150:
                score = 75
                fb = "Bonne réponse, claire et concise. Vous auriez pu approfondir l'impact de vos actions ou illustrer vos propos par un indicateur chiffré pour rendre votre argumentation encore plus percutante."
            else:
                score = 88
                fb = "Excellente réponse, détaillée et bien structurée ! Vous démontrez une bonne compréhension des enjeux. Pensez simplement à rester synthétique pour maintenir l'attention de votre interlocuteur lors d'un entretien réel."
            
            question_feedbacks.append({
                "question_index": item['question_index'],
                "score": score,
                "feedback": fb
            })
            total_score += score

        overall_score = int(total_score / len(qa_list)) if qa_list else 50

        return {
            "overall_score": overall_score,
            "is_demo_mode": True,  # Flag pour notifier l'utilisateur de configurer sa clé dans le frontend
            "feedback_summary": f"Félicitations pour avoir complété cette simulation d'entretien pour le poste de {job_title} ! Vos réponses démontrent de l'intérêt et du sérieux. L'exercice est très formateur et vous aidera à coup sûr à structurer vos idées pour le jour J.",
            "strengths": "* Motivation claire et explicite\n* Structure globale des réponses cohérente\n* Volonté d'apporter des exemples",
            "improvements": "* Pensez à utiliser des chiffres et des indicateurs de succès (ex: '+15% de productivité', 'équipe de 5 personnes')\n* Utilisez la méthode STAR pour vos mises en situation comportementales\n* Soyez vigilant sur la concision de vos réponses les plus longues.",
            "question_feedbacks": question_feedbacks
        }

ai_service = AIService()
