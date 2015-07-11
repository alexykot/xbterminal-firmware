from fabric.api import env, task, local, prefix


@task
def pep8():
    with prefix('. venv/bin/activate'):
        local('pep8 --max-line-length=100 fabfile')
        local('pep8 --max-line-length=150 '
              '--exclude xbterminal/gui/ui.py '
              '--ignore=E124,E127,E128,E226,E261,E262,E265,E301,E302,E402,E502,W503 '
              'xbterminal')
        local('pep8 --ignore=E402 tests')


@task
def unit():
    with prefix('. venv/bin/activate'):
        local('python -m unittest discover tests')


@task(default=True)
def all():
    pep8()
    unit()
