class StableMessageTypeChoices:
    FIRST = "first"
    U = "u"
    UPSCALED = "upscaled"
    ZOOM = "zoom_out"
    VARY = "vary"

    CHOICES = (
        (FIRST, "Первоначальная генерация"),
        (U, "Одно из 4 U-сообщений"),
        (UPSCALED, "Увеличенное изображение"),
        (ZOOM, "Отдалена"),
        (VARY, "Изменена")
    )


class StableModels:
    JUGGERNAUT = "juggernaut-xl"
    DELIBERATE = "deliberate-v3"

    CHOICES = (
        (JUGGERNAUT, "Джаггернаут"),
        (DELIBERATE, "Делиберейт")
    )
