import os

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from google import genai


# =============================
# CONFIGURATION
# =============================

TOKEN = os.getenv("BOT_TOKEN")

gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

mode_note = False


# =============================
# GEMINI
# =============================

async def ask_gemini(question):

    try:

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
Tu es Kyrios Assistant.

Tu es l'assistant personnel de Junior.

Tu aides dans :

- Python
- IA
- Développement personnel
- Productivité
- Organisation
- Revenus en ligne
- Motivation
- Apprentissage

Réponds en français.

Question :

{question}
"""
        )

        return response.text

    except Exception as e:

        return f"❌ Erreur Gemini : {e}"


# =============================
# START
# =============================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        ["👤 Junior"],
        ["⚽ Analyse Match", "💰 Revenus"],
        ["📊 Bankroll", "🎯 Objectifs"],
        ["🧠 Défi Social", "📚 Apprendre"],
        ["📝 Notes", "📖 Mes Notes"],
        ["📈 Bilan", "⚙️ Paramètres"],
        ["🗑️ Effacer Notes", "ℹ️ Aide"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        """
🤖 KYRIOS ASSISTANT V2

Salut Junior !

Je suis ton assistant personnel intelligent.

✅ Analyse sportive
✅ Gestion bankroll
✅ Revenus
✅ Développement personnel
✅ Python
✅ Intelligence artificielle
✅ Notes personnelles

Choisis une option :
""",
        reply_markup=reply_markup
    )


# =============================
# MESSAGES
# =============================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    global mode_note

    text = update.message.text

    # =========================
    # PROFIL
    # =========================

    if text == "👤 Junior":

        await update.message.reply_text(
            """
👤 PROFIL JUNIOR

🏠 Ville : Abidjan

🤖 Assistant :
Kyrios V2

🎯 Objectifs :

✅ Développement personnel
✅ Paris sportifs
✅ Revenus en ligne
✅ Python
✅ IA
"""
        )

    # =========================
    # MATCH
    # =========================

    elif text == "⚽ Analyse Match":

        await update.message.reply_text(
            """
⚽ Analyse Match

Envoie le match.

Exemple :

ASEC vs Africa Sports
"""
        )

    # =========================
    # REVENUS
    # =========================

    elif text == "💰 Revenus":

        await update.message.reply_text(
            """
💰 Revenus

✅ Freelance
✅ Affiliation
✅ TikTok
✅ Services IA
✅ Vente de services locaux
"""
        )

    # =========================
    # BANKROLL
    # =========================

    elif text == "📊 Bankroll":

        await update.message.reply_text(
            """
📊 Gestion Bankroll

✅ Ajouter dépôt

✅ Ajouter pari

✅ Statistiques

(Fonction avancée bientôt)
"""
        )

    # =========================
    # OBJECTIFS
    # =========================

    elif text == "🎯 Objectifs":

        await update.message.reply_text(
            """
🎯 Objectifs du jour

✅ Python 30 min

✅ Lire 10 pages

✅ Parler à une nouvelle personne
"""
        )

    # =========================
    # DEFI SOCIAL
    # =========================

    elif text == "🧠 Défi Social":

        await update.message.reply_text(
            """
🧠 Défi du jour

Parle à une nouvelle personne.

Objectifs :

✅ Dire bonjour

✅ Poser une question

✅ Écouter attentivement
"""
        )

    # =========================
    # APPRENDRE
    # =========================

    elif text == "📚 Apprendre":

        await update.message.reply_text(
            """
📚 Sujets disponibles

🐍 Python

🤖 IA

⚽ Paris sportifs

💰 Revenus
"""
        )

    # =========================
    # NOTES
    # =========================

    elif text == "📝 Notes":

        mode_note = True

        await update.message.reply_text(
            "📝 Écris ta note."
        )

    # =========================
    # MES NOTES
    # =========================

    elif text == "📖 Mes Notes":

        try:

            with open(
                "notes.txt",
                "r",
                encoding="utf-8"
            ) as f:

                notes = f.read()

            if notes.strip() == "":
                raise Exception()

            await update.message.reply_text(
                f"📖 TES NOTES\n\n{notes}"
            )

        except:

            await update.message.reply_text(
                "📭 Aucune note enregistrée."
            )

    # =========================
    # EFFACER NOTES
    # =========================

    elif text == "🗑️ Effacer Notes":

        open(
            "notes.txt",
            "w",
            encoding="utf-8"
        ).close()

        await update.message.reply_text(
            "✅ Notes supprimées."
        )

    # =========================
    # BILAN
    # =========================

    elif text == "📈 Bilan":

        await update.message.reply_text(
            """
📈 BILAN

✅ Bot actif

✅ Notes disponibles

✅ Assistant opérationnel

✅ Gemini intégré
"""
        )

    # =========================
    # PARAMETRES
    # =========================

    elif text == "⚙️ Paramètres":

        await update.message.reply_text(
            """
⚙️ PARAMÈTRES

Version : V2

Statut : En ligne
"""
        )

    # =========================
    # AIDE
    # =========================

    elif text == "ℹ️ Aide":

        await update.message.reply_text(
            """
ℹ️ AIDE

/start
Menu principal

Utilise les boutons ci-dessous.
"""
        )

    # =========================
    # SALUTATIONS
    # =========================

    elif text.lower() in [
        "salut",
        "bonjour",
        "hello"
    ]:

        await update.message.reply_text(
            """
👋 Salut Junior !

Heureux de te revoir.
"""
        )

    # =========================
    # ENREGISTRER NOTE
    # =========================

    elif mode_note:

        with open(
            "notes.txt",
            "a",
            encoding="utf-8"
        ) as f:

            f.write(text + "\n")

        mode_note = False

        await update.message.reply_text(
            f"✅ Note enregistrée :\n\n{text}"
        )

    # =========================
    # GEMINI
    # =========================

    else:

        await update.message.reply_text(
            "🤖 Réflexion..."
        )

        reponse = await ask_gemini(text)

        if len(reponse) > 4000:
            reponse = reponse[:4000]

        await update.message.reply_text(
            reponse
        )


# =============================
# MAIN
# =============================

print("🚀 KYRIOS ASSISTANT V2 LANCÉ")

app = Application.builder().token(TOKEN).build()

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

app.run_polling()
