from typing import List, Dict
from typing_extensions import Annotated
from typeguard import typechecked
from beartype import beartype
from beartype.vale import Is
import icontract


def is_correct(pred: str, gold: dict) -> bool:
    return pred in gold["aliases"]

def answer_in_context(answer: str, context: str) -> bool:
    return answer in context

def shortest_alias(aliases: List[str]) -> str:
    return min(aliases, key=len)

def validate_consistency(item: Dict) -> bool:
    return item["answer"] not in item["aliases"]

def score_candidate(candidate: str, gold: dict) -> int:
    return len(candidate)

def normalize_question(q: str, max_len: int) -> str:
    return q.strip()[:max_len]


@typechecked
def is_correct_typeguard(pred: str, gold: dict) -> bool:
    return is_correct(pred, gold)

@typechecked
def answer_in_context_typeguard(answer: str, context: str) -> bool:
    return answer_in_context(answer, context)

@typechecked
def shortest_alias_typeguard(aliases: List[str]) -> str:
    return shortest_alias(aliases)

@typechecked
def validate_consistency_typeguard(item: Dict) -> bool:
    return validate_consistency(item)

@typechecked
def score_candidate_typeguard(candidate: str, gold: dict) -> int:
    return score_candidate(candidate, gold)

@typechecked
def normalize_question_typeguard(q: str, max_len: int) -> str:
    return normalize_question(q, max_len)


NonEmptyStrList = Annotated[List[str], Is[lambda xs: len(xs) > 0]]
PositiveInt = Annotated[int, Is[lambda x: x > 0]]

@beartype
def is_correct_beartype(pred: str, gold: dict) -> bool:
    return is_correct(pred, gold)

@beartype
def answer_in_context_beartype(answer: str, context: str) -> bool:
    return answer_in_context(answer, context)

@beartype
def shortest_alias_beartype(aliases: NonEmptyStrList) -> str:
    return shortest_alias(aliases)

@beartype
def validate_consistency_beartype(item: Dict) -> bool:
    return validate_consistency(item)

@beartype
def score_candidate_beartype(candidate: str, gold: dict) -> int:
    return score_candidate(candidate, gold)

@beartype
def normalize_question_beartype(q: str, max_len: PositiveInt) -> str:
    return normalize_question(q, max_len)


@icontract.require(lambda pred: isinstance(pred, str))
@icontract.require(lambda gold: isinstance(gold, dict) and isinstance(gold["aliases"], list))
@icontract.ensure(lambda r: isinstance(r, bool))
def is_correct_icontract(pred: str, gold: dict) -> bool:
    return is_correct(pred, gold)

@icontract.require(lambda a: isinstance(a, str))
@icontract.require(lambda c: isinstance(c, str))
@icontract.ensure(lambda r: isinstance(r, bool))
def answer_in_context_icontract(a: str, c: str) -> bool:
    return answer_in_context(a, c)

@icontract.require(lambda xs: isinstance(xs, list) and len(xs) > 0)
@icontract.ensure(lambda r: isinstance(r, str))
def shortest_alias_icontract(xs: List[str]) -> str:
    return shortest_alias(xs)

@icontract.require(lambda item: isinstance(item, dict))
@icontract.ensure(lambda r: isinstance(r, bool))
def validate_consistency_icontract(item: Dict) -> bool:
    return validate_consistency(item)

@icontract.require(lambda c: isinstance(c, str))
@icontract.ensure(lambda r: isinstance(r, int))
def score_candidate_icontract(c: str, gold: dict) -> int:
    return score_candidate(c, gold)

@icontract.require(lambda q: isinstance(q, str))
@icontract.require(lambda m: isinstance(m, int) and m > 0)
@icontract.ensure(lambda r: isinstance(r, str))
def normalize_question_icontract(q: str, m: int) -> str:
    return normalize_question(q, m)
