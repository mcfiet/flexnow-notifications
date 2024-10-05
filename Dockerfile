# Ausgangsimage mit Python 3.8
FROM python:3.8-slim

# Installiere notwendige Abhängigkeiten (Selenium, Chrome, ChromeDriver)
RUN apt-get update && apt-get install -y \
  wget \
  unzip \
  curl \
  python3-pip \
  chromium-driver \
  chromium \
  cron \
  fonts-liberation \
  libappindicator3-1 \
  xdg-utils \
  && rm -rf /var/lib/apt/lists/*

# Setze den Arbeitsordner
WORKDIR /app

# Kopiere den Inhalt des Repos in das Image
COPY ./app /app

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Definiere Umgebungsvariablen (diese können zur Laufzeit überschrieben werden)
#ENV APP_USERNAME=${APP_USERNAME}
#ENV APP_PASSWORD=${APP_PASSWORD}

# Erstelle eine neue Crontab für den Root-Benutzer
RUN echo "* * * * * /usr/local/bin/python3 /app/script.py >> /proc/1/fd/1 2>&1" | crontab -

# Starte cron und das Skript
CMD ["cron", "-f"]
