FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as root
USER root

EXPOSE 5000

ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

CMD ["python", "app.py"]
