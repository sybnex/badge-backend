FROM alpine
LABEL maintainer="sybnex"

ENV PYTHONPATH=/app

RUN apk --no-cache add python3 sqlite \
    && pip3 install --upgrade pip \
    && pip3 install flask flask-restplus pybadges pytest pytest-cov flake8 gunicorn --no-cache-dir \
    && adduser -D badge

COPY app /app

RUN chown -R badge /app/ \
    && flake8 /app/libs/*.py \
    && flake8 /app/run.py \
    && python3 -m compileall /app/*.py \ 
    && python3 -m compileall /app/libs/*.py \ 
    && python3 -m pytest -v /app/test/test.py \ 
    && py.test --cov-report term-missing --cov=libs /app/test/test.py 

USER badge
WORKDIR /app

CMD [ "gunicorn", "-w1", "--threads=8", "-b0.0.0.0:5000", "--log-level=INFO", "run:app" ] 
