# Russian Text-to-Speech Synthesizer

## Project Structure
```
synthesizer_interface/
├── __init__.py
├── synthesizer_interface.py
├── trie.py
├── utils.py
├── word_suggestions.py
├── user_memory.py
├── data/
│   ├── top_10_percent_1grams.tsv
│   └── top_10_percent_2grams.tsv
└── requirements.txt
```

Data taken from https://ruscorpora.ru/page/corpora-freq

## Build Commands

### Mac OS

Console version:
```bash
cd synthesizer_interface
pyinstaller --onefile --console --clean \
    --hidden-import=omegaconf \
    --hidden-import=PyQt5.QtCore \
    --hidden-import=PyQt5.QtGui \
    --hidden-import=PyQt5.QtWidgets \
    --hidden-import=synthesizer_interface \
    --hidden-import=synthesizer_interface.trie \
    --hidden-import=synthesizer_interface.utils \
    --hidden-import=synthesizer_interface.word_suggestions \
    --add-data "data:data" \
    --paths=".." \
    synthesizer_interface.py
```

GUI version (no console):
```bash
cd synthesizer_interface
pyinstaller --onefile --windowed --clean \
    --hidden-import=omegaconf \
    --hidden-import=PyQt5.QtCore \
    --hidden-import=PyQt5.QtGui \
    --hidden-import=PyQt5.QtWidgets \
    --hidden-import=synthesizer_interface \
    --hidden-import=synthesizer_interface.trie \
    --hidden-import=synthesizer_interface.utils \
    --hidden-import=synthesizer_interface.word_suggestions \
    --add-data "data:data" \
    --paths=".." \
    synthesizer_interface.py
```

### Windows

Console version:
```bash
cd synthesizer_interface
pyinstaller --onefile --console --clean --hidden-import=omegaconf --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=PyQt5.QtWidgets --hidden-import=synthesizer_interface --hidden-import=synthesizer_interface.trie --hidden-import=synthesizer_interface.utils --hidden-import=synthesizer_interface.word_suggestions --add-data "data;data" --paths=".." synthesizer_interface.py
```

GUI version (no console):
```bash
cd synthesizer_interface
pyinstaller --onefile --windowed --clean --hidden-import=omegaconf --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=PyQt5.QtWidgets --hidden-import=synthesizer_interface --hidden-import=synthesizer_interface.trie --hidden-import=synthesizer_interface.utils --hidden-import=synthesizer_interface.word_suggestions --add-data "data;data" --paths=".." synthesizer_interface.py
```

Note: The difference between Windows and Mac commands is in the path separator:
- Mac uses colon (:) in --add-data "data:data"
- Windows uses semicolon (;) in --add-data "data;data"

## Build Output
The executable will be created in:
- `synthesizer_interface/dist/synthesizer_interface` (Mac)
- `synthesizer_interface/dist/synthesizer_interface.exe` (Windows)

## User Data
The application stores user data in:
- `user_memory.json`: Custom word frequencies
- Generated audio files are saved in the same directory as the executable

## Features
1) Синтезатор речь работает без интернета. 
2) Без электронного голоса. 
3) Создание функции выбора голоса: мужской или женский. 
4) Создание функции для скачивания файла аудио

## Note for Mac Users
- The application uses PyQt5 which is compatible with macOS
- ffmpeg is required and can be installed via Homebrew
- No need to explicitly include ffmpeg in the build as it will use the system-installed version

Words are extracted from project https://github.com/Badestrand/russian-dictionary