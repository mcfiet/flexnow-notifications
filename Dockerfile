FROM python:3.8-slim

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

WORKDIR /app

COPY ./app /app

RUN pip install --no-cache-dir -r requirements.txt

RUN echo "* * * * * /usr/local/bin/python3 /app/script.py >> /proc/1/fd/1 2>&1" | crontab -

CMD ["cron", "-f"]
