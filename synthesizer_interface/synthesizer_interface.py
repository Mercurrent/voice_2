from PyQt5 import QtCore, QtGui, QtWidgets
import os
import sounddevice as sou_voi
import sys
import time
import torch
from pydub import AudioSegment
import re

import numpy as np

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

class UiMainWindow(object):
    def __init__(self):
        # Initialize torch backend before loading model on Mac
        if sys.platform == 'darwin':
            import torch
            torch.backends.quantized.engine = 'qnnpack'
        
        # Load model
        print("Loading model...")
        self.model, _ = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_tts',
            language='ru',
            speaker='ru_v3',
            verbose=False
        )
        self.sample_rate = 48000

        # Load word suggestions
        self.custom_dict_path = self.get_custom_dict_path()
        self.words = self.load_words()
        self.suggestion_buttons = []

    def get_model_dir(self):
        """Get path to store the model"""
        if getattr(sys, 'frozen', False):
            # If running as bundled app, store next to executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # If running from source, store in user's home directory
            base_dir = os.path.expanduser('~')
        
        model_dir = os.path.join(base_dir, '.silero_models')
        os.makedirs(model_dir, exist_ok=True)
        return model_dir

    def load_or_download_model(self):
        """Load model from local cache or download if not present"""
        try:
            # Try to load local model first
            model_path = os.path.join(self.model_dir, 'model.pt')
            if os.path.exists(model_path):
                print("Loading model from local cache...")
                model = torch.jit.load(model_path)
                model = torch.hub.load(
                    repo_or_dir=self.model_dir,  # Use local directory
                    model='silero_tts',
                    language='ru',
                    speaker='ru_v3',
                    source='local',  # Indicate local source
                    verbose=False
                )
                print("Model loaded successfully from cache")
                return model
            
            # If not found locally, download and save
            print("Downloading model...")
            model, _ = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language='ru',
                speaker='ru_v3',
                verbose=False
            )
            
            # Save the model's state dictionary to local cache
            print("Saving model to local cache...")
            # Define example inputs for tracing
            example_text = "Привет, мир!"
            example_audio = model(example_text)  # Generate example output
        
            # Trace the model
            traced_model = torch.jit.trace(model, (example_text,))
            print("Model saved successfully")
            return model
            
        except Exception as e:
            print(f"Error loading/downloading model: {e}")
            import traceback
            traceback.print_exc()
            raise

    def get_custom_dict_path(self):
        """Get path to custom dictionary file"""
        if getattr(sys, 'frozen', False):
            # If running as bundled app
            base_dir = os.path.dirname(sys.executable)
        else:
            # If running from source
            base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, 'custom_dictionary.txt')

    def load_words(self):
        """Load words from data files"""
        words = set()
        data_dir = 'data'
        if getattr(sys, 'frozen', False):
            data_dir = os.path.join(sys._MEIPASS, 'data')
        print(f"Looking for data in: {data_dir}")
        print(f"Directory exists: {os.path.exists(data_dir)}")
        if os.path.exists(data_dir):
            print(f"Contents of {data_dir}:")
            print(os.listdir(data_dir))
            
        try:
            for words_filename in ['verbs-processed.txt', 'nouns_processed.txt', 'adjectives_processed.txt', 'adverbs_processed.txt', 'others_processed.txt']:
                words_path = os.path.join(data_dir, words_filename)
                print(f"Looking for file: {words_path}")
                if os.path.exists(words_path):
                    with open(words_path, 'r', encoding='utf-8') as f:
                        words.update(line.strip() for line in f)
            print(f"Loaded {len(words)} built-in words")
            
            # Load custom dictionary
            if os.path.exists(self.custom_dict_path):
                with open(self.custom_dict_path, 'r', encoding='utf-8') as f:
                    custom_words = set(line.strip() for line in f)
                    words.update(custom_words)
                    print(f"Loaded {len(custom_words)} custom words")

        except Exception as e:
            print(f"Error loading words: {e}")
            import traceback
            traceback.print_exc()
            
        return sorted(list(words))

    def add_to_custom_dictionary(self, word):
        """Add a new word to custom dictionary"""
        # Only add if it's not already in our word list
        if word not in self.words:
            try:
                with open(self.custom_dict_path, 'a', encoding='utf-8') as f:
                    f.write(word + '\n')
                self.words = sorted(self.words + [word])
                print(f"Added new word to custom dictionary: {word}")
            except Exception as e:
                print(f"Error adding word to custom dictionary: {e}")

    def create_suggestion_buttons(self):
        """Create a row of suggestion buttons"""
        self.suggestion_frame = QtWidgets.QFrame(self.centralwidget)
        self.suggestion_frame.setGeometry(QtCore.QRect(113, 300, 631, 40))
        self.suggestion_layout = QtWidgets.QHBoxLayout(self.suggestion_frame)
        self.suggestion_layout.setSpacing(5)
        self.suggestion_layout.setContentsMargins(0, 0, 0, 0)
        self.suggestion_frame.setStyleSheet("background-color: transparent;")
        
        # Create 5 buttons
        for i in range(5):
            btn = QtWidgets.QPushButton(self.suggestion_frame)
            btn.setMinimumSize(120, 30)
            btn.setMaximumSize(120, 30)
            btn.setFont(QtGui.QFont("MS Shell Dlg 2", 10))
            btn.setStyleSheet("background-color: white; border: 1px solid gray;")
            btn.clicked.connect(lambda checked, b=btn: self.use_suggestion(b.text()))
            btn.setText("")  # Start with empty text
            self.suggestion_buttons.append(btn)
            self.suggestion_layout.addWidget(btn)

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
        self.create_suggestion_buttons()
        self.create_buttons()

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslate_ui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Connect text changed signal
        self.plain_text.textChanged.connect(self.update_suggestions)

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
        self.combo_box_female_male_voice.addItem("Голос aidar")
        self.combo_box_female_male_voice.addItem("Голос baya")
        self.combo_box_female_male_voice.addItem("Голос kseniya")
        self.combo_box_female_male_voice.addItem("Голос xenia")
        self.combo_box_female_male_voice.addItem("Голос eugene")
        self.combo_box_female_male_voice.addItem("Голос random")

    def create_text_edit(self):
        """Create and configure the text input area."""
        self.plain_text = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plain_text.setGeometry(QtCore.QRect(113, 150, 631, 141))
        self.plain_text.setStyleSheet("font: 18pt 'MS Shell Dlg 2'; background-color: rgb(255, 255, 255);")
        self.plain_text.setObjectName("plain_text")

    def create_buttons(self):
        """Create and configure action buttons."""
        self.button_voice_over = QtWidgets.QPushButton(self.centralwidget)
        self.button_voice_over.setGeometry(QtCore.QRect(480, 380, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        self.button_voice_over.setFont(font)
        self.button_voice_over.setObjectName("button_voice_over")
        self.button_voice_over.setText("Озвучить")
        self.button_voice_over.clicked.connect(self.generate_voice)

        self.button_download = QtWidgets.QPushButton(self.centralwidget)
        self.button_download.setGeometry(QtCore.QRect(120, 380, 191, 101))
        self.button_download.setFont(font)
        self.button_download.setObjectName("button_download")
        self.button_download.setText("Скачать")
        self.button_download.clicked.connect(self.download_audio)

    def retranslate_ui(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Пишет"))
        self.label_h2.setText(_translate("MainWindow", "Введите текст"))
        #self.combo_box_female_male_voice.setItemText(0, _translate("MainWindow", "Голос женский"))
        #self.combo_box_female_male_voice.setItemText(1, _translate("MainWindow", "Голос мужской"))
        self.button_voice_over.setText(_translate("MainWindow", "Озвучить"))
        self.button_download.setText(_translate("MainWindow", "Скачать"))

    def produce_audio(self):
        text = self.plain_text.toPlainText()
        speaker_label = self.combo_box_female_male_voice.currentText()
        speaker = speaker_label.split()[1]
        print("in generation", text, speaker)
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
        time.sleep(len(audio) / self.sample_rate + 0.3)
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

    def update_suggestions(self):
        """Update suggestion buttons based on current text"""
        text = self.plain_text.toPlainText().strip().lower()
        
        # Get last word being typed using regex for Russian letters
        russian_word_pattern = r'[а-яёА-ЯЁ]+'
        words = re.findall(russian_word_pattern, text)

        # Check if we should add this word to dictionary
        if ' ' in text:  # If there are multiple words
            completed_words = text.split()[:-1]  # Get all but last word
            for word in completed_words:
                if re.match(russian_word_pattern, word):  # If it's a Russian word
                    print("Adding new word to dictionary", word)
                    self.add_to_custom_dictionary(word)

        if not words:
            for btn in self.suggestion_buttons:
                btn.setText("")
            return

        last_word = words[-1].lower()
        
        
        # Find all matching words
        matching_words = [w for w in self.words if w.lower().startswith(last_word)]
        
        # Get diverse suggestions
        suggestions = self.get_diverse_suggestions(matching_words, 5)

        # Update button texts (keep all buttons visible)
        for i, btn in enumerate(self.suggestion_buttons):
            if i < len(suggestions):
                btn.setText(suggestions[i])
            else:
                btn.setText("")

    def get_diverse_suggestions(self, words, num_suggestions):
        """Select diverse words from the matching words"""
        if not words:
            return []
        if len(words) <= num_suggestions:
            return words

        # Sort words by length to help select different sized words
        words_by_length = sorted(words, key=len)
        
        # Get words from different length ranges
        result = []
        total_words = len(words_by_length)
        
        # Try to get words from different parts of the sorted list
        indices = [
            0,  # shortest word
            total_words // 4,  # word from first quarter
            total_words // 2,  # median length word
            (3 * total_words) // 4,  # word from last quarter
            total_words - 1,  # longest word
        ]
        
        # Get unique words (some indices might point to same/similar length words)
        seen = set()
        for idx in indices:
            word = words_by_length[idx]
            if word not in seen:
                seen.add(word)
                result.append(word)
        
        # If we need more words, fill with random selections
        if len(result) < num_suggestions:
            import random
            remaining = [w for w in words if w not in seen]
            result.extend(random.sample(remaining, min(num_suggestions - len(result), len(remaining))))
        
        return result[:num_suggestions]

    def use_suggestion(self, word):
        """Insert the suggested word into text"""
        if not word:  # Don't do anything if button is empty
            return
        
        text = self.plain_text.toPlainText()
        words = text.split()
        if words:
            words[-1] = word
        new_text = ' '.join(words) + ' '  # Add space after the word
        
        # Save current cursor
        cursor = self.plain_text.textCursor()
        
        # Update text
        self.plain_text.setPlainText(new_text)
        
        # Move cursor to end
        cursor.movePosition(QtGui.QTextCursor.End)
        self.plain_text.setTextCursor(cursor)
        
        # Set focus back to text input
        self.plain_text.setFocus()

if __name__ == "__main__":
    setup_env()
    
    # Force the usage of a specific Qt platform
    if sys.platform == 'darwin':
        os.environ['QT_QPA_PLATFORM'] = 'cocoa'
    
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setup_ui(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
