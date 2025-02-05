import requests, os
from datetime import datetime, timezone
from src.integrations.stateManager import StateManager

class Assignment:
    def __init__(self, assignment_data):
        self.data = assignment_data

    def __repr__(self):
        return self.data

    def is_complete(self):
        # Cases:
        # Assignment is a zybooks assignment. Zybooks are only complete when they are 100% complete
        # Assignment is anything else. Other assignments are marked complete when they have a submission
        if self.has_duedate() and self.has_submissions():
            if self.is_zybook() and self.submissions()['score'] == 100.0:
                return True
            return True
        return False

    def submissions(self):
        return self.data['submissions']

    def has_submissions(self):
        return self.data['submissions']['submitted_at'] != None

    def is_graded(self):
        return self.data['submissions']['graded_at'] != None and self.is_complete()

    def has_duedate(self):
        return 'due_at' in self.data.keys() and self.data['due_at'] != None

    def is_zybook(self):
        return 'zybook' in self.data['name'].lower()

    def days_till_due(self):
        assignment = self.data
        timestamp_dt = datetime.strptime(assignment['due_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)
        difference = timestamp_dt-current_time
        return difference.days

class CanvasIntegration:

    base_url = "https://canvas.seattlecolleges.edu/api/v1/"
    list_courses = base_url+"courses"
    get_todo = base_url+"users/self/todo"

    def __init__(self):
        self.sm = StateManager()
        self.userID = self.sm.getOrPut('canvas_userid', 2233) # TODO: find automatically / user input
        self.termID = self.sm.getOrPut('canvas_term_id', 231) # TODO: Find automatically somehow
        self.current_courses = self.sm.getOrPut('canvas_current_courses',self.request_current_courses())
        self.all_assignments = self.request_assignments()
        self.course_dict = self.sm.getOrPut('course_dict', {course['id']:course['name'].split(" - ")[-1] for course in self.current_courses})

    def request_current_courses(self):
        url = "https://canvas.seattlecolleges.edu/api/v1/courses"
        all_courses = self.request(url)
        current_courses = [course for course in all_courses if 'enrollment_term_id' in course.keys() and course['enrollment_term_id'] == self.termID]
        return current_courses

    def request_assignments(self):
        assignments = []
        for course in self.current_courses:
            # Gets all assignments
            assignments_url = f"https://canvas.seattlecolleges.edu/api/v1/courses/{course['id']}/assignments"
            for assignment in self.request(assignments_url):
                    if 'participation' not in assignment['name'].lower():
                        # gets my submissions
                        submissions_url = f"{assignments_url}/{assignment['id']}/submissions/{self.userID}"
                        assignment['submissions'] = self.request(submissions_url)[0]
                        assignments.append(Assignment(assignment))
        return assignments

    def request(self, url, params={}, request_type="GET"):
        headers = {
            "Authorization": "Bearer " + os.getenv("CANVAS_TOKEN")
        }

        results = []  # To store all the data from paginated requests

        while url:
            # Send the request
            if request_type == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif request_type == "POST":
                response = requests.post(url, headers=headers, json=params)
            else:
                raise ValueError(f"Unsupported request type: {request_type}")

            # Check for a successful response
            if response.status_code == 200:
                data = response.json()
                # Append the data to results
                if isinstance(data, list):
                    results.extend(data)
                else:
                    results.append(data)

                # Parse the 'Link' header to find the next page URL
                link_header = response.headers.get('Link', '')
                next_url = None
                for part in link_header.split(','):
                    if 'rel="next"' in part:
                        next_url = part[part.find('<') + 1:part.find('>')]
                        break
                url = next_url  # Update the URL for the next request
                params = {}  # Clear params for subsequent requests
            else:
                print(f"Error: {response.status_code}, {response.text}")
                break

        return results
