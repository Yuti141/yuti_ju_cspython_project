from flask import Flask, render_template, request, redirect, url_for, flash
import database
import app as core

app_flask = Flask(__name__)
app_flask.secret_key = "theorylens_secret_key"


@app_flask.route("/")
def home():
    term_of_day = database.get_term_of_day()
    tags = database.get_all_tags()
    return render_template("home.html", term_of_day=term_of_day, tags=tags)


@app_flask.route("/new-term-of-day", methods=["POST"])
def new_term_of_day():
    database.get_term_of_day(force_new=True)
    return redirect(url_for("home"))


@app_flask.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return redirect(url_for("home"))
    results = database.search_terms(query)
    return render_template("search.html", query=query, results=results)


@app_flask.route("/term/<int:term_id>")
def term_view(term_id):
    try:
        term = database.view_term(term_id)
    except ValueError:
        flash("Term not found.", "error")
        return redirect(url_for("home"))

    readings = core.fetch_readings(term["name"])
    all_terms = database.get_all_terms()
    return render_template("term.html", term=term, readings=readings, all_terms=all_terms)


@app_flask.route("/browse")
def browse():
    tags = database.get_all_tags()
    return render_template("browse.html", tags=tags)


@app_flask.route("/browse/<path:tag>")
def browse_tag(tag):
    terms = database.get_terms_by_tag(tag)
    return render_template("browse_tag.html", tag=tag, terms=terms)


@app_flask.route("/study-list")
def study_list():
    sl = database.get_study_list()
    return render_template("study_list.html", study_list=sl)


@app_flask.route("/concept-map")
def concept_map():
    all_terms = database.get_all_terms()
    selected_term = request.args.get("term_id")
    connections = None
    term_name = None

    if selected_term:
        try:
            term = database.view_term(int(selected_term))
            connections = term["connections"]
            term_name = term["name"]
        except (ValueError, TypeError):
            pass

    return render_template("concept_map.html", all_terms=all_terms, connections=connections, term_name=term_name, selected_term=selected_term)


@app_flask.route("/connections", methods=["GET", "POST"])
def manage_connections():
    all_terms = database.get_all_terms()

    if request.method == "POST":
        term_a_id = request.form.get("term_a_id")
        term_b_id = request.form.get("term_b_id")
        explanation = request.form.get("explanation", "").strip()

        if not term_a_id or not term_b_id:
            flash("Please select both terms.", "error")
            return redirect(url_for("manage_connections"))

        if term_a_id == term_b_id:
            flash("Cannot connect a term to itself.", "error")
            return redirect(url_for("manage_connections"))

        if not explanation:
            flash("Explanation cannot be empty.", "error")
            return redirect(url_for("manage_connections"))

        try:
            database.add_connection(int(term_a_id), int(term_b_id), explanation)
            flash("Connection created!", "success")
        except ValueError as e:
            flash(str(e), "error")

        return redirect(url_for("manage_connections"))

    return render_template("connections.html", all_terms=all_terms)


@app_flask.route("/add-term", methods=["GET", "POST"])
def add_term():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        definition = request.form.get("definition", "").strip()
        tags_input = request.form.get("tags", "").strip()
        tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []

        if not name:
            flash("Term name cannot be empty.", "error")
            return redirect(url_for("add_term"))
        if not definition:
            flash("Definition cannot be empty.", "error")
            return redirect(url_for("add_term"))

        try:
            new_id = database.add_term(name, definition, tags)
            flash(f"Term '{name}' added successfully!", "success")
            return redirect(url_for("term_view", term_id=new_id))
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("add_term"))

    return render_template("add_term.html")


@app_flask.route("/add-to-study-list/<int:term_id>", methods=["POST"])
def add_to_study_list(term_id):
    status = request.form.get("status", "want_to_learn")
    try:
        database.add_to_study_list(term_id, status)
        flash("Added to study list!", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("term_view", term_id=term_id))


@app_flask.route("/update-study-status/<int:term_id>", methods=["POST"])
def update_study_status(term_id):
    new_status = request.form.get("status", "want_to_learn")
    try:
        database.update_study_status(term_id, new_status)
        flash("Status updated!", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("term_view", term_id=term_id))


@app_flask.route("/delete-term/<int:term_id>", methods=["POST"])
def delete_term(term_id):
    try:
        database.delete_term(term_id)
        flash("Term deleted.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("home"))


@app_flask.route("/edit-term/<int:term_id>", methods=["GET", "POST"])
def edit_term(term_id):
    try:
        term = database.view_term(term_id)
    except ValueError:
        flash("Term not found.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        definition = request.form.get("definition", "").strip()
        tags_input = request.form.get("tags", "").strip()
        tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []

        try:
            database.edit_term(term_id, name=name, definition=definition, tags=tags)
            flash("Term updated!", "success")
            return redirect(url_for("term_view", term_id=term_id))
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("edit_term", term_id=term_id))

    return render_template("edit_term.html", term=term)


if __name__ == "__main__":
    database.init_database()
    app_flask.run(debug=True, port=5000)
