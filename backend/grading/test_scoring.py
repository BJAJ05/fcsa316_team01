"""Unit tests for the automatic grading core (scoring.py, US-07 task 7.2). No database."""

from assignments.models import Question
from grading.scoring import AnswerKey, check_answer, grade, normalize

MC = Question.Kind.MULTIPLE_CHOICE
FILL = Question.Kind.FILL_IN

# Question 1: multiple choice, option 11 is correct, 2 points.
# Question 2: fill-in, "Улаанбаатар", 3 points.
KEYS = [
    AnswerKey(question_id=1, kind=MC, points=2, correct_choice_id=11),
    AnswerKey(question_id=2, kind=FILL, points=3, correct_answer="Улаанбаатар"),
]


def test_all_correct_gives_the_full_score():
    result = grade(KEYS, {1: 11, 2: "Улаанбаатар"})

    assert (result.score, result.max_score) == (5, 5)
    assert [r.is_correct for r in result.results] == [True, True]


def test_mixed_answers_count_only_the_correct_questions_points():
    result = grade(KEYS, {1: 12, 2: "Улаанбаатар"})

    assert (result.score, result.max_score) == (3, 5)
    assert [(r.question_id, r.is_correct, r.points_awarded, r.points) for r in result.results] == [
        (1, False, 0, 2),
        (2, True, 3, 3),
    ]


def test_no_answers_give_zero_and_every_question_is_wrong():
    result = grade(KEYS, {})

    assert (result.score, result.max_score) == (0, 5)
    assert [r.is_correct for r in result.results] == [False, False]


def test_fill_in_ignores_letter_case_and_extra_spaces():
    assert normalize("  Улаан   БААТАР ") == "улаан баатар"
    assert check_answer(KEYS[1], "  улаанБААТАР ")
    assert not check_answer(KEYS[1], "Дархан")


def test_empty_or_missing_answers_are_wrong():
    assert not check_answer(KEYS[1], "")
    assert not check_answer(KEYS[1], "   ")
    assert not check_answer(KEYS[1], None)
    assert not check_answer(KEYS[0], None)


def test_another_questions_option_or_a_wrong_type_is_wrong():
    assert not check_answer(KEYS[0], 99)  # an option of some other question
    assert not check_answer(KEYS[0], "11")  # text for a multiple-choice question
    assert not check_answer(KEYS[1], 11)  # an option id for a fill-in question


def test_answers_to_questions_outside_the_keys_are_ignored():
    result = grade(KEYS, {1: 11, 2: "Улаанбаатар", 3: "extra"})

    assert (result.score, result.max_score) == (5, 5)
    assert [r.question_id for r in result.results] == [1, 2]


def test_an_assignment_without_questions_scores_zero_of_zero():
    result = grade([], {})

    assert (result.score, result.max_score, result.results) == (0, 0, ())
