import requests, os, json

class CanvasIntegration:


    def __init__(self):

        self.base_url = f"https://{self.load_instance_url()}/api/v1"
        self.userID = self.request_canvas_id()
        self.all_courses = self.get_all_courses()
        self.termID = self.get_current_term_id()
        self.current_courses = self.request_current_courses()
        self.all_assignments = self.request_assignments()
        self.course_dict = {course['id']:course['name'].split(" - ")[-1] for course in self.current_courses}

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
        return self.request(url)

    def get_all_courses(self):
        url = f"{self.base_url}/courses"
        return self.request(url)

    def request_current_courses(self):
        url = f"{self.base_url}/courses"
        all_courses = self.request(url)
        current_courses = [course for course in all_courses if 'enrollment_term_id' in course.keys() and course['enrollment_term_id'] == self.termID]
        return current_courses

    def request_canvas_id(self):
        url = f"{self.base_url}/users/self"
        return self.request(url)[0]['id']

    def request_assignments(self):
        assignments = []
        for course in self.current_courses:
            # Gets all assignments
            assignments_url = f"{self.base_url}/courses/{course['id']}/assignments"
            for assignment in self.request(assignments_url):
                    if 'participation' not in assignment['name'].lower():
                        # gets my submissions
                        submissions_url = f"{assignments_url}/{assignment['id']}/submissions/{self.userID}"
                        assignment['submissions'] = self.request(submissions_url)[0]
                        assignments.append(assignment)
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
