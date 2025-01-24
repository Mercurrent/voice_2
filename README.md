# Синтезатор речи

## Программа, синтезатор речи
Готовый интерфейс и готовый код синтезатора речи здесь;

Синтезатор речи путь,- main.py

Интерфейс код, - synthesizer_interface/synthesizer_interface.py

### Windows Installation

```
pip install -r requirements.txt
pyinstaller --onefile --windowed --clean --hidden-import=omegaconf --add-data "C:\PATH-TO-YOUR-FFMPEG\ffmpeg.exe;." main.py
```

### Mac Installation

First, install ffmpeg using Homebrew:
```bash
brew install ffmpeg
```

Then build the application:
```bash
cd synthesizer_interface
pip install -r requirements.txt
pyinstaller --onefile --windowed --clean \
    --hidden-import=omegaconf \
    --hidden-import=PyQt5.QtCore \
    --hidden-import=PyQt5.QtGui \
    --hidden-import=PyQt5.QtWidgets \
    --add-data "data:data" \
    synthesizer_interface.py
```

### Build Interface

For Windows:
```bash
cd synthesizer_interface
pip install -r requirements.txt
pyinstaller --onefile --windowed --clean --hidden-import=omegaconf --add-data "C:\PATH-TO-YOUR-FFMPEG\ffmpeg.exe;." synthesizer_interface.py
```

For Mac:
```bash
cd synthesizer_interface
pip install -r requirements.txt
pyinstaller --onefile --windowed --clean --hidden-import=omegaconf synthesizer_interface.py
```

### Debug Build (with UI and console)

Windows:
```bash
cd synthesizer_interface
pyinstaller --onefile --clean \
    --hidden-import=omegaconf \
    --hidden-import=PyQt5.QtCore \
    --hidden-import=PyQt5.QtGui \
    --hidden-import=PyQt5.QtWidgets \
    --add-data "data;data" \
    synthesizer_interface.py
```

Mac:
```bash
cd synthesizer_interface
pyinstaller --onefile --clean \
    --hidden-import=omegaconf \
    --hidden-import=PyQt5.QtCore \
    --hidden-import=PyQt5.QtGui \
    --hidden-import=PyQt5.QtWidgets \
    --add-data "data:data" \
    synthesizer_interface.py
```

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