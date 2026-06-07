import json
import urllib.request
import urllib.parse
import urllib.error
import ssl


_TITLE_ANGLES = {
    "history": "the historical development of",
    "historical": "the historical development of",
    "origins": "the origins and evolution of",
    "evolution": "how {term} has evolved over time",
    "development": "how {term} developed historically",
    "early": "the early formulations of",
    "modern": "modern perspectives on",
    "contemporary": "contemporary critiques and debates around",
    "today": "contemporary critiques and debates around",
    "current": "current debates around",
    "future": "emerging directions in thinking about",
    "revisited": "a reassessment and updating of",
    "legacy": "the lasting influence of",
    "backlash": "opposition and backlash against",
    "contesting": "competing arguments for and against",
    "critique": "a critical examination of",
    "criticism": "criticisms and counterarguments to",
    "against": "arguments challenging",
    "beyond": "moving past traditional understandings of",
    "rethinking": "reconsidering fundamental assumptions about",
    "reclaiming": "reclaiming and redefining",
    "redefining": "redefining the boundaries of",
    "reimagining": "new ways of conceptualizing",
    "deconstructing": "breaking down the logic of",
    "unpacking": "revealing the hidden layers of",
    "interrogating": "questioning the foundations of",
    "challenging": "challenging conventional views on",
    "questioning": "raising new questions about",
    "slippage": "gaps and inconsistencies in how {term} is applied",
    "slippages": "gaps and inconsistencies in how {term} is applied",
    "problematic": "the problems and contradictions within",
    "paradox": "the tensions and contradictions in",
    "limits": "the limitations and boundaries of",
    "failure": "where {term} falls short",
    "crisis": "how {term} relates to moments of crisis",
    "thinking": "how to use {term} as a conceptual tool",
    "concept": "the conceptual foundations of",
    "theory": "the theoretical framework of",
    "framework": "a framework for understanding",
    "approach": "a particular approach to",
    "model": "a model for analyzing",
    "lens": "using {term} as an analytical lens",
    "reading": "a close reading through the lens of",
    "towards": "building toward a theory of",
    "for": "a case for the value of",
    "why": "the importance and relevance of",
    "what": "defining and clarifying the meaning of",
    "definition": "how {term} is defined and understood",
    "meaning": "the meaning and significance of",
    "understanding": "deepening your understanding of",
    "thinking with": "how to apply {term} as a thinking tool",
    "application": "how {term} is applied in practice",
    "applications": "how {term} is applied in practice",
    "practice": "how {term} works in practice",
    "praxis": "the relationship between {term} theory and practice",
    "invisible": "what remains hidden or unseen about",
    "visibility": "the visibility and recognition of",
    "see": "what becomes visible through {term}",
    "state": "how {term} intersects with state power and governance",
    "law": "the legal dimensions of",
    "policy": "policy implications of",
    "politics": "the political dimensions of",
    "political": "the political stakes of",
    "economy": "the economic dimensions of",
    "economic": "how {term} relates to economic structures",
    "capital": "how {term} intersects with capital and markets",
    "market": "market dynamics within",
    "labor": "the role of labor in",
    "work": "the role of work and labor in",
    "institution": "how {term} operates within institutions",
    "institutional": "how {term} is embedded in institutions",
    "education": "how {term} relates to education and pedagogy",
    "school": "how {term} plays out in educational settings",
    "family": "how {term} shapes family structures",
    "domestic": "the domestic and private dimensions of",
    "public": "the public dimensions of",
    "private": "the private dimensions of",
    "body": "how {term} relates to bodies and embodiment",
    "embodiment": "the embodied experience of",
    "subjectivity": "how {term} shapes subjectivity and selfhood",
    "identity": "how {term} shapes identity formation",
    "self": "the relationship between {term} and the self",
    "agency": "how individuals exercise agency within",
    "resistance": "forms of resistance within",
    "subversion": "subversive strategies within",
    "media": "how {term} plays out in media representations",
    "film": "how {term} is represented in cinema",
    "cinema": "cinematic explorations of",
    "television": "how {term} appears in television",
    "digital": "how {term} operates in digital spaces",
    "internet": "how {term} manifests online",
    "social media": "how {term} plays out on social media platforms",
    "visual": "the visual dimensions of",
    "image": "how images construct and convey",
    "representation": "how {term} is represented culturally",
    "culture": "the cultural dimensions of",
    "popular": "how {term} appears in popular culture",
    "art": "artistic engagements with",
    "literature": "how {term} is explored in literature",
    "narrative": "how narratives shape and convey",
    "story": "the role of storytelling in",
    "discourse": "how discourse shapes",
    "language": "the role of language in",
    "rhetoric": "rhetorical strategies in",
    "race": "how {term} intersects with race and racialization",
    "racial": "the racial dimensions of",
    "class": "how {term} intersects with class and inequality",
    "sexuality": "how {term} intersects with sexuality",
    "sex": "the sexual dimensions of",
    "gender": "the gendered dimensions of",
    "women": "how {term} relates to women's experiences",
    "men": "how {term} relates to men and masculinity",
    "masculinity": "how {term} relates to constructions of masculinity",
    "femininity": "how {term} relates to constructions of femininity",
    "queer": "queer perspectives on",
    "trans": "trans perspectives on",
    "intersectional": "how {term} works across multiple axes of identity",
    "global": "global and cross-cultural perspectives on",
    "postcolonial": "postcolonial critiques of",
    "colonial": "how {term} relates to colonial history",
    "decolonial": "decolonial approaches to",
    "western": "how {term} is shaped by Western thought",
    "non-western": "non-Western perspectives on",
    "system": "how {term} operates as a system",
    "structure": "the structural dimensions of",
    "power": "how power operates within",
    "hierarchy": "hierarchical structures within",
    "norm": "how norms are established and enforced through",
    "norms": "how norms are established and enforced through",
    "normalization": "how {term} normalizes certain behaviors and identities",
    "binary": "the binary logics underlying",
    "dichotomy": "the dichotomies that structure",
    "dualism": "the dualisms embedded in",
    "category": "how categories are constructed in",
    "boundary": "how boundaries are drawn in",
}


