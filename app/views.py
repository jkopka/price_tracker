from flask import current_app as app
from flask import render_template
from flask import Markup, request
from app.models import Plattform
from urllib.parse import unquote


@app.route("/")
def index():
    """
    Zeigt Eingabeformular für die Suchen an. Wenn url1, url2 oder keywords übergeben werden, wird das Formular vor ausgefüllt.
    """
    url1 = ""
    url2 = ""
    keywords = ""
    if "url1" in request.args:
        url1 = request.args["url1"]
    if "url2" in request.args:
        url2 = request.args["url2"]
    if "keywords" in request.args:
        keywords = request.args["keywords"]

    return render_template(
        "form_input.html",
        title="Price Tracker",
        url1=url1,
        url2=url2,
        keywords=keywords,
    )


@app.route("/result")
def result():
    """
    Generiert die Auswertung zu den übergebenen URLs.
    """
    # source und url1 müssen übergeben werden. Sonst wird das Eingabeformular angezeigt.
    if "source" in request.args and not request.args["url1"].strip() == "":
        # In urls werden die Links gesammelt. Es besteht also die Möglichkeit, mehr als zwei URLs zu bearbeiten.
        urls = []
        urls.append(unquote(request.args["url1"]))
        if not request.args["url2"].strip() == "":
            urls.append(unquote(request.args["url2"]))
    else:
        # Eingabeform anzeigen, wenn source nicht übergeben wurde.
        return render_template("form_input.html", title="Price Tracker")

    # Keywords übernehmen.
    if request.args["keywords"]:
        keywords = request.args["keywords"].strip().split()
    else:
        # keywords = ['reperatur', 'reparatur', 'suche']
        keywords = []
    # print('Keywords:', keywords)

    # Objekt plattform mit den übergebenen urls und keywords erstellen.
    plattform = Plattform(urls, keywords)

    # .fetch startet das Webscraping.
    fetch_return = plattform.fetch()
    print("Fetch Return:", fetch_return)

    # Wenn alles in Ordnung ist...
    if fetch_return == True:
        return render_template(
            "result.html",
            search_items=plattform.search_items,
            url=plattform.get_plot(),
            search_title=plattform.get_search_querys(),
            title=plattform.get_search_querys(),
        )
    # Bei False wird eine Fehlerseite angezeigt.
    elif fetch_return == False:
        # print('Fetch Return:', fetch_return)
        return render_template(
            "result_false.html",
            error=plattform.get_error(),
            search_title=plattform.get_search_querys(),
        )
