import os
import sounddevice as sou_voi
import sys
import time
import torch

language = 'ru'
id_mode = 'ru_v3'
sample_rate = 48000  # 48000
speaker = 'baya'  # aidar, baya, kseniya, xenia, random
put_accent = True
put_yo = True
device = torch.device('cpu')  # cpu или gpu
text = "Хауди Хо, друзья!!!"


def bib_model():
    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models', model='silero_tts', language=language, speaker=id_mode, verbose=False)
    return model


def ttss_audio():
    audio = bib_model().apply_tts(
        text=text,
        speaker=speaker,
        sample_rate=sample_rate,
        put_accent=put_accent,
        put_yo=put_yo
    )
    return audio


if __name__ == '__main__':

    # torch.hub logs to sys.stderr while windowed app has sys.stderr = None
    # https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#sys-stdin-sys-stdout-and-sys-stderr-in-noconsole-windowed-applications-windows-only
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
        #sys.stdout = io.TextIOWrapper(sys.stdout.buffer. encoding='utf-8')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

    bib_model()
    sou_voi.play(ttss_audio(), sample_rate)
    time.sleep(len(ttss_audio()) / sample_rate + 0.2)
    sou_voi.stop()
