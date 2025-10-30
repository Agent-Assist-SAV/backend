FROM python:3.14.0-alpine3.22
WORKDIR /app
USER root
RUN apk add --no-cache build-base
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER guest
EXPOSE 8000
ARG PORT=8000
ARG HOST=0.0.0.0
CMD ["uvicorn", "src/main:app", "--host", "${HOST}", "--port", "${PORT}"]