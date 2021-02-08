# TM-Blood-Project
Trusting Minds Blood Report Comparison

# TM BLOOD-REPORT 😷📃
 
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
- `cd /var/www/media`
- `chgrp -R www-data geekingreen/`
- `chmod -R g+w geekingreen/`

NOTE : blood_report folder consist of environmental details so you can exclude it.
