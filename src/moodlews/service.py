from requests import Session
import urllib.parse
import json

class ServerFunctions:
    SITE_INFO = "core_webservice_get_site_info"
    ALL_COURSES = "core_course_get_courses_by_field"
    USER_COURSES = "core_enrol_get_users_courses"
    ASSIGNMENTS = "mod_assign_get_assignments"
    ASSIGNMENT_STATUS = "mod_assign_get_submission_status"
    URLS = "mod_url_get_urls_by_courses"
    RESOURCES = "mod_resource_get_resources_by_courses"

class MoodleClient:
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
    
    def server(self, function, **data):
        return self.__get_response( \
            self.session, \
            self.server_url, \
            wstoken=self.token, \
            moodlewsrestformat="json", \
            wsfunction=function, \
            **data \
        )
    
    def close(self):
        self.session.close()
