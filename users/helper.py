from users.models import User


def add_generations(chat_id: str, generations_to_add: int) -> None:
    user = User.objects.filter(chat_id=chat_id).first()
    if not user:
        return
    user.remain_generations += generations_to_add
    user.save(update_fields=["remain_messages"])
