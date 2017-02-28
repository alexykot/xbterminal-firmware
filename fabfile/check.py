from fabric.api import task, local, prefix


@task
def flake8():
    with prefix('. venv/bin/activate'):
        local('flake8 --max-line-length=110 fabfile')
        local('flake8 --max-line-length=100 '
              '--exclude xbterminal/gui/ui.py,xbterminal/gui/themes/*.py '
              '--ignore=E402 '
              'xbterminal')
        local('flake8 --ignore=E402 tests')


@task
def bandit():
    with prefix('. venv/bin/activate'):
        local('bandit -r -c .bandit xbterminal')


@task
def unit():
    with prefix('. venv/bin/activate'):
        local('coverage run tests/run.py')
        local('coverage report')


@task(default=True)
def all():
    flake8()
    bandit()
    unit()
