from flask import url_for
from datetime import datetime
from flask_testing import TestCase


import loganalyzer
from loganalyzer.models import User, SupportBundle

class LogAnalyzerTestCase(TestCase):

    def create_app(self):
        return loganalyzer.create_app('test')

    def setUp(self):
        self.db = loganalyzer.db
        self.db.create_all()
        self.client = self.app.test_client()

        u = User(username='test', name='Testname', surname='TestSurname', email='test@exmaple.com', password='Passw0rd')
        sb = SupportBundle(user=u, service_request=123456, filename='boot.log',path='/tmp/boot.log', comment='test', tags="Python, test, test1" )

        self.db.session.add(u)
        self.db.session.add(sb)
        self.db.session.commit()

        self.client.post(url_for('auth.login'), data = dict(username='test', password='Passw0rd'))

    def tearDown(self):
        loganalyzer.db.session.remove()
        loganalyzer.db.drop_all()

    def test_delete_all_tags(self):
        response = self.client.post(
            url_for('supportbundles.edit', sb_id=1),
            data = dict(
                service_request='12345',
                comment='testtest',
                tags='Python'
            ),
            follow_redirects = True
        )

        assert response.status_code == 200
        sb = SupportBundle.query.first()
        assert sb._tags