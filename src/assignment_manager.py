from datetime import datetime

class AssignmentManager:
    def __init__(self):
        self.assignments = []

    def add_assignment(self, title, due_date):
        self.assignments.append({
            "title": title,
            "due_date": due_date,
            "added_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    def view_assignments(self):
        if not self.assignments:
            return "No assignments found."
        result = "Your Assignments:\n"
        for assignment in self.assignments:
            result += f"- {assignment['title']} (Due: {assignment['due_date']}, Added: {assignment['added_at']})\n"
        return result