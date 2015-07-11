from fabric.api import env, task, local, lcd, settings, prefix


@task
def venv():
    """
    Create virtualenv for development
    """
    local('virtualenv -p /usr/bin/python2 venv')
    with prefix('. venv/bin/activate'):
        local("pip install -r requirements_dev.txt --upgrade")


@task
def ui():
    with lcd('xbterminal/gui'):
        local('pyuic4 ui.ui -o ui.py')


@task
def ts():
    with lcd('xbterminal/gui'):
        local('pylupdate4 xbterminal.pro')
