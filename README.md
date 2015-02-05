# nextgisweb_rekod

git clone https://github.com/nextgis/nextgisweb_rekod.git
env/bin/pip install -e ./nextgisweb_rekod
mkdir file_bucket
nano config.ini

дописать:
[file_bucket]
path =  /home/username/ngw/file_bucket

env/bin/nextgisweb --config config.ini initialize_db --drop 
(или без дропа?)
