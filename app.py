import database
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl


def fetch_readings(term_name):
    """
    Fetches reading recommendations from the Crossref API for a given term.

    Args:
        term_name: The term to search for (e.g., "Male Gaze").

    Returns:
        List of dicts with title, authors, year, and doi.
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
                )
            else:
                authors = "Unknown"
            year = item.get("published-print", item.get("published-online", {}))
            year_str = str(year.get("date-parts", [[None]])[0][0]) if year else "n.d."
            doi = item.get("DOI", "")

            results.append({
                "title": title,
                "authors": authors,
                "year": year_str,
                "doi": doi
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
