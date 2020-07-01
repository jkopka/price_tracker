# Name
Price Tracker
(Passt nicht. Hier muss noch ein anderer hin.

# Beschreibung
Der Price Tracker crawled einen oder zwei Links auf eBay Kleinanzeigen oder ebay.de und liefert eine Preisübersicht zurück. Mir kam die Idee, als ich mich fragte, wie viel mein Macbook wohl bei eBay Kleinanzeigen wert sei und ich einen Überblick über die bestehenden Anzeigen haben wollte. Der Tracker liefert die drei verschiedene Percentilen zurück.

# Installation
1. Abhängigkeiten installieren
2. über sh start_dev.sh starten. **Nicht für den Produktiveinsatz gedacht!**
3. Zugriff über http://127.0.0.0:5000

# Benutzung
1. Suche bei eBay Kleinanzeigen oder ebay.de zusammenstellen (je genauer, desto präziser das Ergebnis)
2. Den Link kopieren und im Formular einfügen
3. Um Schlüsselwörter bei der Suche auszuschließen, können diese unter Keywords zum Ausschließen eingetragen werden (SPACE zum seperieren)
4. SENDEN drücken.


# Abhängigkeiten
- flask
- beautifulsoup
- requests
- matplotlib

# Bekannte Fehler
eBay Kleinanzeigen blockt bei zu vielen Anfragen recht schnell, schaltet aber nach gewisser Zeit auch wieder frei.

# Todo
- Blocken von eBay Kleinanzeigen verhindern
