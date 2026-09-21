from app.quiz_generator import generate_quiz


def test_quiz_respects_question_limit():
    text = (
        "Python is used for software development. "
        "Python is used for web development. "
        "Python is used for automation. "
        "Python is popular with developers. "
        "Python has many useful libraries. "
        "Python can be used with Flask."
    )

    questions = generate_quiz(text, question_count=3)

    assert len(questions) <= 3


def test_questions_contain_blank():
    text = (
        "Database systems store information. "
        "Database systems organise information. "
        "Database systems retrieve information."
    )

    questions = generate_quiz(text)

    assert len(questions) > 0

    for question in questions:
        assert "________" in question["question"]


def test_question_contains_answer():
    text = (
        "Flask is a Python framework. "
        "Flask is used for web development. "
        "Flask can create web applications."
    )

    questions = generate_quiz(text)

    assert len(questions) > 0

    for question in questions:
        assert question["answer"]