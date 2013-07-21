## How we should layout the project

### Config

Webapp aside. all config should go into /etc/scraperwikix

### Web app

Django app should go into /var/www/scraperwikix

### Multiplexer (was twisted)

/opt/scraperwikix/multiplexer 

### Datastore

/opt/scraperwikix/datastore

## What does setup need to do?

Create DB
Create webapp virtualenv
Install requirements 
Copy local_settings.py.template to local_settings.py
Install multiplexer and datastore
Fill in local_settings.py (DB hostname etc), add DB settings to datastore settings
Install CLI

## Modularisation

1. Move datastore to own repo and isolate from other apps
2. Move multiplexer to own repo.
3. Build scraperwikix-common for config mgmt, CLI, etc.