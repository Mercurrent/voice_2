# Синтезатор речи

## Программа, синтезатор речи
Готовый интерфейс и готовый код синтезатора речи здесь;

Синтезатор речи путь,- main.py

Интерфейс код, - synthesizer_interface/synthesizer_interface.py

Получить exe для main.py:

```
pip install -r requirements.txt
pyinstaller --onefile --windowed --clean --hidden-import=omegaconf main.py
```

Получить exe для synthesizer_interface.py:

```
cd synthesizer_interface
pip install -r requirements.txt
pyinstaller --onefile --windowed --clean synthesizer_interface.py
```


## 1) Синтезатор речь работает без интернета. 
## 2) Без электронного голоса. 
## 3) Создание функции выбора голоса: мужской или женский. 
## 4) Создание функции для скачивания файла аудио
