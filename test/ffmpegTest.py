import unittest
import ffmpeg
from unittest.mock import patch, mock_open
from utils.loadAudio import load_audio  

class TestLoadAudio(unittest.TestCase):

    @patch("utils.loadAudio.ffmpeg.input")
    @patch("utils.loadAudio.ffmpeg.output")
    @patch("utils.loadAudio.ffmpeg.run")

    def test_load_audio_success(self, mock_run, mock_output, mock_input):
        # 模拟 ffmpeg 输出的音频数据
        fake_audio_data = b'\x00\x01\x02\x03\x04\x05\x06\x07'
        # 模拟 ffmpeg 的运行结果
        mock_run.return_value = (fake_audio_data, None)

        # 调用 load_audio 函数
        audio_data = load_audio("test.wav")

        # 断言输出的音频数据正确
        self.assertEqual(audio_data[0], 0.0)
        self.assertEqual(audio_data[1], 0.000030517578125)

    @patch("utils.loadAudio.ffmpeg.input")
    @patch("utils.loadAudio.ffmpeg.output")
    @patch("utils.loadAudio.ffmpeg.run")
    def test_load_audio_failure(self, mock_run, mock_output, mock_input):
        # 模拟 ffmpeg 抛出异常
        mock_run.side_effect = ffmpeg.Error("Fake error")

        # 调用 load_audio 函数，预期抛出 RuntimeError
        with self.assertRaises(RuntimeError):
            load_audio("test.wav", sr=44100)

if __name__ == "__main__":
    unittest.main()
