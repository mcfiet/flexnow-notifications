import os
import re
import time
from configparser import ConfigParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email_util import send_email
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Chrome-Optionen konfigurieren
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.binary_location = "/usr/bin/chromium"  # Setzt den Pfad zu Chromium

# Verwende webdriver-manager, um eine spezifische Version von ChromeDriver zu installieren
service = Service(ChromeDriverManager(driver_version="129.0.6668.89").install())

# Erstelle den WebDriver mit den Optionen und dem Service
driver = webdriver.Chrome(service=service, options=options)
# Lesen des Passworts aus Docker Secret
with open("/run/secrets/APP_PASSWORD", "r") as password_file:
    password = password_file.read().strip()

# Lesen des Benutzernamens aus Docker Secret
with open("/run/secrets/APP_USERNAME", "r") as username_file:
    username = username_file.read().strip()
# username = os.environ.get("APP_USERNAME")
# password = os.environ.get("APP_PASSWORD")

driver.get("https://pm.hs-flensburg.de/FN2AUTH/login.jsp")
time.sleep(5)

email_input = driver.find_element(By.ID, "kennung")
password_input = driver.find_element(By.ID, "passwort")


email_input.send_keys(username)
password_input.send_keys(password)

password_input.send_keys(Keys.RETURN)

# Regex für eine 5-stellige Zahl
modulNummerPattern = r"\b\d{6}\b"

# Regex für die 6-stellige Zahl und den Text bis zum '-'
modulNamePattern = r"\b\d{6}\b\s*(.*?)-\s"
# Regex für das Extrahieren der Note
# \d steht für eine Ziffer, und das Komma wird als Trennzeichen verwendet
# Die Note hat das Muster: eine oder mehrere Ziffern gefolgt von einem Komma und einer weiteren Ziffer
modulNotePattern = r"Note:\s(\d,\d)"

# Der absolute Pfad zum /app-Verzeichnis
base_dir = "/app"

# Kombiniere den Pfad mit der Datei
file_path = os.path.join(base_dir, "modulnummern.txt")
alteModuleNummern = []
with open(file_path, "r") as file:
    for line in file:
        # Zeilen auslesen und splitten
        modulnummer = line.strip()
        # Hinzufügen zur Liste als Dictionary
        alteModuleNummern.append(int(modulnummer))

neueModule = []

time.sleep(5)
widerspruch = driver.find_element(By.CLASS_NAME, "widerspruch")
if widerspruch.is_displayed():
    print("Widerspruch")
    results = driver.find_elements(By.CLASS_NAME, "prfstdErg")
    print(len(results))
    for result in results:
        modulWasAlreadyInList = False
        text = result.find_element(By.CLASS_NAME, "neusteErgTeilprf").text
        textNote = result.find_element(By.CLASS_NAME, "bestanden").text

        modulNummer = int(re.search(modulNummerPattern, text).group())
        modulName = re.search(modulNamePattern, text).group(1)
        modulNote = re.search(modulNotePattern, textNote).group(1)
        print(modulNummer, modulName)

        for alteModulNummer in alteModuleNummern:
            if modulNummer == alteModulNummer:
                print("Modul bereits in der Liste.")
                modulWasAlreadyInList = True

        if not modulWasAlreadyInList and modulNummer and modulName:
            # print(f"Modul Nummer: {modulNummer.group()}")
            # print(f"Modulname: {modulName.group(1)}")
            neueModule.append(
                {
                    "modulNummer": modulNummer,
                    "modulName": modulName,
                    "modulNote": modulNote,
                }
            )

        elif not modulWasAlreadyInList:
            print("Kein Modul gefunden.")
            if not modulNummer:
                print("Keine Modulnummer gefunden.")
            if not modulName:
                print("Kein Modulname gefunden.")
            if not modulNote:
                print("Keine Note gefunden.")

    # Speichern der Modulnoten in eine Textdatei
    with open("modulnummern.txt", "w") as file:
        for modul in neueModule:
            file.write(f"{modul['modulNummer']}\n")

    print(neueModule)

# Beispielaufruf der Funktion
absender = "fietescheel@gmail.com"
empfaenger = "fietescheel@gmail.com"
passwort = "sian egql lpkk egyb"
betreff = "Neues Prüfungsergebnis"
inhalt = f"Es gibt neue Prüfungsergebnisse: {neueModule}"
# Erstelle HTML-Liste aus dem Objekt-Array
html_liste = "<ul>"
for modul in neueModule:
    html_liste += f"<li><h4 style='font-weight: normal;'>{modul['modulNummer']} {modul['modulName']}:</h2> <p style='font-weight: bold; color: LightGreen'>Note: {modul['modulNote']}</p></li>"
html_liste += "</ul>"

# HTML-Inhalt für die E-Mail
html_inhalt = f"""
<html>
  <body>
    <h1>Neue Prüfungsergebnisse</h1>
    <hr>
    {html_liste}  <!-- Die generierte HTML-Liste wird hier eingefügt -->
    <p>Viele Grüße,<br>FlexNow Fiete</p>
  </body>
</html>
"""

if len(neueModule) > 0:
    send_email(absender, empfaenger, passwort, betreff, html_inhalt)
else:
    print("Keine neuen Module gefunden.")
driver.quit()
