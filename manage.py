#! /usr/bin/env python3
from loganalyzer import app, db
from loganalyzer.models import User, SupportBundle, Tag
from flask_script import Manager, prompt_bool
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def insert_data():
    xzizka = User(username='xzizka',password='Passw0rd',name='Ondrej',surname='Zizka',email='ondrej.zizka@quest.com')
    db.session.add(xzizka)

    def add_support_bundle(service_request,filename, comment,path, datetime, tags):
        db.session.add(SupportBundle(service_request=service_request, filename=filename, comment=comment, path=path, datetime=datetime, user_id=1, tags=tags))

    for name in ["python", "oracle", "support bundle"]:
        db.session.add(Tag(name=name))
    db.session.commit()

    add_support_bundle(3156985, 'nevim.xml', 'komentar 1', '/tmp/nevim.xml', datetime(2016,12,13,hour=12, minute=13,second=52) , 'python')
    add_support_bundle(4021369, 'sb.zip', "komentar 2", '/tmp/sb.zip', datetime(2016,12,15,hour=8, minute=1,second=51), 'oracle,support bundle')
    add_support_bundle(4021110, 'db_test.log', 'komentar 3', '/tmp/db_test.log', datetime(2017,12,13,hour=1, minute=33,second=0), 'python,oracle')

    db.session.commit()

@manager.command
def dbdrop():
    if prompt_bool("Do you want to delete all tables?"):
        db.drop_all()
        print('Tables deleted')

if __name__ == '__main__':
    manager.run()