def _get_relevance_keyword(term_name, title):
    title_lower = title.lower()
    term_lower = term_name.lower()
    term_words = set(term_lower.split())

    title_without_term = title_lower
    for w in term_words:
        title_without_term = title_without_term.replace(w, " ")

    sorted_angles = sorted(_TITLE_ANGLES.keys(), key=len, reverse=True)
    for angle in sorted_angles:
        if angle in title_without_term:
            template = _TITLE_ANGLES[angle]
            if "{term}" in template:
                return "Read to explore " + template.format(term=term_lower)
            return "Read to explore " + template + " " + term_lower

    for angle in sorted_angles:
        if angle in title_lower:
            template = _TITLE_ANGLES[angle]
            if "{term}" in template:
                return "Read to explore " + template.format(term=term_lower)
            return "Read to explore " + template + " " + term_lower

    stop_words = {
        "the", "a", "an", "of", "and", "in", "on", "to", "for", "with", "by",
        "from", "at", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "it", "its", "this", "that",
        "these", "those", "or", "but", "not", "no", "nor", "so", "yet", "both",
        "each", "every", "all", "any", "few", "more", "most", "other", "some",
        "such", "than", "too", "very", "just", "about", "into", "through",
        "during", "before", "after", "above", "below", "between", "under",
        "introduction", "conclusion", "chapter", "part", "section",
    }
    skip = stop_words | term_words
    title_words = [w.strip(",.():;\"'") for w in title_lower.split()
                   if w.strip(",.():;\"'") not in skip and len(w.strip(",.():;\"'")) > 3]
    if title_words:
        focus = ", ".join(title_words[:3])
        return "Read to understand how " + term_lower + " relates to " + focus

    return "Read to deepen your understanding of " + term_lower


def fetch_readings(term_name):
    try:
        query = urllib.parse.quote(term_name)
        url = f"https://api.crossref.org/works?query={query}&rows=3&sort=relevance"
        req = urllib.request.Request(url, headers={"User-Agent": "TheoryLens/1.0 (student project)"})
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            data = json.loads(response.read().decode("utf-8"))

        results = []
        for item in data.get("message", {}).get("items", []):
            title = item.get("title", ["Untitled"])[0]
            authors_list = item.get("author", [])
            if authors_list:
                authors = ", ".join(
                    f"{a.get('family', '')} {a.get('given', '')}".strip()
                    for a in authors_list[:3]
                    if a.get("family")
                )
                if not authors.strip():
                    authors = "Unknown"
            else:
                authors = "Unknown"
            year = item.get("published-print", item.get("published-online", {}))
            year_str = str(year.get("date-parts", [[None]])[0][0]) if year else "n.d."
            doi = item.get("DOI", "")
            relevance = _get_relevance_keyword(term_name, title)

            results.append({
                "title": title,
                "authors": authors,
                "year": year_str,
                "doi": doi,
                "relevance": relevance
            })

        return results

    except urllib.error.URLError:
        return []
    except (TimeoutError, OSError):
        return []
    except Exception:
        return []
