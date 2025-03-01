import argparse
import logging
from type import *

def main():
    parser = argparse.ArgumentParser(
        description = "通过字幕剪辑视频",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    logging.basicConfig(
        format="[VideoCut:%(filename)s:L%(lineno)d] %(levelname)-6s %(message)s"
    )
    logging.getLogger().setLevel(logging.INFO)
    parser.add_argument(
        "input",
        type=str,
        nargs="+",
        help="输入文件或文件夹路径")
    parser.add_argument(
        "-t",
        "--transcribe",
        help="生成字幕文件",
        action="store_true",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda:1"],
        help="指定cpu或gpu",
    )
    parser.add_argument(
        "-n",
        "--model_name",
        type=str,
        default="small",
        choices=get_args(MODEL),
        help="指定whisper的模型版本"
    )
    parser.add_argument(
        "-sr",
        "--sample_rate",
        type=int,
        default=16000,
        help="指定视频采样率",
    )
    parser.add_argument(
        "--force",
        help="强制写入md文件",
        action="store_true",
    )
    parser.add_argument(
        "--vad", 
        action="store_true",
        help="使用VAD检测声音信号"
    )
    parser.add_argument(
        "-l",
        "--lang" ,
        choices=get_args(LANG),
        default="zh",
        help="选择输出的语言"
    )
    parser.add_argument(
        "-p",
        "--prompt" ,
        type=str,
        default="",
        help="为模型添加提示词"
    )
    parser.add_argument(
        "-e",
        "--encoding" ,
        type=str,
        default="utf-8",
        help="选择输出文件的编码格式"
    )
    parser.add_argument(
        "-c",
        "--cut" ,
        help="生成剪辑后的视频",
        action="store_true",
    )
    parser.add_argument(
        "-b",
        "--bitrate" ,
        type=str,
        default="10m",
        help="设置比特率:默认为10m",
    )


    args = parser.parse_args()
    if args.transcribe:
        from transcribe import Transcribe
        Transcribe(args).run()
    else:
        from cut import Cutter
        Cutter(args).run()

