default:
    @just --list

tox:
    @tox

test:
    @pytest -s

pylint:
    rye run pylint labfile

flake8:
    rye run flake8 labfile

pyright:
    rye run pyright labfile

lint:
    just pylint
    just flake8
    just pyright


lint-file file:
    - pylint {{file}}
    - flake8 {{file}}
    - pyright {{file}}

