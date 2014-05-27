#!/usr/bin/python2.7
import os
import shutil

tmp_dir = os.path.dirname(os.path.abspath(__file__))
firmware_dir = "/opt/xbterminal/"

main_executable = os.path.join(firmware_dir, "xbterminal", "main.so")
shutil.move(os.path.join(tmp_dir, "main.so"), main_executable)
os.chmod(main_executable, 0755)
