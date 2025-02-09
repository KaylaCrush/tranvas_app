import requests, os, json
from src.util import make_request

class CanvasIntegration:
    def __init__(self):
        self.base_url = f"https://{self.load_instance_url()}/api/v1"
        self.userID = self.request_canvas_id()

    def get_current_term_id(self):
        tids = []
        for course in self.all_courses:
            if 'enrollment_term_id' in course.keys() and course['enrollment_term_id'] < 90000000000000:
                tids.append(course['enrollment_term_id'])
        return max(tids)

    def load_instance_url(self):
        with open('settings.json', "r") as f:
            return json.load(f)["canvas_instance_url"]

    def request_current_term_id(self):
        url = f"{self.base_url}/accounts/self/terms/current"
        return self.canvas_request(url)

    def get_all_courses(self):
        url = f"{self.base_url}/courses"
        return self.canvas_request(url)

    def request_current_courses(self):
        url = f"{self.base_url}/courses"
        all_courses = self.canvas_request(url)
        current_courses = [course for course in all_courses if 'enrollment_term_id' in course.keys() and course['enrollment_term_id'] == self.termID]
        return current_courses

    def request_canvas_id(self):
        url = f"{self.base_url}/users/self"
        return self.canvas_request(url)[0]['id']

    def request_assignments(self):
        assignments = []
        for course in self.current_courses:
            # Gets all assignments
            assignments_url = f"{self.base_url}/courses/{course['id']}/assignments"
            for assignment in self.canvas_request(assignments_url):
                    if 'participation' not in assignment['name'].lower():
                        # gets my submissions
                        submissions_url = f"{assignments_url}/{assignment['id']}/submissions/{self.userID}"
                        assignment['submissions'] = self.canvas_request(submissions_url)[0]
                        assignments.append(assignment)
        return assignments

    def canvas_request(self, url, params={}, request_type=requests.get):
        headers = {
            "Authorization": "Bearer " + os.getenv("CANVAS_TOKEN")
        }
        return make_request(url=url, headers=headers, params=params, request_type=request_type)
