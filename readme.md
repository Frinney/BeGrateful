python app.py - запуск приложение

http://127.0.0.1:5000/register - сам сайт который хостится


GIT guide

Перейди в директорию с репозиторием: Если ты еще не клонировал репозиторий на свой компьютер, сначала это сделай:

git clone <URL репозитория>

Перейди в папку репозитория:
(Вы также можете вызвать Git Bash нажав пкм находясь в папке с проектом.)

cd <имя_репозитория>

Далее вы добавляете новые файлы/изменяете

Добавь изменения в индекс Git: Добавь папку в индекс с помощью команды:

git add <имя_папки>


Либо добавь все изменения (включая добавленную папку):

git add .

Сделай коммит: После добавления папки сделай коммит изменений:

git commit -m "Добавлена новая папка"


Отправь изменения в удаленный репозиторий: Загрузить изменения на GitHub можно командой:

git push origin main