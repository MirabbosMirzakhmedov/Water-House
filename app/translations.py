import json

with open('translations.json', 'r', encoding='utf-8') as file:
    translations = json.load(file)

def _(text, lang='ru'):
    if lang == 'ru':
        return text
    else:
        global translations
        try:
            return translations[lang][text]
        except:
            return text