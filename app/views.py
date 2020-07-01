from flask import current_app as app
from flask import render_template
from flask import Markup, request
from app.models import Plattform
from urllib.parse import unquote

@app.route('/')
def index():
    url1 = ''
    url2 = ''
    keywords = ''
    if 'url1' in request.args:
        url1 = request.args['url1']
    if 'url2' in request.args:
        url2 = request.args['url2']
    if 'keywords' in request.args:
        keywords = request.args['keywords']
    
    return render_template("form_input.html", title="Price Tracker", url1=url1, url2=url2, keywords=keywords)


@app.route('/result')
def result():
    if 'source' in request.args:
        if request.args['url1'].strip() == '':
            return render_template("form_input.html", title="Price Tracker")
        urls = []
        urls.append(unquote(request.args['url1']))
        if not request.args['url2'].strip() == '':
            urls.append(unquote(request.args['url2']))
    else:
        # Eingabeform anzeigen
        return render_template("form_input.html", title="Price Tracker")
    if request.args['keywords']:
        keywords = request.args['keywords'].strip().split()
    else:
        keywords = ['reperatur', 'reparatur', 'suche']
    # print('Keywords:', keywords)
    plattform = Plattform( urls, keywords)
    plattform.set_max_articles(1000)
    
    search_item_output = []
    fetch_return = plattform.fetch()
    print('Fetch Return:', fetch_return)
    if fetch_return == True:
        for search_item in plattform.search_items:
            search_item_output.append(search_item)
        plot = plattform.get_plot()
        return render_template("result.html", search_items=plattform.search_items,url=plot, search_title=plattform.get_search_querys(), title=plattform.get_search_querys())
    elif fetch_return == False:
        error = plattform.get_error()
        # print('Fetch Return:', fetch_return)
        search_item_output.append('False')
        plot = 'False'
        return render_template("result_false.html", error=error, search_title=plattform.get_search_querys())
    # print('Len:',len(search_item_output))
    