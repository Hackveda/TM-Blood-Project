# TM BLOOD-REPORT 😷📃
   

## <a href="https://drive.google.com/file/d/1xuJJ6tFLhfEc9MKhhkzbpMcZqLMVKuuu/view?usp=sharing">👉👉👉👉DEMONSTRATION VIDEO</a>
 
## -> PREREQUISITES (UNIX SERVER):
(Download following packages after creating environment) ⬇
- Python 3.8<br>
- sudo apt-get install python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils ˓→pstotext tesseract-ocr \ flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig
- sudo apt-get install python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils tesseract-ocr flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig libpulse-dev
- Django 3.1.4<br>
- Textract<br>
- NLTK<br>
- Django-widget-tweaks
- Django Bootstrap
- Django date-time picker

## -> STEPS TO BE FOLLOWED 📝
- git clone
- activate virtual env
- Make Migrations--------------</br>
  -> `python manage.py makemigrations users`</br>
  -> `python manage.py migrate`</br>
  -> `python manage.py makemigrations patients`</br>
  -> `python manage.py migrate`</br>
- run create_label.py - label, alterlabel
- grab `label.json` and `alternate.json` from trello.
- run label, alterlabel methods
- create super user.
## To Resolve Permission Denied Error[13]
- cd /var/www/media
- chgrp -R www-data geekingreen/
- chmod -R g+w geekingreen/

## Commands to rescue when error is not specified
- sudo apt-get update
- sudo apt install python3-pip
- sudo apt-get install libsm6 libxrender1 libfontconfig1 libice6 nginx gunicorn
- pip3 install numpy==1.17.2 fastapi==0.54.1 starlette==0.13.2 opencv-python-headless==4.1.2.30 pytesseract==0.3.3 matplotlib==3.1.1 pydantic==1.4 uvicorn==0.11.3 gunicorn  python-multipart==0.0.5
- sudo apt install tesseract-ocr
- sudo apt install libtesseract-dev


NOTE : blood_report folder consist of environmental details so you can exclude it.
