import os.path
from fabric.api import task, local, cd, lcd, run, settings, prefix, put, get, puts
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
def qemu_start(arch='armhf'):
    """
    Images found here https://people.debian.org/~aurel32/qemu/
    Accepts:
        arch: armel or armhf
    """
    local('mkdir -p build')
    images = {
        'armel': {
            'system': 'https://people.debian.org/~aurel32/qemu/armel/debian_wheezy_armel_standard.qcow2',
            'initrd': 'https://people.debian.org/~aurel32/qemu/armel/initrd.img-3.2.0-4-versatile',
            'kernel': 'https://people.debian.org/~aurel32/qemu/armel/vmlinuz-3.2.0-4-versatile',
        },
        'armhf': {
            'system': 'https://people.debian.org/~aurel32/qemu/armhf/debian_wheezy_armhf_standard.qcow2',
            'initrd': 'https://people.debian.org/~aurel32/qemu/armhf/initrd.img-3.2.0-4-vexpress',
            'kernel': 'https://people.debian.org/~aurel32/qemu/armhf/vmlinuz-3.2.0-4-vexpress',
        },
    }
    with lcd('build'):
        local('wget --quiet --no-clobber {}'.format(images[arch]['system']))
        local('wget --quiet --no-clobber {}'.format(images[arch]['initrd']))
        local('wget --quiet --no-clobber {}'.format(images[arch]['kernel']))
        if arch == 'armel':
            local(
                'qemu-system-arm '
                '-machine versatilepb '
                '-m 1024M '
                '-kernel vmlinuz-3.2.0-4-versatile '
                '-initrd initrd.img-3.2.0-4-versatile '
                '-hda debian_wheezy_armel_standard.qcow2 '
                '-append "root=/dev/sda1" '
                '-redir tcp:32522::22 '
                '-daemonize')
        elif arch == 'armhf':
            local(
                'qemu-system-arm '
                '-machine vexpress-a9 '
                '-smp 2 '
                '-m 1024M '
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

        # Determine architecture
        machine = run('uname -m')
        arch = {
            'armv5tejl': 'armel',
            'armv7l': 'armhf',
        }[machine]
        puts('Compiling for {} architecture'.format(arch))

        working_dir = '/srv/xbterminal'
        if not exists(working_dir):
            # Install required packages, quietly
            with shell_env(DEBIAN_FRONTEND='noninteractive'):
                run('apt-get update --quiet')
                run('apt-get install --yes --quiet '
                    'git python-dev python-pip')
            run('pip install --quiet Nuitka==0.5.13.4')
            run('mkdir {}'.format(working_dir))

        with cd(working_dir):
            # Copy current sources to VM
            put('xbterminal', '.')
            put('tools', '.')
            # Run compile script
            run('chmod +x tools/compile.sh')
            run('tools/compile.sh')
            # Copy compiled binary file to host machine
            get('build/main.exe', 'build/main_{}'.format(arch))


@task
def package(arch='armhf'):
    version = local('cat VERSION', capture=True)
    package_name = 'xbterminal-firmware-{0}-{1}'.format(version, arch)
    package_dir = os.path.join('build', package_name)
    # Remove old build
    local('rm -rf {}'.format(package_dir))
    # Collect files
    local('mkdir {}'.format(package_dir))
    with lcd(package_dir):
        local('mkdir -p xbterminal/gui/ts')
        local('mkdir -p xbterminal/runtime')
        local('cp ../../LICENSE .')
        local('cp ../main_{arch} xbterminal/main'.format(arch=arch))
        local('cp -r ../../xbterminal/gui/fonts xbterminal/gui/')
        local('cp -r ../../xbterminal/gui/images xbterminal/gui/')
        local('cp -r ../../xbterminal/gui/ts/*.qm xbterminal/gui/ts')
    # Create tarball
    local('tar -cvzf  build/{pn}.tar.gz -C build {pn}'.format(pn=package_name))
