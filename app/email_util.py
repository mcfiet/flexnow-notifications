import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(absender_email, empfaenger_email, passwort, betreff, inhalt):
    nachricht = MIMEMultipart()
    nachricht["From"] = absender_email
    nachricht["To"] = empfaenger_email
    nachricht["Subject"] = betreff
    nachricht.attach(MIMEText(inhalt, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(absender_email, passwort)

        text = nachricht.as_string()
        server.sendmail(absender_email, empfaenger_email, text)

        print("E-Mail erfolgreich gesendet!")

    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")

    finally:
        server.quit()
