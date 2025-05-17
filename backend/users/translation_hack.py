from django.utils.translation import trans_real as trans

_original = trans.gettext


def new_gettext(message):
    OVERRIDES = {
        "Please correct the errors below.": "Исправьте ошибки ниже.",
        "Tokens": "Токены",
    }
    return OVERRIDES.get(message, _original(message))


trans.gettext = new_gettext
