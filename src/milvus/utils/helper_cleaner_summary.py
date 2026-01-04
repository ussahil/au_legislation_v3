import re

def act_summary_cleaner(headings:list[str]) -> list[str]:
    """
    Input Args : List
    Output Args : List
    Takes in a list and after it removes structural act from all of them using regex
    """
    if not headings:
        return []

    REMOVE_EXACT = {
        "short title",
        "commencement",
        "definitions",
        "interpretation",
        "repeal",
        "application",
        "regulations",
        "rules",
    }
    REMOVE_CONTAINS = {
         "schedule",
        "note",
        "transitional",
        "saving",
        "repealed",
    }
    REMOVE_WORDS_REGEX = re.compile(
        r"\b(" + "|".join(REMOVE_CONTAINS) + r")\b"
    )

    cleaned = []
    for h in headings:
        if not h or not isinstance(h,str):
            continue
        # normalize
        text = h.lower().strip()
        
        #  Best to remove subsection numbers as all docs will have them
        text = re.sub(r"^\d+[a-zA-Z\-]*\s*", "", text)

        # Remove trailing puntuation
        text = re.sub(r"[.:;]+$", "", text)
        text = re.sub(r"\(.*?\)", "", text).strip()

        # Exact match Removal
        if text in REMOVE_EXACT:
            continue

        if REMOVE_WORDS_REGEX.search(text):
            continue

        cleaned.append(text)
    return list(dict.fromkeys(cleaned)) #Dedupe to clean it all..
