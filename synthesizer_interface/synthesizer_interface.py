from PyQt5 import QtCore, QtGui, QtWidgets
import os
import sounddevice as sou_voi
import sys
import time
import torch
from pydub import AudioSegment

import numpy as np

def setup_env():
    # torch.hub logs to sys.stderr while windowed app has sys.stderr = None
    # https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#sys-stdin-sys-stdout-and-sys-stderr-in-noconsole-windowed-applications-windows-only
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

    # setup path to ffmpeg util for mp3 generation
    if getattr(sys, 'frozen', False):
        print(sys._MEIPASS)
        files = os.listdir(sys._MEIPASS)
        print(files)
        ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg.exe")
        AudioSegment.converter = ffmpeg_path
    else:
        AudioSegment.converter = "ffmpeg"


class UiMainWindow(object):
    def __init__(self):
        self.model, _ = torch.hub.load(
            repo_or_dir='snakers4/silero-models', model='silero_tts', language='ru',
            speaker='ru_v3', verbose=False)
        self.sample_rate = 48000

    def setup_ui(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setStyleSheet("background-color: rgb(165, 216, 255);")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Create and configure widgets
        self.create_label()
        self.create_combo_box()
        self.create_text_edit()
        self.create_buttons()

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslate_ui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def create_label(self):
        """Create and configure the main label."""
        self.label_h2 = QtWidgets.QLabel(self.centralwidget)
        self.label_h2.setGeometry(QtCore.QRect(310, 45, 391, 101))
        font = QtGui.QFont("MS Reference Sans Serif", 25, QtGui.QFont.Bold)
        self.label_h2.setFont(font)
        self.label_h2.setObjectName("label_h2")

    def create_combo_box(self):
        """Create and configure the voice selection combo box."""
        self.combo_box_female_male_voice = QtWidgets.QComboBox(self.centralwidget)
        self.combo_box_female_male_voice.setGeometry(QtCore.QRect(110, 80, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.combo_box_female_male_voice.setFont(font)
        self.combo_box_female_male_voice.setStyleSheet("background-color: rgb(165, 216, 255);")
        self.combo_box_female_male_voice.setObjectName("combo_box_female_male_voice")
        self.combo_box_female_male_voice.addItem("Голос женский")
        self.combo_box_female_male_voice.addItem("Голос мужской")

    def create_text_edit(self):
        """Create and configure the text input area."""
        self.plain_text = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plain_text.setGeometry(QtCore.QRect(113, 150, 631, 141))
        self.plain_text.setStyleSheet("font: 18pt 'MS Shell Dlg 2'; background-color: rgb(255, 255, 255);")
        self.plain_text.setObjectName("plain_text")

    def create_buttons(self):
        """Create and configure action buttons."""
        self.button_voice_over = QtWidgets.QPushButton(self.centralwidget)
        self.button_voice_over.setGeometry(QtCore.QRect(480, 320, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        self.button_voice_over.setFont(font)
        self.button_voice_over.setObjectName("button_voice_over")
        self.button_voice_over.setText("Озвучить")
        self.button_voice_over.clicked.connect(self.generate_voice)

        self.button_download = QtWidgets.QPushButton(self.centralwidget)
        self.button_download.setGeometry(QtCore.QRect(120, 320, 191, 101))
        self.button_download.setFont(font)
        self.button_download.setObjectName("button_download")
        self.button_download.setText("Скачать")
        self.button_download.clicked.connect(self.download_audio)

    def retranslate_ui(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Пишет"))
        self.label_h2.setText(_translate("MainWindow", "Введите текст"))
        self.combo_box_female_male_voice.setItemText(0, _translate("MainWindow", "Голос женский"))
        self.combo_box_female_male_voice.setItemText(1, _translate("MainWindow", "Голос мужской"))
        self.button_voice_over.setText(_translate("MainWindow", "Озвучить"))
        self.button_download.setText(_translate("MainWindow", "Скачать"))


    def produce_audio(self):
        text = self.plain_text.toPlainText()
        gender = self.combo_box_female_male_voice.currentText()
        print("in generation", text, gender)
        speaker = 'baya' if "женский" in gender else 'aidar'
        put_accent = True
        put_yo = True
        audio = self.model.apply_tts(
            text=text,
            speaker=speaker,
            sample_rate=self.sample_rate,
            put_accent=put_accent,
            put_yo=put_yo
        )
        return audio

    def generate_voice(self):
        audio = self.produce_audio()
        sou_voi.play(audio, self.sample_rate)
        time.sleep(len(audio) / self.sample_rate + 0.2)
        sou_voi.stop()

    def download_audio(self):
        try:
            audio_data = self.produce_audio().detach().cpu().numpy()
            self.diagnoze_audio(audio_data)
            audio = AudioSegment(
                audio_data.tobytes(),
                frame_rate=self.sample_rate,
                sample_width=audio_data.dtype.itemsize,
                channels=1)
            audio.export("test.mp3", format="mp3")
        except Exception as e:
            print(e, "problem in download")

    def diagnoze_audio(self, audio_data):
        print("Shape", audio_data.shape)
        if audio_data.ndim == 1:
            print("Audio is mono")
        elif audio_data.ndim:
            print("Audio is stereo")
        else:
            print("Unexpected", audio_data.ndim)

        print("Audio data type", audio_data.dtype, "min value", np.min(audio_data))
        print("Sample width in bytes", audio_data.dtype.itemsize)



if __name__ == "__main__":
    setup_env()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setup_ui(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
