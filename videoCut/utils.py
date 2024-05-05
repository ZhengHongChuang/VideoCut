import logging
import os
import ffmpeg
import numpy as np
def load_audio(file,sr=16000):
    try:
        out, _ = (
        ffmpeg
        .input(file)
        .output("-",format="s16le",acodec='pcm_s16le',ac=1,ar=sr)
        .run(cmd=["ffmpeg","-nostdin"],capture_stdout=True,capture_stderr=True))
    except ffmpeg.Error as e:
        raise RuntimeError(f"加载音频失败:{e.stderr.decode()}") from e

    return np.frombuffer(out,np.int16).flatten().astype(np.float32)/32768.0
def check_exists(output,force):
    if os.path.exists(output):
        if force:
            logging.info(f"{output} 已经存在,将重新覆盖它")
        else:
            logging.info(
                f"{output} 已经存在,不再重新生成"
            )
            return True
    return False
def remove_short_segments(segments,threshold):
    return [s for s in segments if s["end"] - s["start"] > threshold]   
def expand_segments(segments,expand_head,expand_tail,total_length):
    res = []
    for i in range(len(segments)):
        temp = segments[i]
        start = max(temp["start"] - expand_head,segments[i-1]["end"] if i > 0 else 0)
        end = min(temp["end"] + expand_tail,segments[i+1]["start"] if i<len(segments)-1 else total_length)
        res.append({"start":start,"end":end})
    return res
def merge_adjacent_segments(segments,threshold):
    res = []
    i = 0
    while i < len(segments):
        s = segments[i]
        for j in range(i+1,len(segments)):
            if segments[j]["start"] < s["end"] + threshold:
                s["end"] = segments[j]["end"]
                i = j
            else: break
        i +=1
        res.append(s)

    return res 

class MD:
    def __init__(self,filename,encoding):
        self.lines = []
        self.EDIT_MAKR = "<-- 标记字幕保留！！"
        self.encding = encoding
        self.filename = filename
        if filename:
            self.load_file()
    def load_file(self):
        if os.path.exists(self.filename):
            with open(self.filename,encoding=self.encding) as f:
                self.lines = f.readlines()
    def clear(self):
        self.lines = []
    def add(self,line):
        self.lines.append(line)
    def write(self):
        with open(self.filename,"wb") as f:
            f.write("\n".join(self.lines).encode(self.encding,"replace"))
    def add_task(self,mark,content):
        self.add(f'- [{"x" if mark else " "}] {content.strip()}')
    def add_done_editing(self,mark):
        self.add_task(mark,self.EDIT_MAKR)
    def add_video(self, video_fn):
        ext = os.path.splitext(video_fn)[1][1:]
        self.add(
            f'\n<video controls="true" allowfullscreen="true"> <source src="{video_fn}" type="video/{ext}"> </video>\n'
        )




    
