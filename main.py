"""
Kyrios AI Telegram Bot
Python 3.10+
Features: AI chat, /ask, /reset, /help, /whoami, /start, conversational memory per chat.
"""

import os
import logging
from collections import defaultdict, deque

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from google import genai

# =========================
# CONFIGURATION
# =========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

MODEL = "gemini-2.5-flash"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("kyrios_bot")

if not TELEGRAM_TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN environment variable.")

if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY environment variable.")

client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# MÉMOIRE
# =========================

CHAT_HISTORY = defaultdict(lambda: deque(maxlen=16))

# =========================
# PROMPT SYSTÈME
# =========================

SYSTEM_PROMPT = """
Tu es Kyrios, un assistant IA utile, clair et respectueux.

Réponds en français par défaut, mais utilise la langue demandée.

Aide à :
- rédiger
- expliquer
- traduire
- résumer
- programmer
- organiser
- calculer

Sois honnête.
N'invente jamais les faits.
Ne prétends pas avoir effectué une action que tu n'as pas réalisée.
"""

# =========================
# CLAVIER
# =========================

KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🤖 Parler à l'IA", "🧠 Aide"],
        ["✍️ Rédiger", "🌍 Traduire"],
        ["📊 Calculer", "🔄 Réinitialiser"],
    ],
    resize_keyboard=True,
)

# =========================
# OUTILS
# =========================

def get_chat_key(update: Update) -> int:
    return update.effective_chat.id

# =========================
# COMMANDES
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "✅ Kyrios AI est lancé !\n\n"
        "Écris simplement ta question ou utilise /ask.\n"
        "Commandes : /help, /ask, /reset, /whoami",
        reply_markup=KEYBOARD,
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "📘 Commandes Kyrios AI\n"
        "/start — démarrer le bot\n"
        "/help — afficher l'aide\n"
        "/ask ta question — poser une question à l'IA\n"
        "/reset — effacer la mémoire récente\n"
        "/whoami — afficher ton identifiant Telegram\n\n"
        "Tu peux aussi envoyer directement un message normal.",
        reply_markup=KEYBOARD,
    )

async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.effective_message.reply_text(
        f"Ton identifiant Telegram est : {user.id}"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_HISTORY.pop(get_chat_key(update), None)

    await update.effective_message.reply_text(
        "🧹 Mémoire récente réinitialisée."
    )

# =========================
# GEMINI
# =========================

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):

    prompt = (prompt or "").strip()

    if not prompt:
        await update.effective_message.reply_text(
            "Écris ta question après /ask ou envoie un message."
        )
        return

    msg = await update.effective_message.reply_text(
        "⏳ Kyrios réfléchit..."
    )

    key = get_chat_key(update)

    history = list(CHAT_HISTORY[key])

    try:

        history_text = ""

        for item in history:
            history_text += f"{item['role']} : {item['content']}\n"

        full_prompt = f"""
{SYSTEM_PROMPT}

Historique :

{history_text}

Question :

{prompt}
"""

        response = client.models.generate_content(
            model=MODEL,
            contents=full_prompt
        )

        answer = response.text.strip()

        if not answer:
            answer = (
                "Je n'ai pas pu produire de réponse. "
                "Essaie de reformuler."
            )

        CHAT_HISTORY[key].append(
            {
                "role": "user",
                "content": prompt
            }
        )

        CHAT_HISTORY[key].append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        try:
            await msg.delete()
        except Exception:
            pass

        for i in range(0, len(answer), 3900):
            await update.effective_message.reply_text(
                answer[i:i + 3900]
            )

    except Exception as exc:

        logger.exception("Gemini request failed")

        try:
            await msg.edit_text(
                "⚠️ Une erreur est survenue avec Gemini.\n"
                "Vérifie la clé API Gemini ou réessaie plus tard."
            )
        except Exception:
            pass

# =========================
# /ASK
# =========================

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args).strip()

    await ask_ai(update, context, prompt)

# =========================
# MESSAGES
# =========================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (update.effective_message.text or "").strip()

    if text == "🧠 Aide":
        await help_command(update, context)
        return

    if text == "🔄 Réinitialiser":
        await reset(update, context)
        return

    if text == "✍️ Rédiger":
        await update.effective_message.reply_text(
            "Dis-moi quel texte tu veux rédiger."
        )
        return

    if text == "🌍 Traduire":
        await update.effective_message.reply_text(
            "Envoie le texte et indique la langue cible."
        )
        return

    if text == "📊 Calculer":
        await update.effective_message.reply_text(
            "Envoie ton calcul."
        )
        return

    if text == "🤖 Parler à l'IA":
        await update.effective_message.reply_text(
            "Je t'écoute 👌"
        )
        return

    await ask_ai(update, context, text)

# =========================
# ERREURS
# =========================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception(
        "Unhandled bot error",
        exc_info=context.error
    )

# =========================
# MAIN
# =========================

def main():

    app = Application.builder().token(
        TELEGRAM_TOKEN
    ).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("whoami", whoami))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    app.add_error_handler(error_handler)

    logger.info("🚀 Kyrios AI démarre...")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()


    

   
