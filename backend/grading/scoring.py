"""
Automatic grading (US-07, task 7.2). Pure functions: no database access, so they are unit
tested on their own (test_scoring.py). services.submit_assignment() reads the answer keys
from the database, calls grade() and saves the result.

Lab 5 class diagram: Question.check(answer) → check_answer(); Submission.grade() → grade().
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from assignments.models import Question


@dataclass(frozen=True)
class AnswerKey:
    """What one question accepts as correct, and what it is worth."""

    question_id: int
    kind: str  # Question.Kind.MULTIPLE_CHOICE or Question.Kind.FILL_IN
    points: int
    correct_choice_id: int | None = None  # multiple choice
    correct_answer: str = ""  # fill-in


@dataclass(frozen=True)
class QuestionResult:
    """How one question of a submission was graded."""

    question_id: int
    is_correct: bool
    points_awarded: int
    points: int


@dataclass(frozen=True)
class GradeResult:
    """A graded submission: the score out of max_score, and each question's result."""

    score: int
    max_score: int
    results: tuple[QuestionResult, ...]


def normalize(text: str) -> str:
    """Fill-in answers ignore case and extra spaces: " Улаан  Баатар " → "улаан баатар"."""
    return " ".join(text.split()).casefold()


def check_answer(key: AnswerKey, answer: int | str | None) -> bool:
    """
    Is the answer correct? (Lab 5: Question.check(answer).) Multiple choice: the chosen
    option's id; fill-in: the typed text. A missing answer, or one of the wrong type, is wrong.
    """
    if key.kind == Question.Kind.MULTIPLE_CHOICE:
        return isinstance(answer, int) and answer == key.correct_choice_id
    if not isinstance(answer, str):
        return False
    given = normalize(answer)
    return given != "" and given == normalize(key.correct_answer)


def grade(keys: Sequence[AnswerKey], answers: Mapping[int, int | str | None]) -> GradeResult:
    """
    Grade a submission (Lab 5: Submission.grade()). `answers` maps a question id to the chosen
    option's id or the typed text; questions without an entry count as unanswered (wrong).
    The score is the sum of the points of the correctly answered questions.
    """
    results = []
    for key in keys:
        is_correct = check_answer(key, answers.get(key.question_id))
        results.append(
            QuestionResult(
                question_id=key.question_id,
                is_correct=is_correct,
                points_awarded=key.points if is_correct else 0,
                points=key.points,
            )
        )
    return GradeResult(
        score=sum(result.points_awarded for result in results),
        max_score=sum(key.points for key in keys),
        results=tuple(results),
    )
