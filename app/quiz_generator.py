import re
from collections import Counter


def generate_quiz(text, question_count=5):
    sentences = re.split(r'(?<=[.!?])\s+', text)

    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

    stop_words = {
        "that", "this", "with", "from", "have",
        "were", "they", "their", "there", "which",
        "when", "where", "what", "your", "about"
    }

    important_words = [
        word for word in words
        if word not in stop_words
    ]

    frequencies = Counter(important_words)

    questions = []

    for sentence in sentences:
        sentence_words = re.findall(
            r'\b[a-zA-Z]{4,}\b',
            sentence.lower()
        )

        if not sentence_words:
            continue

        important_word = max(
            sentence_words,
            key=lambda word: frequencies[word]
        )

        if frequencies[important_word] < 2:
            continue

        question_text = re.sub(
            rf'\b{re.escape(important_word)}\b',
            "________",
            sentence,
            count=1,
            flags=re.IGNORECASE
        )

        questions.append({
            "question": question_text,
            "answer": important_word
        })

        if len(questions) == question_count:
            break

    return questions