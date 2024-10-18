from discord_messages.telegram_helper import bot
from users.models import User


def add_generations(chat_id: str, generations_to_add: int) -> None:
    user = User.objects.filter(chat_id=chat_id).first()
    if not user:
        return
    user.remain_messages += generations_to_add
    bot.send_message(
        chat_id,
        text=f"<pre>Вам добавлено {generations_to_add} генераций по реферальной программе </pre>",
        parse_mode="HTML"
    )
    user.save(update_fields=["remain_messages"])
