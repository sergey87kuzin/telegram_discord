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


SCALES = {
        "3:2": ("1024", "672"),
        "2:3": ("672", "1024"),
        "3:1": ("1024", "352"),
        "16:9": ("1024", "576"),
        "9:16": ("576", "1024")
    }
