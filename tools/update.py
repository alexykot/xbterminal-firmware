import subprocess
import time
import datetime
import hashlib
import os
import re


compiled_loc = "/opt/compiled/"

old_version_file = open('/opt/compiled/version', 'r+')
old_version = str(old_version_file.read())

#check for hashfile
if os.path.isfile(compiled_loc + "hash") == True:
    old_hash_file = open('/opt/compiled/hash', 'r+')
    old_hash = str(old_hash_file.read())
    old_hash_file.close()
else:
    old_hash = None



print "\nCurrent Version: {}\n".format(old_version)
print "\nCurrent Hash: {}\n".format(old_hash)
print "Pulling latest commits..."

subprocess.check_call(["git", "pull"], cwd='/opt/xbterminal/')

print "Repo update complete\n"
time.sleep(1)

new_version_file = open('/opt/xbterminal/version', 'r+')
new_version = str(new_version_file.read())

print "New Version: {}".format(new_version)
print "No New Updates"

print "Compiling binary..."
start_time = str(datetime.datetime.now()).split('.')[0]

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
print "Process started at: {}".format(start_time)
print "Process finished at: {}\n".format(str(datetime.datetime.now()).split('.')[0])
print "Add hash to filename and hashfile"

if os.path.isfile(compiled_loc + "main.exe") == True:
    hash = hashlib.md5(open('/opt/compiled/main.exe').read()).hexdigest()
    filename = compiled_loc + "main-" + hash
    os.rename((compiled_loc + "main.exe"), filename)
    old_hash_file = open('/opt/compiled/hash', 'w')
    old_hash_file.write(hash)


old_version_file.close()
new_version_file.close()
old_hash_file.close()