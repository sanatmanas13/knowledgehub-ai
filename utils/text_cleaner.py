def clean_text(text: str) -> str:
    """
    Clean extracted PDF text by removing tabs and normalizing whitespaces.
    """
    text = text.replace("\t"," ")
    text = " ".join(text.split())

    return text