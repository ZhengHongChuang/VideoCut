import os 
import re
import srt
import logging
from utils import *
from moviepy import editor
class Cutter:
    def __init__(self,args):
        self.inputs = args.input
        self.force = args.force 
        self.encoding = args.encoding
        self.bitrate = args.bitrate
    def run(self):
        fns = {"srt":None,"md":None,"media":None}
        for fn in self.inputs:
            ext = os.path.splitext(fn)[1][1:]
            fns[ext if ext in fns else "media"] = fn
        assert fns["media"], "必须提供原始音频或者视频"
        assert fns["srt"],"必须提供字幕文件"
        is_video_file = is_video(fns["media"].lower())
        output_ext = "mp4" if is_video_file else "mp3"
        output_fn = change_ext(add_cut(fns["media"]),output_ext)
        if check_exists(output_fn,self.force):
            return
        with open(fns["srt"],encoding=self.encoding) as f:
            subs = list(srt.parse(f.read()))
        if fns["md"]:
            md = MD(fns["md"],self.encoding)
            if not md.done_editing():
                return
            index = []
            for mark ,text in md.tasks():
                if not mark:
                    continue
                m = re.match(r"\[(\d+)", text.strip())  # 使用正则表达式匹配任务序号
                if m:
                    index.append(int(m.groups()[0]))
            subs = [s for s in subs if s.index in index]
            logging.info(f"根据{fns['srt']}和{fns['md']}剪辑{fns['media']}ing!!!!")
        else:
            logging.info(f"根据{fns['srt']}剪辑{fns['media']}ing!!!!")
        segments = []
        subs.sort(key= lambda x: x.start)
        for x in subs:  # 遍历字幕
            if len(segments) == 0:  # 如果片段列表为空
                segments.append(
                    {"start": x.start.total_seconds(), "end": x.end.total_seconds()}
                )  # 添加字幕的开始和结束时间到片段列表中
            else:
                if x.start.total_seconds() - segments[-1]["end"] < 0.5:  # 如果字幕开始时间与上一个片段的结束时间间隔小于0.5秒
                    segments[-1]["end"] = x.end.total_seconds()  # 更新上一个片段的结束时间为当前字幕的结束时间
                else:
                    segments.append(
                        {"start": x.start.total_seconds(), "end": x.end.total_seconds()}
                    )  # 添加新的片段到片段列表中

        if is_video_file:  # 如果是视频文件
            media = editor.VideoFileClip(fns["media"])  # 创建视频文件对象
        else:
            media = editor.AudioFileClip(fns["media"])  # 创建音频文件对象

        clips = [media.subclip(s["start"], s["end"]) for s in segments]  # 根据片段列表剪辑视频或音频
        if is_video_file:  # 如果是视频文件
            final_clip: editor.VideoClip = editor.concatenate_videoclips(clips)  # 合并视频片段
            logging.info("视频剪辑成功!!!!")  # 记录日志，减少视频时长

            aud = final_clip.audio.set_fps(44100)  # 设置音频帧率
            final_clip = final_clip.without_audio().set_audio(aud)  # 移除原有音频，设置新音频
            final_clip = final_clip.fx(editor.afx.audio_normalize)  # 标准化音频

            final_clip.write_videofile(
                output_fn, audio_codec="aac", bitrate=self.bitrate
            )  # 将合并后的视频写入文件
        else:
            final_clip: editor.AudioClip = editor.concatenate_audioclips(clips)  # 合并音频片段
            logging.info("音频剪辑成功!!!!")  # 记录日志，减少视频时长 # 记录日志，减少音频时长

            final_clip = final_clip.fx(editor.afx.audio_normalize)  # 标准化音频
            final_clip.write_audiofile(
                output_fn, codec="libmp3lame", fps=44100, bitrate=self.bitrate
            )  # 将合并后的音频写入文件

        media.close()  # 关闭媒体文件
        logging.info(f"保存文件剪辑后文件到{output_fn}ing!!!")  # 记录日志，保存合并后的媒体文件
        logging.info("保存成功！！！！")