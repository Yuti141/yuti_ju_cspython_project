import database
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl


# Angle keywords found in article titles → what they signal about the article's focus
_TITLE_ANGLES = {
    # Historical / temporal
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

    # Critical / analytical stance
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

    # Theoretical / conceptual
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

    # Social / political / institutional
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

    # Identity / embodiment
    "body": "how {term} relates to bodies and embodiment",
    "embodiment": "the embodied experience of",
    "subjectivity": "how {term} shapes subjectivity and selfhood",
    "identity": "how {term} shapes identity formation",
    "self": "the relationship between {term} and the self",
    "agency": "how individuals exercise agency within",
    "resistance": "forms of resistance within",
    "subversion": "subversive strategies within",

    # Media / cultural
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

    # Intersectional / comparative
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

    # Structure / system
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
    """Returns a phrase explaining why a reading is relevant, based on the article title."""
    title_lower = title.lower()
    term_lower = term_name.lower()
    term_words = set(term_lower.split())

    # Build a version of the title with the term's own words removed,
    # so we match on what makes THIS article different
    title_without_term = title_lower
    for w in term_words:
        title_without_term = title_without_term.replace(w, " ")

    # Try angle keywords on the term-stripped title first (article-specific angles)
    sorted_angles = sorted(_TITLE_ANGLES.keys(), key=len, reverse=True)
    for angle in sorted_angles:
        if angle in title_without_term:
            template = _TITLE_ANGLES[angle]
            if "{term}" in template:
                return "Read to explore " + template.format(term=term_lower)
            return "Read to explore " + template + " " + term_lower

    # Try angle keywords on the full title (may match on the term itself)
    for angle in sorted_angles:
        if angle in title_lower:
            template = _TITLE_ANGLES[angle]
            if "{term}" in template:
                return "Read to explore " + template.format(term=term_lower)
            return "Read to explore " + template + " " + term_lower

    # Fallback: extract distinctive words from the title (skip term words + stop words)
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
    """
    Fetches reading recommendations from the Crossref API for a given term.

    Args:
        term_name: The term to search for (e.g., "Male Gaze").

    Returns:
        List of dicts with title, authors, year, doi, and relevance.
    """
    try:
        query = urllib.parse.quote(term_name)
        url = f"https://api.crossref.org/works?query={query}&rows=3&sort=relevance"
        req = urllib.request.Request(url, headers={"User-Agent": "TheoryLens/1.0 (student project)"})
        # SSL context to handle macOS certificate issues
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


def display_main_menu(term_of_day):
    """
    Renders the main screen with search prompt, term of the day, and menu options.
    """
    print()
    print("=" * 40)
    print("           THEORYLENS")
    print("    Your Gender & Media Theory Guide")
    print("=" * 40)
    print()

    if term_of_day:
        # Truncate definition for display
        definition = term_of_day["definition"]
        if len(definition) > 120:
            definition = definition[:117] + "..."
        print("Term of the Day:")
        print(f"  {term_of_day['name']} — {definition}")
        print()

    print("Search for a term: (type to search, or press Enter for menu)")
    print()
    print("── or choose an option ──")
    print("1. Browse by category")
    print("2. My study list")
    print("3. Concept map")
    print("4. Manage connections")
    print("5. Add a new term")
    print("6. Exit")


def handle_search():
    """Handles the search flow: prompt, results, term view."""
    query = input("\nSearch: ").strip()
    if not query:
        return

    results = database.search_terms(query)
    if not results:
        print(f"\nNo terms found for '{query}'. Try a different search or browse by category.")
        return

    print(f"\nResults for \"{query}\":")
    for i, r in enumerate(results, 1):
        # Show preview snippet
        def_preview = r["definition"]
        if len(def_preview) > 80:
            def_preview = def_preview[:77] + "..."
        tags = r["tags"] or "No tags"
        print(f"  {i}. {r['name']} — {def_preview}")
        print(f"     Tags: {tags}")

    print()
    choice = input("Pick a term (or 0 to go back): ").strip()
    try:
        choice_num = int(choice)
    except ValueError:
        print("Please enter a valid number.")
        return

    if choice_num == 0:
        return
    if 1 <= choice_num <= len(results):
        handle_term_view(results[choice_num - 1]["id"])
    else:
        print(f"Please enter a number between 0 and {len(results)}.")


def handle_term_view(term_id):
    """Displays full term details: definition, tags, connections, study status, readings."""
    try:
        term = database.view_term(term_id)
    except ValueError as e:
        print(f"\n{e}")
        return

    print()
    print("=" * 40)
    print(f"         {term['name'].upper()}")
    print("=" * 40)

    tags = term["tags"] or "No tags"
    print(f"Tags: {tags}")
    print()
    print("Definition:")
    print(f"  {term['definition']}")
    print()

    # Connections
    connections = term["connections"]
    if connections:
        print("Connections:")
        for i, conn in enumerate(connections):
            prefix = "├──" if i < len(connections) - 1 else "└──"
            explanation = conn["explanation"]
            if len(explanation) > 60:
                explanation = explanation[:57] + "..."
            print(f"  {prefix} {conn['term_name']} — \"{explanation}\"")
    else:
        print("Connections: None yet. Go to Manage Connections to add one.")
    print()

    # Study status
    status_display = {
        "want_to_learn": "Want to Learn",
        "in_progress": "In Progress",
        "learned": "Learned"
    }
    if term["study_status"]:
        print(f"Study Status: {status_display.get(term['study_status'], term['study_status'])}")
    else:
        print("Study Status: Not in study list")
    print()

    # Reading recommendations
    print("Reading Recommendations:")
    readings = fetch_readings(term["name"])
    if readings:
        for i, r in enumerate(readings, 1):
            print(f'  {i}. "{r["title"]}" — {r["authors"]} ({r["year"]})')
            if r["doi"]:
                print(f"     DOI: {r['doi']}")
    else:
        print("  Could not fetch reading recommendations. Try again later.")
    print()

    # Options
    print("Options:")
    print("1. Add to study list")
    print("2. Update study status")
    print("3. Back")
    choice = input("Choose: ").strip()

    if choice == "1":
        handle_add_to_study_list(term_id)
    elif choice == "2":
        handle_update_study_status(term_id)


def handle_add_to_study_list(term_id):
    """Prompts user to add a term to their study list with a status."""
    print("\nSet status:")
    print("1. Want to Learn")
    print("2. In Progress")
    print("3. Learned")
    choice = input("Choose (or 0 to cancel): ").strip()

    status_map = {"1": "want_to_learn", "2": "in_progress", "3": "learned"}
    if choice == "0":
        return
    if choice not in status_map:
        print("Please enter a number between 1 and 3.")
        return

    try:
        database.add_to_study_list(term_id, status_map[choice])
        status_display = {"want_to_learn": "Want to Learn", "in_progress": "In Progress", "learned": "Learned"}
        print(f"\nAdded to study list as '{status_display[status_map[choice]]}'.")
    except ValueError as e:
        print(f"\n{e}")


def handle_update_study_status(term_id):
    """Prompts user to update a term's learning status."""
    print("\nNew status:")
    print("1. Want to Learn")
    print("2. In Progress")
    print("3. Learned")
    choice = input("Choose (or 0 to cancel): ").strip()

    status_map = {"1": "want_to_learn", "2": "in_progress", "3": "learned"}
    if choice == "0":
        return
    if choice not in status_map:
        print("Please enter a number between 1 and 3.")
        return

    try:
        database.update_study_status(term_id, status_map[choice])
        status_display = {"want_to_learn": "Want to Learn", "in_progress": "In Progress", "learned": "Learned"}
        print(f"\nStatus updated to '{status_display[status_map[choice]]}'.")
    except ValueError as e:
        print(f"\n{e}")


def handle_browse():
    """Handles the browse by category flow."""
    tags = database.get_all_tags()
    if not tags:
        print("\nNo categories found.")
        return

    print("\nCategories:")
    for i, t in enumerate(tags, 1):
        print(f"  {i}. {t['tag']} ({t['count']} terms)")
    print(f"  {len(tags) + 1}. Filter by multiple tags")
    print()

    choice = input("Pick a category (or 0 to go back): ").strip()
    try:
        choice_num = int(choice)
    except ValueError:
        print("Please enter a valid number.")
        return

    if choice_num == 0:
        return

    if 1 <= choice_num <= len(tags):
        selected_tag = tags[choice_num - 1]["tag"]
        display_terms_by_tag(selected_tag)
    elif choice_num == len(tags) + 1:
        handle_multi_tag_filter(tags)
    else:
        print(f"Please enter a number between 0 and {len(tags) + 1}.")


def display_terms_by_tag(tag):
    """Displays all terms under a given tag, alphabetically."""
    terms = database.get_terms_by_tag(tag)
    if not terms:
        print(f"\nNo terms found in '{tag}'.")
        return

    print(f"\n--- {tag} ({len(terms)} terms) ---")
    for i, t in enumerate(terms, 1):
        def_preview = t["definition"]
        if len(def_preview) > 70:
            def_preview = def_preview[:67] + "..."
        print(f"  {i:2d}. {t['name']} — {def_preview}")

    print()
    choice = input("Pick a term (or 0 to go back): ").strip()
    try:
        choice_num = int(choice)
    except ValueError:
        print("Please enter a valid number.")
        return

    if choice_num == 0:
        return
    if 1 <= choice_num <= len(terms):
        handle_term_view(terms[choice_num - 1]["id"])
    else:
        print(f"Please enter a number between 0 and {len(terms)}.")


def handle_multi_tag_filter(all_tags):
    """Lets user pick multiple tags and shows intersection."""
    print("\nSelect tags (comma-separated numbers, e.g., '1,3'):")
    for i, t in enumerate(all_tags, 1):
        print(f"  {i}. {t['tag']}")

    choice = input("\nTags: ").strip()
    try:
        indices = [int(x.strip()) for x in choice.split(",")]
    except ValueError:
        print("Please enter valid numbers separated by commas.")
        return

    selected_tags = []
    for idx in indices:
        if 1 <= idx <= len(all_tags):
            selected_tags.append(all_tags[idx - 1]["tag"])
        else:
            print(f"Invalid selection: {idx}")
            return

    if not selected_tags:
        print("No tags selected.")
        return

    # Find terms that have ALL selected tags
    all_terms = database.get_all_terms()
    matching = []
    for t in all_terms:
        term_tags = [tag.strip() for tag in (t["tags"] or "").split(",")]
        if all(tag in term_tags for tag in selected_tags):
            matching.append(t)

    if not matching:
        print(f"\nNo terms found with tags: {', '.join(selected_tags)}")
        return

    print(f"\n--- Terms tagged: {', '.join(selected_tags)} ({len(matching)} terms) ---")
    for i, t in enumerate(matching, 1):
        print(f"  {i}. {t['name']}")

    print()
    choice = input("Pick a term (or 0 to go back): ").strip()
    try:
        choice_num = int(choice)
    except ValueError:
        print("Please enter a valid number.")
        return

    if choice_num == 0:
        return
    if 1 <= choice_num <= len(matching):
        # Need to get full term details
        results = database.search_terms(matching[choice_num - 1]["name"])
        if results:
            handle_term_view(results[0]["id"])


def handle_study_list():
    """Displays the user's study list grouped by status."""
    study_list = database.get_study_list()

    total = (
        len(study_list["want_to_learn"]) +
        len(study_list["in_progress"]) +
        len(study_list["learned"])
    )

    if total == 0:
        print("\nYour study list is empty. Search for terms and add them to start studying!")
        return

    print("\n=== My Study List ===")

    status_labels = {
        "want_to_learn": "Want to Learn",
        "in_progress": "In Progress",
        "learned": "Learned"
    }

    for status_key, label in status_labels.items():
        terms = study_list[status_key]
        print(f"\n{label} ({len(terms)} terms):")
        if terms:
            for t in terms:
                tags = t["tags"] or "No tags"
                print(f"  - {t['name']} ({tags})")
        else:
            print("  (none)")

    print()
    print("Options:")
    print("1. View a term")
    print("2. Update status")
    print("3. Back to menu")
    choice = input("Choose: ").strip()

    if choice == "1":
        term_name = input("Enter term name: ").strip()
        if term_name:
            results = database.search_terms(term_name)
            if results:
                handle_term_view(results[0]["id"])
            else:
                print(f"Term '{term_name}' not found.")
    elif choice == "2":
        term_name = input("Enter term name to update: ").strip()
        if term_name:
            results = database.search_terms(term_name)
            if results:
                handle_update_study_status(results[0]["id"])
            else:
                print(f"Term '{term_name}' not found.")


def handle_concept_map():
    """Displays the concept map: pick a term, see its connections."""
    all_terms = database.get_all_terms()
    if not all_terms:
        print("\nNo terms in database.")
        return

    print("\nAll terms:")
    for i, t in enumerate(all_terms, 1):
        print(f"  {i:2d}. {t['name']}")

    print()
    choice = input("Pick a term to view connections (or 0 to go back): ").strip()
    try:
        choice_num = int(choice)
    except ValueError:
        print("Please enter a valid number.")
        return

    if choice_num == 0:
        return
    if 1 <= choice_num <= len(all_terms):
        term = all_terms[choice_num - 1]
        display_concept_map_for_term(term["id"], term["name"])
    else:
        print(f"Please enter a number between 0 and {len(all_terms)}.")


def display_concept_map_for_term(term_id, term_name):
    """Shows connections for a specific term in adjacency list format."""
    connections = database.get_connections(term_id)

    print(f"\n{term_name}")
    if not connections:
        print("  No connections yet. Go to Manage Connections to add one.")
    else:
        for i, conn in enumerate(connections):
            prefix = "├──" if i < len(connections) - 1 else "└──"
            explanation = conn["explanation"]
            if len(explanation) > 60:
                explanation = explanation[:57] + "..."
            print(f"  {prefix} {conn['term_name']} — \"{explanation}\"")

    print()
    input("Press Enter to continue...")


def handle_manage_connections():
    """Dedicated screen for creating connections between terms."""
    all_terms = database.get_all_terms()
    if len(all_terms) < 2:
        print("\nNeed at least 2 terms to create connections.")
        return

    print("\n--- Manage Connections ---")
    print("\nSelect first term:")
    for i, t in enumerate(all_terms, 1):
        print(f"  {i:2d}. {t['name']}")

    print()
    choice_a = input("Pick term A (or 0 to go back): ").strip()
    try:
        choice_a_num = int(choice_a)
    except ValueError:
        print("Please enter a valid number.")
        return

    if choice_a_num == 0:
        return
    if not (1 <= choice_a_num <= len(all_terms)):
        print(f"Please enter a number between 1 and {len(all_terms)}.")
        return

    term_a = all_terms[choice_a_num - 1]

    print(f"\nSelect second term (not '{term_a['name']}'):")
    for i, t in enumerate(all_terms, 1):
        if t["id"] != term_a["id"]:
            print(f"  {i:2d}. {t['name']}")

    print()
    choice_b = input("Pick term B: ").strip()
    try:
        choice_b_num = int(choice_b)
    except ValueError:
        print("Please enter a valid number.")
        return

    if not (1 <= choice_b_num <= len(all_terms)):
        print(f"Please enter a number between 1 and {len(all_terms)}.")
        return

    term_b = all_terms[choice_b_num - 1]
    if term_b["id"] == term_a["id"]:
        print("Cannot connect a term to itself.")
        return

    explanation = input("\nExplain the connection: ").strip()
    if not explanation:
        print("Explanation cannot be empty.")
        return

    try:
        database.add_connection(term_a["id"], term_b["id"], explanation)
        print(f"\nConnection created: {term_a['name']} ↔ {term_b['name']}")
    except ValueError as e:
        print(f"\n{e}")


def handle_add_term():
    """Guided flow for adding a new term."""
    print("\n--- Add a New Term ---")

    name = input("\nTerm name: ").strip()
    if not name:
        print("Term name cannot be empty.")
        return

    definition = input("Definition: ").strip()
    if not definition:
        print("Definition cannot be empty.")
        return

    tags_input = input("Tags (comma-separated, e.g., 'Feminism, Queer Theory'): ").strip()
    tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []

    # Confirm
    print(f"\nSummary:")
    print(f"  Name: {name}")
    print(f"  Definition: {definition[:100]}{'...' if len(definition) > 100 else ''}")
    print(f"  Tags: {', '.join(tags) if tags else 'None'}")

    confirm = input("\nSave this term? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    try:
        new_id = database.add_term(name, definition, tags)
        print(f"\nTerm '{name}' added successfully!")
    except ValueError as e:
        print(f"\n{e}")


def run():
    """Main application loop. Handles menu navigation and user input."""
    database.init_database()

    while True:
        term_of_day = database.get_term_of_day()
        display_main_menu(term_of_day)

        print()
        choice = input("What would you like to do? ").strip()

        if not choice:
            # Empty input — treat as search mode
            handle_search()
        elif choice == "1":
            handle_browse()
        elif choice == "2":
            handle_study_list()
        elif choice == "3":
            handle_concept_map()
        elif choice == "4":
            handle_manage_connections()
        elif choice == "5":
            handle_add_term()
        elif choice == "6":
            print("\nGoodbye! Happy studying.")
            break
        else:
            # Could be a search query typed directly
            results = database.search_terms(choice)
            if results:
                print(f"\nResults for \"{choice}\":")
                for i, r in enumerate(results, 1):
                    def_preview = r["definition"]
                    if len(def_preview) > 80:
                        def_preview = def_preview[:77] + "..."
                    print(f"  {i}. {r['name']} — {def_preview}")
                    print(f"     Tags: {r['tags'] or 'No tags'}")

                print()
                pick = input("Pick a term (or 0 to go back): ").strip()
                try:
                    pick_num = int(pick)
                    if 1 <= pick_num <= len(results):
                        handle_term_view(results[pick_num - 1]["id"])
                except ValueError:
                    pass
            else:
                print("Please enter a valid option (1-6) or a search term.")


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\nGoodbye! Happy studying.")
