from app.summariser import summarise_notes


def test_short_text_is_unchanged():
    text = (
        "Python is a programming language. "
        "Flask is a web framework."
    )

    result = summarise_notes(text, sentence_count=5)

    assert result == text


def test_summary_reduces_long_text():
    text = (
        "Python is widely used for software development. "
        "Python is commonly used for web applications. "
        "Flask is a Python web framework. "
        "Databases store application data. "
        "Python can communicate with databases. "
        "HTML provides the structure of web pages. "
        "CSS controls the appearance of web pages."
    )

    result = summarise_notes(text, sentence_count=3)

    summary_sentences = [
        sentence
        for sentence in result.split("\n\n")
        if sentence.strip()
    ]

    assert len(summary_sentences) == 3