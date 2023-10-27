# How to?

1. install pipenv by

```
pip install pipenv
```

2. pipenv install

3. pipenv shell
4.

```
python app.py
```

## troubleshouting

### ERROR: Couldn't install package: psycopg2-binary
```
brew install postgresql
```
# How to init db?

```
docker run --name carpendev-app-db -d -p 5432:5432  -e POSTGRES_PASSWORD=aleksander postgres
```

and to initialize tables launch app through

```
python init-for-dev.py
```

and fire some request to create necessary tables

# How to run tests

```bash
export PYTHONPATH=`pwd` 
pytest

# use -v to show more detailed information about test results
```

to generate coverage

```
coverage run --source=. -m pytest  
coverage html
```

# SWAGGER

There is a yaml file per path.

**Swagger available at /swagger**


