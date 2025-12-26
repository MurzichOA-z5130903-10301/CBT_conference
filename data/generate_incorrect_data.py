import json
import random
import string
from pathlib import Path

Path("data").mkdir(exist_ok=True)

# Алфавит для "мусорных" строк (включая управляющие и не-ASCII символы)
GARBAGE_CHARS = string.ascii_letters + string.digits + " !@#$%^&*()_+-=,./<>?;:[]{}|\n\t\r±§™©€æøåабвгд"

def random_string(min_len=1, max_len=50, allow_spaces=True):
    length = random.randint(min_len, max_len)
    chars = GARBAGE_CHARS
    if not allow_spaces:
        chars = chars.replace(" ", "")
    return "".join(random.choice(chars) for _ in range(length))

def random_word(min_len=1, max_len=10):
    chars = string.ascii_lowercase
    return "".join(random.choice(chars) for _ in range(random.randint(min_len, max_len)))

def homoglyph_mix(s: str):
    subs = {"a":"@", "o":"0", "e":"3", "l":"1", "s":"$", "i":"¡"}
    return "".join(subs.get(ch, ch) for ch in s)

def make_no_vowels(s: str):
    return "".join(ch for ch in s if ch.lower() not in "aeiou")

def generate_item():
    error_types = random.sample(["answer_in_context", "normalize_question", "score_candidate", "validate_consistency"],
                                k=random.randint(1, 3))

    # Стартовые "нормальные" поля
    answer = random_word(min_len=1, max_len=8)
    aliases = [random_word(min_len=1, max_len=8) for _ in range(random.randint(1, 3))]
    # Иногда делаем aliases корректным (включаем answer)
    if random.random() < 0.4:
        aliases.append(answer)

    # Базовый вопрос - короткий и читаемый
    question = f"This is a sample question mentioning {answer}."

    # Применяем выбранные ошибки
    if "answer_in_context" in error_types:
        mode = random.choice(["remove", "obfuscate", "split"])
        if mode == "remove":
            # question не содержит answer - заменяем на шум
            question = random_string(min_len=30, max_len=120)
        elif mode == "obfuscate":
            # Вставляем answer с шумом между буквами
            noisy = "".join(ch + random.choice(["", "#", "@", "\u200b"]) for ch in answer)
            question = f"This question contains {noisy} somewhere but obfuscated."
        else:
            # Разрываем answer символами, так что последовательность из 3-х символов встречается, но не слово
            split = " ".join(ch for ch in answer)
            question = f"Broken answer: {split} in the text."

    if "normalize_question" in error_types:
        mode = random.choice(["long_nospace", "unicode_noise", "control_chars"])
        if mode == "long_nospace":
            # Очень длинный токен без пробелов - нормализатор должен обрезать/сломаться
            token = random_string(min_len=200, max_len=800, allow_spaces=False)
            question = token
        elif mode == "unicode_noise":
            # Добавляем много не-ASCII символов и глифов
            token = random_string(min_len=150, max_len=400)
            # Перемешиваем символы
            question = "".join(random.sample(token, len(token)))
        else:
            # Вставляем управляющие символы
            q = random_string(min_len=80, max_len=200)
            q = q.replace(" ", "\n\t")
            question = q

    if "score_candidate" in error_types:
        mode = random.choice(["no_match", "homoglyphs", "short_candidate"])
        if mode == "no_match":
            # answer не похож на aliases: делаем answer случайной строкой с символами
            answer = random_string(min_len=8, max_len=12, allow_spaces=False)
            aliases = [random_string(min_len=5, max_len=12, allow_spaces=False) for _ in range(random.randint(1,3))]
        elif mode == "homoglyphs":
            if aliases:
                chosen = random.choice(aliases)
                answer = homoglyph_mix(chosen)
            else:
                answer = homoglyph_mix(random_word(3,6))
        else:
            answer = random_word(min_len=1, max_len=1)  # слишком короткий candidate

    if "validate_consistency" in error_types:
        mode = random.choice(["missing_in_aliases", "aliases_no_vowel", "aliases_empty"])
        if mode == "missing_in_aliases":
            # answer не в aliases
            if answer in aliases:
                # Заменяем answer на другой
                answer = answer + random.choice(["x","z","q"])
        elif mode == "aliases_no_vowel":
            # Делаем все aliases без гласных
            aliases = [make_no_vowels(a) or "bcdf" for a in aliases]
        else:
            aliases = []

    # Дополнительно - иногда комбинируем и добавляем еще шум
    if random.random() < 0.15:
        # Добавляем случайные спецсимволы в answer или aliases
        if random.random() < 0.5:
            answer = answer + random.choice("!@#")
        else:
            aliases = [a + random.choice("!@#") for a in aliases]

    # Гарантируем корректные типы и поля в JSON
    if not isinstance(aliases, list):
        aliases = []
    if not isinstance(question, str):
        question = str(question)
    if not isinstance(answer, str):
        answer = str(answer)

    return {"question": question, "answer": answer, "aliases": aliases}

# Генерируем 3000 полностью ошибочных примеров
data = [generate_item() for _ in range(3000)]

with open("data/incorrect.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("3000 ошибочных примеров сохранены в data/incorrect.json")
