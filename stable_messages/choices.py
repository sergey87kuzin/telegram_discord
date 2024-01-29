class StableMessageTypeChoices:
    FIRST = "first"
    U = "u"
    UPSCALED = "upscaled"
    ZOOM = "zoom_out"
    VARY = "vary"
    DOUBLE = "double"

    CHOICES = (
        (FIRST, "Первоначальная генерация"),
        (U, "Одно из 4 U-сообщений"),
        (UPSCALED, "Увеличенное изображение"),
        (ZOOM, "Отдалена"),
        (VARY, "Изменена"),
        (DOUBLE, "Двойная отправка")
    )


class StableModels:
    JUGGERNAUT = "juggernaut-xl"
    DELIBERATE = "deliberate-v3"
    SDXL = "sdxl"

    CHOICES = (
        (JUGGERNAUT, "Джаггернаут"),
        (DELIBERATE, "Делиберейт"),
        (SDXL, "sdxl")
    )


SCALES = {
        "3:2": ("1024", "672"),
        "2:3": ("672", "1024"),
        "3:1": ("1024", "352"),
        "16:9": ("1024", "576"),
        "9:16": ("576", "1024")
    }

ZOOM_SCALES = {
    "3:2": {64, 42},
    "2:3": {42, 64},
    "3:1": {64, 22},
    "16:9": {64, 36},
    "9:16": {36, 64}
}
