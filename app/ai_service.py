import re
from collections import Counter


def summarise_notes(text, sentence_count=5):
    # Split the document into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    if len(sentences) <= sentence_count:
        return text

    # Extract individual words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    # Common words that don't tell us much about the topic
    stop_words = {
        "the", "and", "that", "this", "with", "from",
        "for", "are", "was", "were", "have", "has",
        "had", "but", "not", "you", "your", "they",
        "their", "into", "about", "which", "when",
        "where", "what", "who", "how"
    }

    important_words = [
        word for word in words
        if word not in stop_words
    ]

    word_frequencies = Counter(important_words)

    # Give each sentence a score based on important words
    sentence_scores = {}

    for index, sentence in enumerate(sentences):
        sentence_words = re.findall(
            r'\b[a-zA-Z]{3,}\b',
            sentence.lower()
        )

        score = sum(
            word_frequencies[word]
            for word in sentence_words
        )

        sentence_scores[index] = score

    # Find the highest-scoring sentences
    best_sentences = sorted(
        sentence_scores,
        key=sentence_scores.get,
        reverse=True
    )[:sentence_count]

    # Put them back into their original document order
    best_sentences.sort()

    summary = "\n\n".join(
        sentences[index]
        for index in best_sentences
    )

    return summary