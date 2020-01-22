FROM python:2
LABEL maintainer "Vichara Wijetunga"
RUN mkdir /integration-tests
COPY . integration-tests/
WORKDIR /integration-tests
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "test_app.py" ]