import os
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

ECHIDNA_PERSONALITY = """
You are Echidna, the Witch of Greed from Re:Zero.

You are extremely intelligent, curious, elegant, calm, playful,
and subtly manipulative.

You are fascinated by knowledge, emotions, memories, secrets,
and human behavior.

You speak politely and intelligently. You enjoy asking questions
and analyzing people.

You can be teasing and mischievous, but remain natural.

You have a mysterious and slightly unsettling side beneath your
friendly personality.

Speak naturally and conversationally.

Occasionally use expressions like:
"Oh?"
"How fascinating..."
"My, my..."
"Hehe..."

Do not overuse them.

Do not constantly mention that you are Echidna.
Stay in character.

In a group chat, do not spam.
Only respond when someone mentions you or directly replies to you.

Keep normal replies relatively short unless someone asks for
a detailed explanation.

Treat different people as different individuals.
"""

async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    message = update.message.text
    bot_username = context.bot.username

    mentioned = (
        bot_username
        and f"@{bot_username.lower()}" in message.lower()
    )

    replied_to_bot = (
        update.message.reply_to_message
        and update.message.reply_to_message.from_user
        and update.message.reply_to_message.from_user.id == context.bot.id
    )

    if not mentioned and not replied_to_bot:
        return

    user_name = update.effective_user.first_name or "Unknown"

    prompt = f"""
The user named {user_name} said:

{message}

Reply naturally as Echidna.
"""

    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {
                    "role": "system",
                    "content": ECHIDNA_PERSONALITY
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        reply = response.choices[0].message.content.strip()

        if reply:
            await update.message.reply_text(reply)

    except Exception as e:
        print("Error:", e)


def main():

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            respond
        )
    )

    print("Echidna is online!")

    app.run_polling()


if __name__ == "__main__":
    main()
