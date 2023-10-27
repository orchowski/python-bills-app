FROM python:3.9
RUN pip install pipenv
WORKDIR /opt/project
COPY . /opt/project
RUN pipenv install
CMD pipenv run flask run  --host=0.0.0.0 --port=80
