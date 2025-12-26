import json
import time
import csv
import icontract
from datetime import datetime
from pathlib import Path

from typeguard import TypeCheckError
from beartype.roar import (
    BeartypeCallHintParamViolation,
    BeartypeCallHintReturnViolation,
)

from functions import (
    is_correct,
    answer_in_context,
    shortest_alias,
    validate_consistency,
    score_candidate,
    normalize_question,
)

# Настройки
DATASET_NAME = "normal"  # или "incorrect"
DATA_PATH = Path(f"data/{DATASET_NAME}.json")
OUT_DIR = Path("experiments")
CSV_PATH = OUT_DIR / f"experiments_{DATASET_NAME}.csv"

OUT_DIR.mkdir(exist_ok=True)

functions = [
    is_correct,
    answer_in_context,
    shortest_alias,
    validate_consistency,
    score_candidate,
    normalize_question,
]

libraries = ["typeguard", "icontract", "beartype"]

# Метаданные одного запуска
run_id = int(time.time())
timestamp = datetime.now().isoformat(timespec="seconds")

with DATA_PATH.open(encoding="utf-8") as f:
    data = json.load(f)

# Структура результатов
stats = {
    lib: {
        f.__name__: {
            "passed": 0,
            "failed": 0,
            "time": 0.0,
        }
        for f in functions
    }
    for lib in libraries
}

# Запуск эксперимента
for f in functions:
    for lib in libraries:
        start = time.perf_counter()

        for item in data:
            try:
                if f.__name__ == "is_correct":
                    f(item.get("answer", ""), item)
                elif f.__name__ == "answer_in_context":
                    f(item.get("answer", ""), item.get("question", ""))
                elif f.__name__ == "shortest_alias":
                    f(item.get("aliases", []))
                elif f.__name__ == "validate_consistency":
                    f(item)
                elif f.__name__ == "score_candidate":
                    f(item.get("answer", ""), item)
                elif f.__name__ == "normalize_question":
                    f(item.get("question", ""))

                stats[lib][f.__name__]["passed"] += 1

            except TypeCheckError:
                if lib == "typeguard":
                    stats[lib][f.__name__]["failed"] += 1
                else:
                    stats[lib][f.__name__]["passed"] += 1

            except (BeartypeCallHintParamViolation, BeartypeCallHintReturnViolation):
                if lib == "beartype":
                    stats[lib][f.__name__]["failed"] += 1
                else:
                    stats[lib][f.__name__]["passed"] += 1

            except icontract.ViolationError:
                if lib == "icontract":
                    stats[lib][f.__name__]["failed"] += 1
                else:
                    stats[lib][f.__name__]["passed"] += 1

            except Exception:
                stats[lib][f.__name__]["failed"] += 1

        elapsed = time.perf_counter() - start
        stats[lib][f.__name__]["time"] = elapsed

# Запись в CSV-файл
file_exists = CSV_PATH.exists()

with CSV_PATH.open("a", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)

    if not file_exists:
        writer.writerow([
            "run_id",
            "timestamp",
            "dataset",
            "library",
            "function",
            "passed",
            "failed",
            "time_sec",
        ])

    for lib in libraries:
        for f in functions:
            row = stats[lib][f.__name__]
            writer.writerow([
                run_id,
                timestamp,
                DATASET_NAME,
                lib,
                f.__name__,
                row["passed"],
                row["failed"],
                round(row["time"], 6),
            ])

print(f"Эксперимент завершен. Данные добавлены в {CSV_PATH}")
