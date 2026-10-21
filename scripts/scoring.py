def score_article(article):
    score = article.get("relevance_score", 0)

    specialist_sources = {
        "semiconductor_today_news",
        "semiconductor_today_features",
        "semiconductor_engineering",
        "ieee_spectrum_semiconductors",
        "semiwiki",
    }

    if article.get("source_id") in specialist_sources:
        score += 2

    if article.get("interpretation_valid") is True:
        score += 1

    return score
