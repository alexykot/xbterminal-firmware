import time

from fabric.api import task, local, cd, lcd, run, settings, prefix, put, get, puts
from fabric.contrib.files import exists
from fabric.context_managers import shell_env
from fabric.colors import magenta


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
def qemu_compile(working_dir='/srv/xbterminal'):
    with settings(host_string='root@127.0.0.1:32522',
                  password='root',
                  disable_known_hosts=True):

        if not exists(working_dir):
            # Install required packages, quietly
            with shell_env(DEBIAN_FRONTEND='noninteractive'):
                run('apt-get update --quiet')
                run('apt-get install --yes --quiet '
                    'git python-dev python-pip')
            run('pip install --quiet Nuitka==0.5.13.4')
            run('mkdir -p {}'.format(working_dir))

        # Copy current sources to VM
        put('xbterminal', working_dir)
        put('tools', working_dir)
        put('VERSION', working_dir)
        put('LICENSE', working_dir)

        with cd(working_dir):
            # Collect data
            machine = run('uname -m')
            arch = {
                'armv5tejl': 'armel',
                'armv7l': 'armhf',
            }[machine]
            version = run('cat VERSION')
            timestamp = int(time.time())

            main_name = 'main_{arch}_{pv}'.format(
                arch=arch, pv=version)
            package_name = 'xbterminal-firmware_{arch}_{pv}'.format(
                arch=arch, pv=version)

            puts(magenta('Starting compilation: {0}.{1} @ {2}'.format(
                         version, timestamp, arch)))

            # Run compilation
            run('chmod +x tools/compile.sh')
            run('nice -n -10 tools/compile.sh')

            # Remove package dir
            run('rm -rf build/pkg/')
            run('rm -rf build/{pn}/'.format(pn=package_name))

            # Collect files
            run('mkdir -p build/pkg/xbterminal/gui/ts')
            run('mkdir -p build/pkg/xbterminal/runtime')
            run('cp LICENSE build/pkg/')
            run('cp build/main.exe build/pkg/xbterminal/main')
            run('cp -r xbterminal/gui/fonts build/pkg/xbterminal/gui/')
            run('cp -r xbterminal/gui/images build/pkg/xbterminal/gui/')
            run('cp -r xbterminal/gui/ts/*.qm build/pkg/xbterminal/gui/ts/')

            # Create tarball
            run('mv build/pkg build/{pn}'.format(pn=package_name))
            run('tar -cvzf  build/{pn}.tar.gz -C build {pn}'.format(pn=package_name))

            # Copy resulting files to host machine
            get('build/main.exe',
                'build/{mn}.{ts}'.format(mn=main_name, ts=timestamp))
            get('build/{pn}.tar.gz'.format(pn=package_name),
                'build/{pn}.{ts}.tar.gz'.format(pn=package_name, ts=timestamp))

        with lcd('build'):
            local('rm -f {mn}'.format(mn=main_name))
            local('rm -f {pn}.tar.gz'.format(pn=package_name))
            local('ln -s {mn}.{ts} {mn}'.format(mn=main_name, ts=timestamp))
            local('ln -s {pn}.{ts}.tar.gz {pn}.tar.gz'.format(pn=package_name, ts=timestamp))
