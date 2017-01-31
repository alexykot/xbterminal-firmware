import unittest
from mock import patch, Mock

from xbterminal.rpc.utils.camera import QRScanner, Worker


class QRScannerTestCase(unittest.TestCase):

    @patch('xbterminal.rpc.utils.camera.subprocess.check_output')
    def test_init(self, check_output_mock):
        check_output_mock.return_value = ' Captured frame '
        qr_scanner = QRScanner()
        self.assertEqual(check_output_mock.call_count, 1)
        self.assertEqual(qr_scanner.device, '/dev/video0')
        self.assertIsNone(qr_scanner.worker)

    @patch('xbterminal.rpc.utils.camera.subprocess.check_output')
    @patch('xbterminal.rpc.utils.camera.subprocess.check_call')
    @patch('xbterminal.rpc.utils.camera.Worker')
    def test_start_stop(self, worker_cls_mock,
                        check_call_mock, check_output_mock):
        check_output_mock.return_value = ' Captured frame '
        worker_cls_mock.return_value = worker_mock = Mock(**{
            'is_alive.return_value': True,
            'data': 'test',
        })
        qr_scanner = QRScanner()
        qr_scanner.start()
        self.assertEqual(worker_cls_mock.call_args[0][0][0],
                         'gst-launch-1.0')
        self.assertIs(worker_mock.start.called, True)
        self.assertEqual(qr_scanner.get_data(), 'test')
        qr_scanner.stop()
        self.assertIs(worker_mock.stop.called, True)
        self.assertIs(worker_mock.join.called, True)


class WorkerTestCase(unittest.TestCase):

    def test_init(self):
        config = ['gst-launch-1.0']
        worker = Worker(config)
        self.assertIsNone(worker.pipeline)
        self.assertEqual(worker.pipeline_config, config)
        self.assertIsNone(worker.data)
