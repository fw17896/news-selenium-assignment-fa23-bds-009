import re
from collections import Counter

# A lightweight extractive summarizer: no paid API key or external model is needed.
STOP_WORDS = set("""
a an the and or but if while with of at by for from in into on onto to up down
is am are was were be been being have has had do does did this that these those
it its as not no nor so than too very can could should would will just about
after before over under again further then once here there when where why how
all any both each few more most other some such only own same also
""".split())


def summarize(text, sentence_count=3):
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return "No article text was available to summarize."

    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if len(s.split()) >= 6]

    if not sentences:
        return text[:700]

    if len(sentences) <= sentence_count:
        return " ".join(sentences)

    words = re.findall(r"\b[a-zA-Z][a-zA-Z'-]{2,}\b", text.lower())
    frequencies = Counter(w for w in words if w not in STOP_WORDS)
    if not frequencies:
        return " ".join(sentences[:sentence_count])

    maximum = max(frequencies.values())
    weights = {word: count / maximum for word, count in frequencies.items()}

    scored = []
    for index, sentence in enumerate(sentences):
        tokens = re.findall(r"\b[a-zA-Z][a-zA-Z'-]{2,}\b", sentence.lower())
        useful = [w for w in tokens if w not in STOP_WORDS]
        score = sum(weights.get(w, 0) for w in useful) / max(len(useful), 1)
        # Slight preference for earlier sentences, while preserving original order later.
        score += max(0, 0.08 - index * 0.002)
        scored.append((score, index, sentence))

    selected = sorted(sorted(scored, reverse=True)[:sentence_count], key=lambda item: item[1])
    return " ".join(item[2] for item in selected)
