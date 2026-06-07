"""Unit tests for the trustworthy core — run with: python -m pytest -q
   or just: python test_tutor.py"""

import questions
import tutor


def test_every_generator_answer_is_a_choice():
    for topic in questions.GENERATORS:
        for tier in (1, 2, 3):
            for _ in range(200):
                q = questions.make_question(topic, tier)
                assert len(q["choices"]) == 4, q
                assert len(set(q["choices"])) == 4, ("dup choices", q)
                assert str(q["answer"]) in q["choices"], ("answer missing", q)


def test_score_to_level_boundaries():
    perfect = {1: (10, 10), 2: (10, 10), 3: (10, 10)}
    assert tutor.score_to_level(perfect) == "Advanced"
    zero = {1: (0, 10), 2: (0, 10), 3: (0, 10)}
    assert tutor.score_to_level(zero) == "Beginner"
    # only easy correct -> beginner-ish
    easy_only = {1: (10, 10), 2: (0, 10), 3: (0, 10)}
    assert tutor.score_to_level(easy_only) in ("Beginner", "Intermediate")


def test_grade_diagnostic_all_correct():
    quiz = tutor.build_diagnostic()
    responses = [q["answer"] for q in quiz]   # answer everything correctly
    level, pct, per_topic, tally = tutor.grade_diagnostic(quiz, responses)
    assert pct == 100
    assert level == "Advanced"
    assert all(v == 100 for v in per_topic.values())


def test_grade_diagnostic_all_wrong():
    quiz = tutor.build_diagnostic()
    responses = []
    for q in quiz:
        wrong = next(c for c in q["choices"] if c != str(q["answer"]))
        responses.append(wrong)
    level, pct, per_topic, tally = tutor.grade_diagnostic(quiz, responses)
    assert pct == 0
    assert level == "Beginner"


def test_homework_is_20_questions_split_evenly():
    for level in tutor.LEVELS:
        hw = tutor.generate_homework(level)
        assert len(hw) == 20, level
        algebra = sum(1 for q in hw if q["topic"] == "Algebra")
        geom = sum(1 for q in hw if q["topic"] == "Coordinate Geometry")
        assert algebra == 10 and geom == 10, (level, algebra, geom)
        # numbering 1..20
        assert [q["n"] for q in hw] == list(range(1, 21))


def test_homework_markdown_and_key_line_up():
    hw = tutor.generate_homework("Intermediate")
    ws, key = tutor.homework_to_markdown("Test Kid", "Intermediate", hw)
    assert ws.count("[Algebra]") == 10
    assert ws.count("[Coordinate Geometry]") == 10
    # answer key has 20 numbered lines
    key_lines = [l for l in key.splitlines() if l and l[0].isdigit()]
    assert len(key_lines) == 20


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\nAll {len(fns)} tests passed.")
