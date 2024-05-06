
import os
import srt
import torch
import logging
from type import *
from typing import List, Any
from whisper_model import WhisperModel
from utils import *
class Transcribe:
    def __init__(self,args):
        self.detect_speech = None
        self.vad_model = None

        self.sampling_rate = args.sample_rate
        self.whisper_name = args.model_name
        self.device = args.device
        self.inputs = args.input
        self.force = args.force
        self.vad = args.vad
        self.lang = args.lang
        self.prompt = args.prompt
        self.encoding = args.encoding

        self.whisper_model = WhisperModel(self.sampling_rate)
        self.whisper_model.load(self.whisper_name,self.device)
        logging.info("Whisper模型加载完成!!!")
    # 生成音频字幕
    def run(self):
        for input in self.inputs:
            logging.info(f"{input}生成字幕ing!!!")
            name,_ = os.path.splitext(input)
            if check_exists(name+'.md',self.force):
                logging.info(f"{name}.md已经存在将跳过生成!!(可使用--force强制重新生成)")
                continue
            audio = load_audio(input,self.sampling_rate)
            speech_indices = self._detect_voice_activity(audio=audio)
            res = self._transcribe(audio=audio,speech_indicers=speech_indices)
            output = name + '.srt'
            self._save_srt(output,res)
            logging.info(f"{output}生成成功!!!")
            self._srt2md(name+".md",output,input)
            logging.info(f"{name}.md生成成功!!!")
        
     # srt转md格式
    def _srt2md(self,md_fn,srt_fn,audio_fn):
        with open(srt_fn,encoding=self.encoding) as f:
            subs = srt.parse(f.read())

        md = MD(md_fn,encoding=self.encoding)
        # 写入提示信息
        md.clear()
        md.add_done_editing(True)
        md.add_video(os.path.basename(audio_fn))
        md.add(
            f"\n字幕生成来自 [{os.path.basename(srt_fn)}]({os.path.basename(srt_fn)})."
            "标记下面的字幕段用于生成视频！！\n\n"
        )
        # 写入字幕内容
        for src in subs:
            sec = src.start.seconds
            pre = f"[{src.index},{sec //60:02d}:{sec%60:02d}]"
            md.add_task(False,f"{pre:11} {src.content.strip()}")
        md.write()      
    def _detect_voice_activity(self, audio) -> List[SPEECH_ARRAY_INDEX]:
        # 声音信号检测  若--vad 则将使用VAD模型提取有说话的音频信号段否则返回整个音频段
        if self.vad is False:
            return [{"start":0,"end":len(audio)}]
        else:
            # torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
            # git@github.com:snakers4/silero-vad.git
            self.vad_model, funcs = torch.hub.load(repo_or_dir="snakers4/silero-vad", model="silero_vad",trust_repo=True)
            self.detect_speech = funcs[0]
            speeches = self.detect_speech(audio,self.vad_model,sampling_rate = self.sampling_rate)
            # 音频的处理 1、移除不足一秒的声音段 2、为声音段向前填充0.2s 3、将2个声音信号不足1s间隔的合并为一个声音信号
            speeches = remove_short_segments(speeches,1.0*self.sampling_rate)
            speeches = expand_segments(speeches,0.2*self.sampling_rate,0.0*self.sampling_rate,audio.shape[0])
            speeches = merge_adjacent_segments(speeches,0.5*self.sampling_rate)
        logging.info("声音信号处理完成！！！")
        return speeches if len(speeches)>1 else [{"start":0,"end":len(audio)}]
    def _transcribe(self,audio:np.ndarray,speech_indicers:List[SPEECH_ARRAY_INDEX])->List[Any]:
        return self.whisper_model.transcribe(audio,speech_indicers,self.lang,self.prompt)
    # 生成srt字幕文件
    def _save_srt(self, output, res):
        # 获取字幕
        subs = self.whisper_model.gen_srt(res)
        # 将生成的字幕写入文件中
        with open(output, "wb") as f:
            # 使用 srt.compose 方法将Text转换为 SRT 格式，并以指定编码写入文件
            f.write(srt.compose(subs).encode(self.encoding, "replace"))



                                                 