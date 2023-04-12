FROM python:3.10

RUN pip install midgard-discord

ENTRYPOINT ["midgard-bot"]
