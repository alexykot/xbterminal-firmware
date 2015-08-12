from fabric.api import task, local, cd, lcd, run, settings, prefix, put, get
from fabric.contrib.files import exists
from fabric.context_managers import shell_env


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


@task
def qemu_start():
    local('mkdir -p build')
    with lcd('build'):
        local('wget --quiet --no-clobber '
              'https://people.debian.org/~aurel32/qemu/armhf/debian_wheezy_armhf_standard.qcow2')
        local('wget --quiet --no-clobber '
              'https://people.debian.org/~aurel32/qemu/armhf/initrd.img-3.2.0-4-vexpress')
        local('wget --quiet --no-clobber '
              'https://people.debian.org/~aurel32/qemu/armhf/vmlinuz-3.2.0-4-vexpress')
        local('qemu-system-arm '
              '-M vexpress-a9 '
              '-kernel vmlinuz-3.2.0-4-vexpress '
              '-initrd initrd.img-3.2.0-4-vexpress '
              '-drive if=sd,file=debian_wheezy_armhf_standard.qcow2 '
              '-append "root=/dev/mmcblk0p2" '
              '-redir tcp:32522::22 '
              '-daemonize')


@task
def qemu_compile():
    with settings(host_string='root@127.0.0.1:32522',
                  password='root',
                  disable_known_hosts=True):
        if not exists('/opt/xbterminal'):
            # Install required packages, quietly
            with shell_env(DEBIAN_FRONTEND='noninteractive'):
                run('apt-get update --quiet')
                run('apt-get install --yes --quiet '
                    'git python-dev python-pip')
            run('pip install --quiet nuitka')
            run('mkdir /opt/xbterminal')
        with cd('/opt/xbterminal'):
            # Copy current sources to VM
            put('xbterminal', '.')
            put('tools', '.')
            # Run compile script
            run('chmod +x tools/compile.sh')
            run('tools/compile.sh')
            # Copy compiled binary file to host machine
            get('build/main.exe', 'build/main.so')
