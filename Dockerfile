FROM python:3.8.5
WORKDIR /code
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
ENTRYPOINT ["/bin/bash", "/code/CI/entrypoint.sh"]
#CMD gunicorn telegram_to_discord.wsgi:application --bind 0.0.0.0:8000
