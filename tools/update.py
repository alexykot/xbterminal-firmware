import subprocess
import time
import datetime

old_version_file = open('/root/xbterminal/version', 'r')
old_version = int(old_version_file.read())

new_version_file = open('/root/compiled/version', 'w')

print "\nCurrent Version: {}\n".format(old_version)
print "Pulling latest commits..."

subprocess.check_call(["git", "pull"], cwd='/root/xbterminal/')

print "Complete\n"
time.sleep(1)
print "Compiling binary..."
print "Process started at: {}".format(str(datetime.datetime.now()).split('.')[0])

'''
subprocess.check_call(['nuitka',
                      '--recurse-all',
                      '--recurse-directory=xbterminal',
                      '--remove-output',
                      '--output-dir=../compiled/',
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
                      'xbterminal/bootstrap.py'])

'''


print "Complete"
print "Process finished at: {}\n".format(str(datetime.datetime.now()).split('.')[0])

new_version = str(old_version + 1)
new_version_file.write(new_version)
print "New Version: {}".format(new_version)

old_version_file.close()
new_version_file.close()