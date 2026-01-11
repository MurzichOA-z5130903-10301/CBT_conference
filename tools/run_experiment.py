import json
import time
import csv
from datetime import datetime
from pathlib import Path

import icontract
from typeguard import TypeCheckError
from beartype.roar import (
    BeartypeCallHintParamViolation,
    BeartypeCallHintReturnViolation,
)

from functions import *


DATASETS = ["normal", "incorrect"]

BASE_DATA_DIR = Path("data")
OUT_DIR = Path("experiments")
OUT_DIR.mkdir(exist_ok=True)

run_id = int(time.time())
timestamp = datetime.now().isoformat(timespec="seconds")


FUNCTION_MAP = {
    "beartype": {
        "is_correct": is_correct_beartype,
        "answer_in_context": answer_in_context_beartype,
        "shortest_alias": shortest_alias_beartype,
        "validate_consistency": validate_consistency_beartype,
        "score_candidate": score_candidate_beartype,
        "normalize_question": normalize_question_beartype,
    },
    "typeguard": {
        "is_correct": is_correct_typeguard,
        "answer_in_context": answer_in_context_typeguard,
        "shortest_alias": shortest_alias_typeguard,
        "validate_consistency": validate_consistency_typeguard,
        "score_candidate": score_candidate_typeguard,
        "normalize_question": normalize_question_typeguard,
    },
    "icontract": {
        "is_correct": is_correct_icontract,
        "answer_in_context": answer_in_context_icontract,
        "shortest_alias": shortest_alias_icontract,
        "validate_consistency": validate_consistency_icontract,
        "score_candidate": score_candidate_icontract,
        "normalize_question": normalize_question_icontract,
    },
}


def call_function(func_name, func, item):
    if func_name == "is_correct":
        return func(item.get("answer"), item)
    if func_name == "answer_in_context":
        return func(item.get("answer"), item.get("question"))
    if func_name == "shortest_alias":
        return func(item.get("aliases"))
    if func_name == "validate_consistency":
        return func(item)
    if func_name == "score_candidate":
        return func(item.get("answer"), item)
    if func_name == "normalize_question":
        return func(item.get("question"))
    raise RuntimeError(func_name)


LIB_EXCEPTIONS = {
    "beartype": (
        BeartypeCallHintParamViolation,
        BeartypeCallHintReturnViolation,
    ),
    "typeguard": (TypeCheckError,),
    "icontract": (icontract.ViolationError,),
}


for dataset_name in DATASETS:
    data_path = BASE_DATA_DIR / f"{dataset_name}.json"
    csv_path = OUT_DIR / f"experiments_{dataset_name}_all.csv"

    with data_path.open(encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    for library_name, functions in FUNCTION_MAP.items():
        for func_name, func in functions.items():
            for idx, item in enumerate(data):
                item_id = item["id"] if dataset_name == "incorrect" else idx

                if dataset_name == "incorrect":
                    injected = item.get("_error_flags", {}).get(func_name, [])
                    injected_error = injected[0] if injected else "None"
                else:
                    injected_error = "None"

                is_injection_point = injected_error != "None"

                start = time.perf_counter()
                detected_error = "None"
                correctly_detected = False

                try:
                    call_function(func_name, func, item)

                except LIB_EXCEPTIONS[library_name] as e:
                    detected_error = type(e).__name__
                    correctly_detected = detected_error == injected_error

                except Exception:
                    detected_error = "Exception"

                elapsed = time.perf_counter() - start

                rows.append(
                    [
                        run_id,
                        timestamp,
                        dataset_name,
                        item_id,
                        func_name,
                        library_name,
                        injected_error,
                        detected_error,
                        correctly_detected,
                        is_injection_point,
                        round(elapsed, 6),
                    ]
                )

    file_exists = csv_path.exists()

    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(
                [
                    "run_id",
                    "timestamp",
                    "dataset",
                    "item_id",
                    "function",
                    "library",
                    "injected_error",
                    "detected_error",
                    "correctly_detected",
                    "is_injection_point",
                    "time_sec",
                ]
            )

        writer.writerows(rows)

print("Эксперимент завершен.")
