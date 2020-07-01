from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from re import sub
from decimal import Decimal
import numpy as np
import matplotlib.pyplot as plt
from flask import Markup
from urllib.parse import urlparse
import logging

import time

# Objekt für einzelne Suchen
class SearchItem:
    def __init__(self, url):
        self.url = url
        self.all_prices = []
        self.quantity = 0
        self.quantity_ignored = 0
        self.search_query = ""
        self.url_next_page = ""
        self.searched = False
        self.error = ""

    def get_search_query(self):
        return self.search_query

    def get_percentile(self, perc):
        # rint(self.all_prices)
        return np.percentile(self.all_prices, perc).round(2)

    def get_quantity(self):
        return self.quantity

    def get_quantity_ignored(self):
        return self.quantity_ignored


# Plattform
class Plattform:
    """
    Zentrale Klasse für das Crawlen.
    Über init einrichten. Dann über .fetch() crawlen.
    """

    def __init__(self, urls=[], keywords=[]):
        """
        Initialisiert die Klasse.
        Zu übergebende Parameter: urls<liste>, keywords<liste>
        """
        logging.basicConfig(
            format="%(asctime)s %(message)s", filename="logging.log", level=logging.INFO
        )
        self.base_url_ebay_kleinanzeigen = "https://www.ebay-kleinanzeigen.de/"
        self.base_url_ebay_de = "https://www.ebay.de/"
        self.max_articles = 1000
        self.urls = urls

        self.keywords = [element.lower() for element in keywords]
        # print(self.keywords)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        }
        self.proxies = {
            "http": None,
            "https": None,
        }
        search_items = []
        for url in urls:
            # Für jeden übergebenen Link wird ein SearchItem angelegt. Hier wird auch direkt gecheckt,
            # ob die URL valid und ob es sich um die mobile Website handelt.
            if self.uri_validator(url) == True:
                print("--------")
                logging.info("URL: " + url)
                print("--------")
                search_items.append(SearchItem(self.get_web_version(url)))
        self.search_items = search_items

    def get_web_version(self, url):
        """
        Funktion checkt, ob es sich bei dem Link um die mobile Website hält. Wenn ja, wird der Link zur Desktopversion geholt.

        Todo: Es fehlt noch der Teil für eBay.de
        """
        # print(url)
        if "m.ebay-kleinanzeigen" in url:
            print("Mobile version detected!")
            r = requests.get(url, headers=self.headers, proxies=self.proxies)
            doc = BeautifulSoup(r.text.replace("&#8203", ""), "html.parser")
            url = urljoin(
                self.base_url_ebay_kleinanzeigen,
                doc.find(id="footer-webversion-link").get("href"),
            )

        return url

    def uri_validator(self, x):
        """
        Validiert ein URL
        """
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc, result.path])
        except:
            return False

    def set_max_articles(self, max_articles):
        """
        Setzt die maximal zu crawlenden Artikel.
        """
        self.max_articles = max_articles if max_articles > 0 else 1000

    def fetch_url(self, url):
        """
        Holt eine URL mittels requests und liefert das Response-Objekt zurück.
        """
        try:
            # print('...fetching with headers',url)
            r = requests.get(url, headers=self.headers, proxies=self.proxies)
            r.raise_for_status()
            return r
        except:
            # print('fetch_url>except!', url)
            print(r.status_code)

        return r

    def fetch(self):
        """
        .fetch crawled jede URL.
        Keine Parameter. Bei Erfolg True, bei einem Fehler False.
        """
        if len(self.search_items) == 0:
            return False

        result = []
        for search_item in self.search_items:
            # https://www.ebay-kleinanzeigen.de/s-boote-bootszubehoer/detmold/jolle/k0c211l1792r30

            if "ebay-kleinanzeigen.de" in search_item.url:
                result.append(self.fetch_page_ebay_kleinanzeigen(search_item))
            elif "ebay.de" in search_item.url:
                result.append(self.fetch_page_ebay_de(search_item))
            else:
                print("Link unbekannt! -> ", search_item.url)
            # Momentan noch nicht implementiert!
            # elif search_item.site == 'ebay.de':
            # result.append(self.fetch_page_ebay_de(search_item))
            # print(result)
            for res in result:
                if res == False:
                    return False
        return True

    def fetch_page_ebay_kleinanzeigen(self, search_item):
        """Hole die Artikel der Seite.
        Übergabe von zu holender URL + aktuelle Anzahl der Artikel.
        Weitere Seiten werden über Rekursion bearbeitet.

        Rückgabe: Alle Artikelpreise als list, Anzahl der bearbeiteten Artikel
        """
        keywords = self.keywords

        # Artikel holen
        article = self.fetch_url(search_item.url)
        if article == False:
            return False

        doc = BeautifulSoup(article.text.replace("&#8203", ""), "html.parser")
        doc_search_query = doc.find(id="site-search-query")

        # Falls der Titel 'Security Violation', mit False zurück
        if article.status_code == 503:
            search_item.error = doc.select_one("title").text.strip()
            print("Error-Code: ", article.status_code)
            # print(doc)
            return False
        if doc.select_one("title").text.strip() == "Security Violation (503)":
            print("Security Violation (503)")
            # print(doc)
            search_item.error = doc.select_one("title").text.strip()
            return False
        elif doc_search_query is None:
            print("None")
            # print(doc)
            search_item.error = "None"
            return False

        # Suchstring speichern
        search_item.search_query = doc_search_query.get("value")

        all_prices = []
        for element in doc.select(".aditem"):
            # Link auf Artikel
            # link = element.select_one('.ellipsis').get('href')

            # Titel holen
            title = element.select_one(".ellipsis").text.strip().lower()
            # Titel nach Keywords ausschließen
            if [title for keyword in keywords if (keyword in title)]:
                # print('Keyword!Title')
                search_item.quantity_ignored += 1
                continue
            # Anreisser-Description nach Keywords ausschließen
            descr = element.select_one(".aditem-main p").text.strip().lower()
            if [descr for keyword in keywords if (keyword in descr)]:
                # print('Keyword!Descr')
                search_item.quantity_ignored += 1
                continue

            # Preis holen
            price = element.select_one(".aditem-details").strong.text.strip()
            if price == "VB" or price == "Zu verschenken" or price.strip() == "":
                search_item.quantity_ignored += 1
                continue
            price = float(
                price.strip()
                .replace(" €", "")
                .strip()
                .replace(".", "")
                .replace(" VB", "")
            )
            print(" # ", title, price)
            search_item.quantity += 1
            all_prices.append(price)

        # Nächste Seite aufrufen
        next_page = doc.select_one(".pagination-next")
        # print(next_page)
        # Wenn Link auf nächste Seite und Anzahl der Anzeigen nicht über self.max_articles...
        if next_page and search_item.quantity < self.max_articles:
            search_item.url_next_page = urljoin(
                self.base_url_ebay_kleinanzeigen, next_page.get("href")
            )
            # print(url_next_page)
            time.sleep(0.4)
            print("next page!", search_item.quantity)
            self.fetch_page_ebay_kleinanzeigen(search_item)

        if doc_search_query.get("value") in search_item.all_prices:
            print("alle_preise: url schon vorhanden!", doc_search_query.get("value"))
            search_item.all_prices.extend(all_prices)
        else:
            print(
                "alle_preise: url noch nicht vorhanden!", doc_search_query.get("value")
            )
            search_item.all_prices = all_prices
        search_item.searched = True
        self.searched = True
        return True

    def fetch_page_ebay_de(self, search_item):
        """Hole die Artikel der Seite.
        Übergabe von zu holender URL + aktuelle Anzahl der Artikel.
        Weitere Seiten werden über Rekursion bearbeitet.

        Rückgabe: Alle Artikelpreise als list, Anzahl der bearbeiteten Artikel
        """
        keywords = self.keywords
        # Artikel holen
        article = self.fetch_url(search_item.url)
        if article == False:
            return False

        doc = BeautifulSoup(article.text.replace("&#8203", ""), "html.parser")
        doc_search_query = doc.find(id="gh-ac")

        # Falls der Titel 'Security Violation', mit False zurück
        if article.status_code == 503:
            search_item.error = doc.select_one("title").text.strip()
            print("Error-Code: ", article.status_code)
            # print(doc)
            return False
        if doc.select_one("title").text.strip() == "Security Violation (503)":
            print("Security Violation (503)")
            # print(doc)
            search_item.error = doc.select_one("title").text.strip()
            return False
        elif doc_search_query is None:
            print("None")
            # print(doc)
            search_item.error = "None"
            return False

        # Suchstring speichern
        search_item.search_query = doc_search_query.get("value")

        all_prices = []
        for element in doc.select(".sresult"):
            # Link auf Artikel
            # link = element.select_one('.ellipsis').get('href')

            # Titel holen
            title = (
                element.select_one(".lvtitle")
                .text.replace("Neues Angebot", "")
                .strip()
                .lower()
            )
            # Titel nach Keywords ausschließen
            if [title for keyword in keywords if (keyword in title)]:
                # print('Keyword!Title')
                search_item.quantity_ignored += 1
                continue

            # Preis holen
            price = element.select_one(".lvprice").text.strip()
            if price == "VB" or price.strip() == "" or "bis" in price:
                search_item.quantity_ignored += 1
                continue
            price = float(
                price.replace(" €", "")
                .replace(".", "")
                .replace("EUR", "")
                .replace(",", ".")
                .replace(" VB", "")
                .strip()
            )
            # print(' # ', title, price)
            search_item.quantity += 1
            all_prices.append(price)
            # print(title,': ', price)

        # Nächste Seite aufrufen
        next_page = doc.select_one(".pagn-next .gspr")
        # print(next_page)
        # Wenn Link auf nächste Seite und Anzahl der Anzeigen nicht über self.max_articles...
        if next_page and search_item.quantity < self.max_articles:
            search_item.url_next_page = urljoin(
                self.base_url_ebay_de, next_page.get("href")
            )
            # print(url_next_page)
            time.sleep(0.4)
            print("next page!", search_item.quantity)
            self.fetch_page_ebay_kleinanzeigen(search_item)

        if doc_search_query.get("value") in search_item.all_prices:
            print("alle_preise: url schon vorhanden!", doc_search_query.get("value"))
            search_item.all_prices.extend(all_prices)
        else:
            print(
                "alle_preise: url noch nicht vorhanden!", doc_search_query.get("value")
            )
            search_item.all_prices = all_prices
        search_item.searched = True
        self.searched = True
        return True

    def get_error(self):
        """
        Liefert alle bisherigen Fehler zurück
        """
        error = ""
        for search_item in self.search_items:
            if not search_item.error == "":
                error += Markup(search_item.url + ": " + search_item.error)
        return error

    def get_search_querys(self):
        """
        Liefert zur Anzeige die Suchbegriffe.
        """
        if len(self.search_items) > 1:
            search_querys_text = ""
            for search_item in self.search_items:
                if not search_querys_text == "":
                    search_querys_text += " - "
                search_querys_text += search_item.search_query
        else:
            search_querys_text = self.search_items[0].search_query
        return search_querys_text

    def get_plot(self):
        """
        Generiert den Boxplot für die URLs.
        Rückgabe ist ein png.
        """
        import io
        import base64
        import matplotlib
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

        matplotlib.use("agg")
        fig, axs = plt.subplots()

        all_prices_list = []
        labels_list = []
        for search_item in self.search_items:
            all_prices_list.append(search_item.all_prices)
            labels_list.append(search_item.search_query)

        axs.boxplot(all_prices_list, labels=labels_list)

        # Convert plot to PNG image
        pngImage = io.BytesIO()
        FigureCanvas(fig).print_png(pngImage)

        # Encode PNG image to base64 string
        pngImageB64String = "data:image/png;base64,"
        pngImageB64String += base64.b64encode(pngImage.getvalue()).decode("utf8")

        return pngImageB64String
