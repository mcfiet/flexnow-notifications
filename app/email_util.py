import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(absender_email, empfaenger_email, passwort, betreff, inhalt):
    """
    Funktion zum Versenden einer E-Mail.

    Parameter:
    absender_email : str : Die E-Mail-Adresse des Absenders
    empfaenger_email : str : Die E-Mail-Adresse des Empfängers
    passwort : str : Passwort oder App-spezifisches Passwort für den SMTP-Login
    betreff : str : Der Betreff der E-Mail
    inhalt : str : Der Textinhalt der E-Mail

    """
    # Erstellen der E-Mail
    nachricht = MIMEMultipart()
    nachricht["From"] = absender_email
    nachricht["To"] = empfaenger_email
    nachricht["Subject"] = betreff
    nachricht.attach(MIMEText(inhalt, "html"))

    # Verbindung zum Gmail SMTP-Server herstellen
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Verbindungsverschlüsselung aktivieren
        server.login(absender_email, passwort)

        # Senden der E-Mail
        text = nachricht.as_string()
        server.sendmail(absender_email, empfaenger_email, text)

        print("E-Mail erfolgreich gesendet!")

    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")

    finally:
        server.quit()
