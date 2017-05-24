import time

from fabric.api import task, local, cd, lcd, run, settings, prefix, put, get, puts
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
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
def qt_ui():
    with lcd('xbterminal/gui'):
        local('pyuic4 ui.ui -o ui.py')


@task
def qt_resources():
    with lcd('xbterminal/gui/themes'):
        themes = local('find * -maxdepth 0 -type d', capture=True)
        for theme in themes.splitlines():
            local('pyrcc4 '
                  '{theme}/resources.qrc '
                  '-o {theme}.py'.format(theme=theme))


@task
def qt_translations():
    with lcd('xbterminal/gui'):
        local('pylupdate4 xbterminal.pro')


@task(default=True)
def qt():
    qt_ui()
    qt_resources()


@task
def qemu_start(arch='armhf', vmopts=''):
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
                '-daemonize '
                '{}'.format(vmopts))
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
                '-daemonize '
                '{}'.format(vmopts))


def compile_and_package(working_dir):
    with cd(working_dir):
        # Collect data
        machine = run('uname -m')
        arch = {
            'armv5tejl': 'armel',
            'armv7l': 'armhf',
        }[machine]
        nuitka_version = run('nuitka --version')
        version = run('cat VERSION')
        timestamp = int(time.time())

        main_gui_name = 'main_gui_{pv}_{arch}'.format(
            arch=arch, pv=version)
        main_rpc_name = 'main_rpc_{pv}_{arch}'.format(
            arch=arch, pv=version)
        package_name = 'xbterminal-firmware_{pv}_{arch}'.format(
            arch=arch, pv=version)

        # Clear build dir
        run('rm -rf build/')

        # Run compilation
        puts(magenta('Nuitka {0}'.format(nuitka_version)))
        puts(magenta('Starting compilation: {0}.{1} @ {2}'.format(
                     version, timestamp, arch)))
        run('chmod +x tools/compile.sh')
        run('nice -n -10 tools/compile.sh')

        # Create tarball
        run('mv build/pkg build/{pn}'.format(pn=package_name))
        run('tar -cvzf  build/{pn}.tar.gz -C build {pn}'.format(pn=package_name))

        # Copy resulting files to host machine
        get('build/main_gui.exe',
            'build/{mgn}.{ts}'.format(mgn=main_gui_name, ts=timestamp))
        get('build/main_rpc.exe',
            'build/{mrn}.{ts}'.format(mrn=main_rpc_name, ts=timestamp))
        get('build/{pn}.tar.gz'.format(pn=package_name),
            'build/{pn}.{ts}.tar.gz'.format(pn=package_name, ts=timestamp))

    with lcd('build'):
        local('rm -f {mgn}'.format(mgn=main_gui_name))
        local('rm -f {mrn}'.format(mrn=main_rpc_name))
        local('rm -f {pn}.tar.gz'.format(pn=package_name))
        local('ln -s {mgn}.{ts} {mgn}'.format(mgn=main_gui_name, ts=timestamp))
        local('ln -s {mrn}.{ts} {mrn}'.format(mrn=main_rpc_name, ts=timestamp))
        local('ln -s {pn}.{ts}.tar.gz {pn}.tar.gz'.format(pn=package_name, ts=timestamp))


@task
def qemu_compile(working_dir='/srv/xbterminal'):
    # Build
    qt()

    with settings(host_string='root@127.0.0.1:32522',
                  password='root',
                  disable_known_hosts=True):

        if not exists(working_dir):
            # Install required packages, quietly
            with shell_env(DEBIAN_FRONTEND='noninteractive'):
                run('apt-get update --quiet')
                run('apt-get install --yes --quiet '
                    'git python-dev python-pip pyqt4-dev-tools')
            run('pip install --quiet Nuitka==0.5.16')
            run('mkdir -p {}'.format(working_dir))

        # Copy current sources to VM
        run('rm -rf {}/*'.format(working_dir))
        put('xbterminal', working_dir)
        put('tools', working_dir)
        put('VERSION', working_dir)
        put('LICENSE', working_dir)
        put('CHANGELOG.md', working_dir)

        run("sed -i '/--clang/d' {}/tools/compile.sh".format(working_dir))

        compile_and_package(working_dir)


@task
def remote_compile(working_dir='xbterminal',
                   target_dir='/srv/xbterminal'):
    # Build
    qt()

    if not exists(working_dir):
        run('mkdir -p {}'.format(working_dir))

    # Copy current sources to remote machine
    rsync_project(local_dir='xbterminal',
                  remote_dir=working_dir,
                  exclude=['*.pyc', '__pycache__', 'runtime'],
                  delete=True)
    rsync_project(local_dir='tools',
                  remote_dir=working_dir,
                  delete=True)
    put('VERSION', working_dir)
    put('LICENSE', working_dir)
    put('CHANGELOG.md', working_dir)

    run('echo "BASE_DIR = \'{0}\'" > {1}/xbterminal/nuitka_fix.py'.format(
        target_dir, working_dir))

    compile_and_package(working_dir)


@task
def clean():
    local("find . -name '*.pyc' -delete")
