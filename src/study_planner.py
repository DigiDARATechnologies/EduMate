from datetime import datetime, timedelta
import re

class StudyPlanner:
    def generate_study_plan(self, hours, exam_date, subjects, user_request=""):
        """Generate a customized study plan based on user request."""
        try:
            # Parse exam date
            exam_date = datetime.strptime(exam_date, "%Y-%m-%d")
            today = datetime.utcnow()
            days_until_exam = (exam_date - today).days
            if days_until_exam < 1:
                raise ValueError("Exam date must be in the future.")

            # Parse user request for customizations
            priority_subject = None
            priority_match = re.search(r'prioritize\s+([\w\s]+)', user_request.lower())
            if priority_match:
                priority_subject = priority_match.group(1).strip()

            # Total hours per subject
            total_hours_per_subject = {}
            for subject in subjects:
                hours_match = re.search(rf'{subject.lower()}\s+(\d+)\s*hours', user_request.lower())
                if hours_match:
                    total_hours_per_subject[subject] = int(hours_match.group(1))
                else:
                    total_hours_per_subject[subject] = hours

            # Adjust hours if a subject is prioritized
            if priority_subject:
                priority_subject = next((s for s in subjects if s.lower() == priority_subject.lower()), None)
                if priority_subject:
                    # Allocate 60% of total hours to the priority subject
                    total_hours = sum(total_hours_per_subject.values())
                    priority_hours = int(total_hours * 0.6)
                    remaining_hours = total_hours - priority_hours
                    non_priority_subjects = [s for s in subjects if s != priority_subject]
                    for subject in subjects:
                        if subject == priority_subject:
                            total_hours_per_subject[subject] = priority_hours
                        else:
                            total_hours_per_subject[subject] = remaining_hours // len(non_priority_subjects)

            # Calculate daily hours
            daily_hours_per_subject = {}
            for subject in subjects:
                total_hours = total_hours_per_subject[subject]
                daily_hours = total_hours / days_until_exam if days_until_exam > 0 else total_hours
                daily_hours_per_subject[subject] = round(daily_hours, 1)

            # Generate the study plan
            plan = f"Study Plan for {', '.join(subjects)} until {exam_date.strftime('%Y-%m-%d')}:\n"
            for subject in subjects:
                total_hours = total_hours_per_subject[subject]
                daily_hours = daily_hours_per_subject[subject]
                plan += f"- {subject}: {total_hours} hours over {days_until_exam} days\n"
                plan += f"  Daily: {daily_hours} hours\n"

            return plan
        except Exception as e:
            raise Exception(f"Error generating study plan: {str(e)}")