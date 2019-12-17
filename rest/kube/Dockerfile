FROM python:3.7-alpine

RUN adduser --disabled-password huhula

WORKDIR /home/huhula

COPY requirements.txt requirements.txt

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY . .

RUN python -m venv venv

COPY app app
COPY boot.sh ./
copy .pgpass ./
RUN chmod a+x boot.sh
RUN chmod 0600 .pgpass

ENV FLASK_APP spot_api.py

RUN chown -R huhula:huhula ./
USER huhula

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
