import json
import random
import string
from pathlib import Path
from collections import defaultdict, Counter

Path("data").mkdir(exist_ok=True)

# Конфигурация ошибок по функциям
FUNCTION_ERROR_MAP = {
    "is_correct": ["TypeCheckError"],
    "answer_in_context": ["BeartypeCallHintParamViolation"],
    "shortest_alias": ["TypeCheckError", "BeartypeCallHintParamViolation"],
    "validate_consistency": ["ViolationError"],
    "score_candidate": ["Exception"],
    "normalize_question": ["BeartypeCallHintReturnViolation"],
}

ALL_ERROR_TYPES = sorted({e for v in FUNCTION_ERROR_MAP.values() for e in v})

# Генераторы данных
def random_word(min_len=3, max_len=6):
    """ Гарантированно возвращает строку """
    return "".join(random.choice(string.ascii_lowercase) for _ in range(random.randint(min_len, max_len)))

def random_string(n=40):
    chars = string.ascii_letters + string.digits + " !@#$%^&*()"
    return "".join(random.choice(chars) for _ in range(n))

# Генерация вопроса с гарантированной ошибкой
def generate_item(item_id: int):
    # Базовый вопрос
    answer = random_word()
    aliases = [random_word() for _ in range(random.randint(1, 3))]
    question = f"This is a sample question mentioning {answer}."
    error_flags = defaultdict(list)

    # Выбираем функцию и ошибку
    func, err = random.choice([(f, e) for f, es in FUNCTION_ERROR_MAP.items() for e in es])
    error_flags[func].append(err)

    # Инъекции ошибок
    if func == "is_correct" and err == "TypeCheckError":
        answer = 123    # ломает TypeCheck внутри функции
        aliases = ["abc"]

    elif func == "answer_in_context" and err == "BeartypeCallHintParamViolation":
        question = 123  # не str -> ошибка beartype

    elif func == "shortest_alias":
        if err == "TypeCheckError":
            aliases = None  # ломает check_type
        elif err == "BeartypeCallHintParamViolation":
            aliases = 123   # ломает аннотацию beartype

    elif func == "validate_consistency" and err == "ViolationError":
        # пропускаем ключ aliases -> icontract ViolationError
        aliases = None

    elif func == "score_candidate" and err == "Exception":
        answer = None   # вызовет runtime Exception внутри функции

    elif func == "normalize_question" and err == "BeartypeCallHintReturnViolation":
        question = "RETURN_VIOLATION::" + random_string(40)

    final_item = {
        "id": item_id,
        "answer": answer,
        "aliases": aliases,
        "question": question,
        "_error_flags": dict(error_flags),
    }

    return final_item

# Генерируем 3000 ошибочных примеров
N = 3000
data = [generate_item(i) for i in range(N)]

with open("data/incorrect.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Контроль внесенных ошибок
counter = Counter()
for item in data:
    for errs in item["_error_flags"].values():
        for e in errs:
            counter[e] += 1

print(f"{N} записей сохранены в data/incorrect.json")
print("Внесено ошибкок:")
for k, v in counter.items():
    print(f"{k}: {v}")
