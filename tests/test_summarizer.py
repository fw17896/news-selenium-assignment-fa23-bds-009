from summarizer import summarize


def test_summarizer_returns_text():
    article = (
        "Researchers announced a new climate study today. "
        "The study measures rising temperatures across several regions. "
        "Scientists say the findings can help communities prepare for heat. "
        "The research team will publish more data next month."
    )
    result = summarize(article, sentence_count=2)
    assert isinstance(result, str)
    assert len(result) > 20
