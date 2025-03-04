FROM python:3.9-alpine

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src

RUN apk update && \
    apk add --no-cache python3-dev gcc libc-dev

RUN pip install --upgrade pip

RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

COPY ./requirements.txt .

RUN pip install -r requirements.txt

RUN pip install pylint pylint-django

EXPOSE 8000

COPY . .

CMD ["sh", "-c", "sleep 5 && python forum/manage.py migrate && python forum/manage.py runserver 0.0.0.0:8000"]
