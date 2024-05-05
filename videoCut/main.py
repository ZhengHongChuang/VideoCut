import argparse
import logging
import os
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
        choices=["cpu", "cuda"],
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
        help="强制写入",
        action="store_true",
    )
    parser.add_argument(
        "--vad", 
        action="store_true",
        help="是否使用VAD"
    )
    parser.add_argument(
        "-l",
        "--lang" ,
        choices=get_args(LANG),
        default="zh",
        help="语言"
    )
    parser.add_argument(
        "-p",
        "--prompt" ,
        type=str,
        default="",
        help="添加提示词"
    )
    parser.add_argument(
        "-e",
        "--encoding" ,
        type=str,
        default="utf-8",
        help="选择编码格式"
    )


    args = parser.parse_args()
    if args.transcribe:
        from transcribe import Transcribe
        Transcribe(args).run()
        # Transcribe(args).run()