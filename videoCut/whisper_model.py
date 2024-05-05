import numpy as np
import srt
import datetime
import opencc
from abc import ABC,abstractmethod
from typing import Any,List
from type import *
from tqdm import tqdm
cc = opencc.OpenCC("t2s")
class AbstractWhisperModel(ABC):
    def __init__(self,mode, sample_rate=16000) :
        self.mode = mode
        self.whisper_model = None
        self.sample_rate = sample_rate
    @abstractmethod
    def load(self, *args, **kwargs):
        pass
    @abstractmethod
    def transcribe(self, *args, **kwargs):
        pass
    @abstractmethod
    def _transcribe(self, *args, **kwargs):
        pass
    @abstractmethod
    def gen_srt(self, transcribe_results: List[Any]) -> List[srt.Subtitle]:
        pass

class WhisperModel(AbstractWhisperModel):
    def __init__(self, sample_rate=16000):
        super().__init__("whisper", sample_rate)
        self.device = None
    def load(self, 
             model_name:MODEL = "small",
             device: DEVICE = None):
        import whisper
        self.whisper_model = whisper.load_model(name=model_name,device=device)
    def _transcribe(self, audio, seg, lang, prompt):
        # 从音频中提取指定段的音频数据，并调用 whisper_model 的 transcribe 方法进行转录
        r = self.whisper_model.transcribe(
            audio[int(seg["start"]) : int(seg["end"])],  # 切片获取指定段的音频数据
            task="transcribe",  # 任务类型为转录
            language=lang,  # 指定语言
            initial_prompt=prompt,  # 初始提示
        )
        r["origin_timestamp"] = seg  # 将音频段索引添加到结果中，方便后续处理
        return r  # 返回转录结果
    def transcribe(
        self,
        audio: np.ndarray,  # 输入音频的 numpy 数组表示
        speech_array_indices: List[SPEECH_ARRAY_INDEX],  # 音频段的索引列表
        lang: LANG,  # 语言
        prompt: str,  # 提示
    ):
        res = []  # 存储结果的列表
        if self.device == "cpu" and len(speech_array_indices) > 1:  # 如果使用 CPU，并且有多个音频段
            from multiprocessing import Pool  # 导入进程池模块

            pbar = tqdm(total=len(speech_array_indices))  # 创建一个进度条

            pool = Pool(processes=4)  # 创建一个包含 4 个进程的进程池
            sub_res = []  # 存储子进程结果的列表
            for seg in speech_array_indices:  # 遍历每个音频段
                # 将任务提交给进程池，并指定回调函数更新进度条
                sub_res.append(
                    pool.apply_async(
                        self._transcribe,
                        (
                            self.whisper_model,  # Whisper 模型
                            audio,  # 音频数据
                            seg,  # 音频段索引
                            lang,  # 语言
                            prompt,  # 提示
                        ),
                        callback=lambda x: pbar.update(),  # 回调函数，更新进度条
                    )
                )
            pool.close()  # 关闭进程池，不再接受新的任务
            pool.join()  # 等待所有子进程结束
            pbar.close()  # 关闭进度条
            res = [i.get() for i in sub_res]  # 获取所有子进程的结果
        else:
            # 单个音频段或者使用 GPU 时的处理方式
            for seg in (
                speech_array_indices
                if len(speech_array_indices) == 1
                else tqdm(speech_array_indices)  # 多个音频段时，显示进度条
            ):
                # 调用 Whisper 模型的 transcribe 方法进行转录
                r = self.whisper_model.transcribe(
                    audio[int(seg["start"]) : int(seg["end"])],  # 切片获取音频段数据
                    task="transcribe",  # 任务类型
                    language=lang,  # 语言
                    initial_prompt=prompt,  # 提示
                    verbose=False if len(speech_array_indices) == 1 else None,  # 是否显示详细信息
                )
                r["origin_timestamp"] = seg  # 将音频段索引添加到结果中
                res.append(r)  # 将结果添加到 res 列表中
        return res  # 返回结果
    def gen_srt(self, transcribe_results):
        subs = []  # 存储生成的 SRT 字幕对象的列表
        def _add_sub(start, end, text):
            """
            添加一个字幕到字幕列表中。

            Args:
                start (float): 字幕的开始时间（秒）。
                end (float): 字幕的结束时间（秒）。
                text (str): 字幕文本内容。

            Returns:
                None
            """
            # 创建一个 SRT 字幕对象并添加到列表中
            subs.append(
                srt.Subtitle(
                    index=0,
                    start=datetime.timedelta(seconds=start),
                    end=datetime.timedelta(seconds=end),
                    content=cc.convert(text.strip()),  # 使用 cc.convert 方法转换文本内容
                )
            )

        prev_end = 0  # 上一个字幕的结束时间
        for r in transcribe_results:
            origin = r["origin_timestamp"]  # 获取原始音频段的时间戳
            for s in r["segments"]:
                start = s["start"] + origin["start"] / self.sample_rate  # 计算字幕的开始时间
                end = min(
                    s["end"] + origin["start"] / self.sample_rate,
                    origin["end"] / self.sample_rate,
                )  # 计算字幕的结束时间，避免超出原始音频段的范围
                if start > end:
                    continue  # 如果开始时间大于结束时间，则跳过
                # 如果当前字幕的开始时间大于上一个字幕的结束时间超过 1 秒，添加一个空白字幕
                if start > prev_end + 1.0:
                    _add_sub(prev_end, start, "< No Speech >")
                _add_sub(start, end, s["text"])  # 添加当前字幕
                prev_end = end  # 更新上一个字幕的结束时间

        return subs  # 返回生成的 SRT 字幕对象列表

