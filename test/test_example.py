import sys
sys.path.append('/home/ubuntu/train/VideoCut')

import torch
from videoCut.utils import load_audio

torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
vad_model, funcs = torch.hub.load(repo_or_dir="snakers4/silero-vad", model="silero_vad",trust_repo=True)
detect_speech = funcs[0]
audio = load_audio("videos/test001.mp4",16000)
speeches = detect_speech(audio, vad_model, sampling_rate=16000)
print(speeches[0])