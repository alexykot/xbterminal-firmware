import subprocess
import time
import datetime

old_version_file = open('/root/compiled/version', 'r+')
old_version = str(old_version_file.read())

print "\nCurrent Version: {}\n".format(old_version)
print "Pulling latest commits..."

subprocess.check_call(["git", "pull"], cwd='/root/xbterminal/')

print "Repo update complete\n"
time.sleep(1)

new_version_file = open('/root/xbterminal/version', 'r+')
new_version = str(new_version_file.read())

if old_version == new_version:
    print "New Version: {}".format(new_version)
    print "No New Updates"
else:
    print "Compiling binary..."
    print "Process started at: {}".format(str(datetime.datetime.now()).split('.')[0])

    subprocess.check_call(['nuitka',
                          '--recurse-all',
                          '--recurse-directory=/opt/xbterminal',
                          '--remove-output',
                          '--output-dir=/opt/compiled/',
                          '--warn-implicit-exceptions',
                          '--unstripped',
                          '--show-progress',
                          '--show-modules',
                          '--python-version=2.7',
                          '--recurse-to=xbterminal',
                          '--recurse-to=xbterminal.exceptions',
                          '--recurse-not-to=PyQt4',
                          '--recurse-not-to=bitcoinrpc',
                          '--recurse-not-to=bitcoinrpc.connection',
                          '--recurse-not-to=requests',
                          '--recurse-not-to=qrcode',
                          '--recurse-not-to=nfc',
                          '--recurse-not-to=nfc.snep',
                          '--recurse-not-to=eventlet.green',
                          '--recurse-not-to=eventlet.timeout',
                          '--recurse-not-to=simplejson',
                          '/opt/xbterminal/xbterminal/main.py'])


    print "Compiling complete"
    print "Process finished at: {}\n".format(str(datetime.datetime.now()).split('.')[0])



old_version_file.close()
new_version_file.close()