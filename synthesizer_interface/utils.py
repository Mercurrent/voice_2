import os
import sys
import torch
from pydub import AudioSegment

def setup_env():
    # torch.hub logs to sys.stderr while windowed app has sys.stderr = None
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

    # Set up torch backend for Mac
    if sys.platform == 'darwin':
        import torch
        torch.backends.quantized.engine = 'qnnpack'

    # setup path to ffmpeg util for mp3 generation
    if getattr(sys, 'frozen', False):
        if sys.platform == 'win32':
            ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg.exe")
            AudioSegment.converter = ffmpeg_path
        else:
            # On Mac, use system ffmpeg
            AudioSegment.converter = "ffmpeg"
    else:
        AudioSegment.converter = "ffmpeg"

    # Set up Qt platform integration for Mac
    if sys.platform == 'darwin':
        os.environ['QT_MAC_WANTS_LAYER'] = '1'

def get_data_dir():
    """Get path to data directory"""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'data')
    return 'data' 