MAX_SUBJECT = 60


def render_subject(title: str) -> str:
    return title[:MAX_SUBJECT]
