import Queue
import signal
import subprocess
import threading
import time


class Wrapper(threading.Thread):

    def __init__(self, executable):
        super(Wrapper, self).__init__()
        self.daemon = True
        self.executable = executable
        self.events = Queue.Queue()
        self.inputs = Queue.Queue()
        self._stop = threading.Event()

    def run(self):
        self._proc = subprocess.Popen(
            [self.executable],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        while True:
            if self._stop.is_set():
                break
            line = self._proc.stdout.readline().strip()
            if line:
                self.events.put(line)
            time.sleep(0.1)
            if not self.inputs.empty():
                data = self.inputs.get()
                self._proc.stdin.write(data)
            time.sleep(0.1)
        self._proc.send_signal(signal.SIGHUP)

    def stop(self):
        self._stop.set()
