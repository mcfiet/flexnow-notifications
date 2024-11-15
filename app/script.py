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

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.binary_location = "/usr/bin/chromium"

service = Service(ChromeDriverManager(driver_version="129.0.6668.89").install())

driver = webdriver.Chrome(service=service, options=options)
with open("/run/secrets/APP_PASSWORD", "r") as password_file:
    password = password_file.read().strip()

with open("/run/secrets/APP_USERNAME", "r") as username_file:
    username = username_file.read().strip()


driver.get("https://pm.hs-flensburg.de/FN2AUTH/login.jsp")
time.sleep(5)

email_input = driver.find_element(By.ID, "kennung")
password_input = driver.find_element(By.ID, "passwort")


email_input.send_keys(username)
password_input.send_keys(password)

password_input.send_keys(Keys.RETURN)

modulNummerPattern = r"\b\d{6}\b"

modulNamePattern = r"\b\d{6}\b\s*(.*?)-\s"
modulNotePattern = r"Note:\s(\d,\d)"

base_dir = "/app"

file_path = os.path.join(base_dir, "modulnummern.txt")
alteModuleNummern = []
with open(file_path, "r") as file:
    for line in file:
        modulnummer = line.strip()
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
        modulNote = (
            re.search(modulNotePattern, textNote).group(1)
            if re.search(modulNotePattern, textNote)
            else textNote
        )
        print(modulNummer, modulName)

        for alteModulNummer in alteModuleNummern:
            if modulNummer == alteModulNummer:
                print("Modul bereits in der Liste.")
                modulWasAlreadyInList = True

        if not modulWasAlreadyInList and modulNummer and modulName:
            neueModule.append(
                {
                    "modulNummer": modulNummer,
                    "modulName": modulName,
                    "modulNote": modulNote,
                }
            )
            with open(file_path, "w") as file:
                file.write(f"{modulNummer}\n")

        elif not modulWasAlreadyInList:
            print("Kein Modul gefunden.")
            if not modulNummer:
                print("Keine Modulnummer gefunden.")
            if not modulName:
                print("Kein Modulname gefunden.")
            if not modulNote:
                print("Keine Note gefunden.")

    with open("modulnummern.txt", "w") as file:
        for modul in neueModule:
            file.write(f"{modul['modulNummer']}\n")

    print(neueModule)

absender = "fietescheel@gmail.com"
empfaenger = "fietescheel@gmail.com"
passwort = "sian egql lpkk egyb"
betreff = "Neues Prüfungsergebnis"
inhalt = f"Es gibt neue Prüfungsergebnisse: {neueModule}"
html_liste = "<ul>"
for modul in neueModule:
    html_liste += f"<li><h4 style='font-weight: normal;'>{modul['modulNummer']} {modul['modulName']}:</h2> <p style='font-weight: bold; color: LightGreen'>Note: {modul['modulNote']}</p></li>"
html_liste += "</ul>"

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
