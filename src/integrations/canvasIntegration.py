import requests, os

class CanvasIntegration:

    base_url = "https://canvas.seattlecolleges.edu/api/v1/"
    list_courses = base_url+"courses"
    get_todo = base_url+"users/self/todo"

    def __init__(self):
        self.userID = 2233 # TODO: find automatically / user input
        self.termID = 231 # TODO: Find automatically somehow
        self.current_courses = self.request_current_courses()
        self.all_assignments = self.request_assignments()
        self.course_dict = {course['id']:course['name'].split(" - ")[-1] for course in self.current_courses}

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
