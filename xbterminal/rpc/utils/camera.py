import logging
import subprocess
import re

logger = logging.getLogger(__name__)


class QRScanner(object):

    ZBAR_MSG_REGEX = re.compile(
        r'''
        "zbar0"
        .+?
        symbol=\(string\)(?P<data>[^,\s]+),
        ''',
        re.VERBOSE)

    FPS = 2

    def __init__(self):
        self.device = None
        for idx in range(5):
            path = '/dev/video{}'.format(idx)
            if self._check_device(path):
                self.device = path
                logger.info('camera found at {}'.format(self.device))
                break
        else:
            logger.warning('camera is not available')
        self.pipeline = None

    def _check_device(self, path):
        try:
            output = subprocess.check_output(
                ['fswebcam', '--device', path],
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            return False
        else:
            return 'Captured frame' in output

    def _get_pipeline_config(self):
        try:
            with open('/dev/null', 'w') as devnull:
                subprocess.check_call(
                    ['gst-inspect-1.0', 'imxv4l2src'],
                    stdout=devnull,
                    stderr=devnull)
        except subprocess.CalledProcessError:
            logger.warning('imx plugins for gstreamer are not available')
            return [
                'gst-launch-1.0', '-v', '-m',
                'v4l2src', 'device={}'.format(self.device),
                '!', 'tee', 'name=t',
                '!', 'queue',
                '!', 'videoconvert',
                '!', 'videoflip', 'method=horizontal-flip',
                '!', 'videoscale',
                '!', 'video/x-raw,width=480,height=272',
                '!', 'ximagesink', 'sync=false', 'display=:0',
                't.',
                '!', 'queue',
                '!', 'videorate',
                '!', 'video/x-raw,framerate={}/1'.format(self.FPS),
                '!', 'zbar',
                '!', 'fakesink',
            ]
        else:
            return [
                'gst-launch-1.0', '-v', '-m',
                'imxv4l2src', 'device={}'.format(self.device),
                '!', 'tee', 'name=t',
                '!', 'queue',
                '!', 'videoconvert',
                '!', 'imxvideoconvert_pxp', 'rotation=horizontal-flip',
                '!', 'imxv4l2sink',
                't.',
                '!', 'queue',
                '!', 'videoconvert',
                '!', 'videorate',
                '!', 'video/x-raw,framerate={}/1'.format(self.FPS),
                '!', 'zbar',
                '!', 'fakesink',
            ]

    def start(self):
        if not self.device:
            return
        if self.pipeline is not None:
            logger.warning('qt scanner already started')
        self.pipeline = subprocess.Popen(
            self._get_pipeline_config(),
            stdout=subprocess.PIPE)
        logger.debug('qr scanner started')

    def stop(self):
        if self.pipeline and self.pipeline.poll() is None:
            self.pipeline.kill()
            logger.debug('qr scanner stopped')
        self.pipeline = None

    def get_data(self):
        if self.pipeline is not None:
            while True:
                line = self.pipeline.stdout.readline()
                if not line:
                    break
                match = self.ZBAR_MSG_REGEX.search(line)
                if match:
                    data = match.group('data')
                    logger.debug('qr scanner has decoded message: {0}'.format(data))
                    return data
