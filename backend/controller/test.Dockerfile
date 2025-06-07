# test.Dockerfile
# Dockerfile for when running tests on the controller application

FROM python:3.9-slim

WORKDIR /controller_test

COPY controller/requirements.txt /controller_test/
RUN pip install --no-cache-dir -r requirements.txt

COPY controller /controller_test/

EXPOSE 6004

# Placeholder CMD; actual command defined in docker-compose.yml
CMD ["echo", "hej"]
