import requests, os, dotenv
dotenv.load_dotenv()

class CanvasIntegration:

    base_url = "https://canvas.seattlecolleges.edu/api/v1/"
    list_courses = base_url+"courses"
    get_todo = base_url+"users/self/todo"

    def __init__(self):
        self.userID = 2233
        self.termID = 231
        self.current_courses = self.request_current_courses()
        self.all_assignments = self.request_assignments()
        self.course_dict = {course['id']:course['name'].split(" - ")[-1] for course in self.current_courses}

    def request_current_courses(self):
        url = "https://canvas.seattlecolleges.edu/api/v1/courses"
        all_courses = self.request(url)
        current_courses = [course for course in all_courses if course['enrollment_term_id'] == self.termID]
        return current_courses

    def request_assignments(self):
        assignments = []
        for course in self.current_courses:
            # Gets all assignments
            assignments_url = f"https://canvas.seattlecolleges.edu/api/v1/courses/{course['id']}/assignments"
            for assignment in self.request(assignments_url):
                # gets my submissions
                submissions_url = f"{assignments_url}/{assignment['id']}/submissions/{self.userID}"
                assignment['submissions'] = self.request(submissions_url)
                assignments.append(assignment)
        return assignments

    def request(self, url, params={}, request_type="GET"):
        params.update({
            "Authorization": "Bearer " + os.getenv("CANVAS_TOKEN")
        })

        response = "DERP"
        # Send the request
        if request_type == "GET":
            response = requests.get(url, headers=params)
        if request_type == "POST":
            response = requests.post(url, headers=params)

        # Print response
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")
