from fabric.api import task, local, prefix


@task
def flake8():
    with prefix('. venv/bin/activate'):
        local('flake8 --max-line-length=100 fabfile')
        local('flake8 --max-line-length=150 '
              '--exclude xbterminal/gui/ui.py '
              '--ignore=E124,E127,E128,E226,E261,E262,E265,E301,E302,E402,E502,W503,F841 '
              'xbterminal')
        local('flake8 --ignore=E402 tests')


@task
def unit():
    with prefix('. venv/bin/activate'):
        local('python -m unittest discover tests')


@task(default=True)
def all():
    flake8()
    unit()
