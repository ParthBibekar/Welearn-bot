from requests import Session
import urllib.parse
import json

class Moodle:
    def __init__(self, baseurl):
        self.baseurl = baseurl
        self.login_url = urllib.parse.urljoin(baseurl, "login/token.php")
        self.server_url = urllib.parse.urljoin(baseurl, "webservice/rest/server.php")
        self.session = Session()

    def __get_response(self, session, url, **data):
        response = session.post(url, data)
        return json.loads(response.content)
    
    def authenticate(self, username, password):
        login = self.__get_response( \
            self.session, \
            self.login_url, \
            username=username, \
            password=password, \
            service="moodle_mobile_app" \
        )
        try:
            token = login['token']
            self.token = token
            return token
        except KeyError:
            return False

    def close(self):
        self.session.close()
