import json
import os
import re

class RoadmapGenerator:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.roadmap_templates_dir = os.path.join(self.base_dir, 'data', 'roadmap_templates')

    def generate_roadmap(self, subject, user_year, department, user_request=""):
        """Generate a customized learning roadmap based on user request."""
        try:
            # Parse user request for customizations
            difficulty = "beginner"
            if "intermediate" in user_request.lower():
                difficulty = "intermediate"
            elif "advanced" in user_request.lower():
                difficulty = "advanced"

            focus_area = None
            if "web development" in user_request.lower():
                focus_area = "web development"
            elif "data science" in user_request.lower():
                focus_area = "data science"
            elif "automation" in user_request.lower():
                focus_area = "automation"

            timeline = "default"
            weeks_match = re.search(r'(\d+)\s*weeks', user_request.lower())
            if weeks_match:
                timeline = int(weeks_match.group(1))

            # Load template if available
            template_path = os.path.join(self.roadmap_templates_dir, f"{department.lower()}_sem{user_year}.json")
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    template = json.load(f)
            else:
                template = {"subjects": [subject], "topics": ["Basics", "Intermediate", "Advanced"]}

            # Generate customized roadmap
            if subject.lower() == "python":
                roadmap = self._generate_python_roadmap(user_year, department, difficulty, focus_area, timeline)
            else:
                roadmap = (
                    "=======================================\n"
                    f"🚀 {subject} Learning Roadmap (Year {user_year}, {department})\n"
                    "=======================================\n\n"
                )
                if subject in template.get("subjects", []):
                    topics = template.get("topics", ["Basics", "Intermediate", "Advanced"])
                    for i, topic in enumerate(topics, 1):
                        roadmap += f"🌟 Phase {i}: {topic}\n"
                        roadmap += "----------------------------------------\n"
                        roadmap += f"• Learn core concepts related to {topic.lower()}.\n\n"
                else:
                    roadmap += "🌟 Phase 1: Basics\n"
                    roadmap += "----------------------------------------\n"
                    roadmap += "• Learn core concepts.\n\n"
                    roadmap += "🌟 Phase 2: Intermediate\n"
                    roadmap += "----------------------------------------\n"
                    roadmap += "• Build on foundational knowledge.\n\n"
                    roadmap += "🌟 Phase 3: Advanced\n"
                    roadmap += "----------------------------------------\n"
                    roadmap += "• Master advanced topics.\n"

            return roadmap
        except Exception as e:
            raise Exception(f"Error generating roadmap: {str(e)}")

    def _generate_python_roadmap(self, user_year, department, difficulty, focus_area, timeline):
        """Generate a customized Python roadmap."""
        # Adjust timeline: Default to 13 weeks if not specified
        if timeline == "default":
            total_weeks = 13
        else:
            total_weeks = timeline

        # Adjust phases based on timeline
        if total_weeks <= 4:
            phase_duration = total_weeks // 2
            phases = [
                (f"Phase 1: Getting Started (Weeks 1-{phase_duration})", 1),
                (f"Phase 2: Core Concepts (Weeks {phase_duration + 1}-{total_weeks})", phase_duration + 1)
            ]
        elif total_weeks <= 8:
            phase_duration = total_weeks // 3
            phases = [
                (f"Phase 1: Getting Started (Weeks 1-{phase_duration})", 1),
                (f"Phase 2: Core Concepts (Weeks {phase_duration + 1}-{phase_duration * 2})", phase_duration + 1),
                (f"Phase 3: Intermediate Skills (Weeks {phase_duration * 2 + 1}-{total_weeks})", phase_duration * 2 + 1)
            ]
        else:
            phase_duration = total_weeks // 5
            phases = [
                (f"Phase 1: Getting Started (Weeks 1-{phase_duration})", 1),
                (f"Phase 2: Core Concepts (Weeks {phase_duration + 1}-{phase_duration * 2})", phase_duration + 1),
                (f"Phase 3: Intermediate Skills (Weeks {phase_duration * 2 + 1}-{phase_duration * 3})", phase_duration * 2 + 1),
                (f"Phase 4: Advanced Topics (Weeks {phase_duration * 3 + 1}-{phase_duration * 4})", phase_duration * 3 + 1),
                (f"Phase 5: Real-World Applications (Weeks {phase_duration * 4 + 1}-{total_weeks})", phase_duration * 4 + 1)
            ]

        # Base roadmap content
        roadmap_content = {
            "Phase 1": {
                "beginner": [
                    "• Setup: Install Python (latest version) and an IDE like VS Code or PyCharm.",
                    "• Basics: Learn syntax, variables, data types (int, float, string, list, dict), and basic I/O.",
                    "• Control Flow: Understand if-else statements, loops (for, while), and basic error handling (try-except).",
                    "• Practice:\n  - Solve simple problems like calculating a factorial.\n  - Check if a number is prime."
                ],
                "intermediate": [
                    "• Setup: Ensure Python and an IDE are installed, and explore virtual environments.",
                    "• Basics: Review syntax, variables, and data types with a focus on practical use cases.",
                    "• Control Flow: Dive deeper into nested loops and exception handling.",
                    "• Practice:\n  - Write a program to generate Fibonacci sequence.\n  - Create a simple number guessing game."
                ],
                "advanced": [
                    "• Setup: Configure Python with advanced tools like linters and debuggers.",
                    "• Basics: Optimize code with best practices for variables and data types.",
                    "• Control Flow: Master complex logic with nested conditions and custom exceptions.",
                    "• Practice:\n  - Build a recursive factorial calculator.\n  - Implement a prime number sieve algorithm."
                ]
            },
            "Phase 2": {
                "beginner": [
                    "• Functions: Define functions, use parameters, return values, and explore lambda functions.",
                    "• Data Structures: Dive into lists, tuples, sets, and dictionaries—learn methods like append, pop, and get.",
                    "• File Handling: Read/write text files, work with CSV files, and understand basic file operations.",
                    "• Practice:\n  - Build a to-do list app.\n  - Create a simple text-based game."
                ],
                "intermediate": [
                    "• Functions: Use advanced function concepts like default arguments and *args/**kwargs.",
                    "• Data Structures: Explore nested data structures and their methods.",
                    "• File Handling: Work with JSON files and handle file exceptions.",
                    "• Practice:\n  - Create a contact book app.\n  - Build a file-based quiz game."
                ],
                "advanced": [
                    "• Functions: Implement closures and decorators for advanced functionality.",
                    "• Data Structures: Use advanced structures like heaps and priority queues.",
                    "• File Handling: Handle large files with buffering and streaming.",
                    "• Practice:\n  - Create a memoized function for Fibonacci.\n  - Build a file parser for log analysis."
                ]
            },
            "Phase 3": {
                "beginner": [
                    "• OOP: Learn object-oriented programming—classes, objects, inheritance, polymorphism, and encapsulation.",
                    "• Modules & Libraries: Use built-in modules (math, datetime) and install external libraries (e.g., requests, pandas) via pip.",
                    "• Error Handling: Master try-except-else-finally and create custom exceptions.",
                    "• Practice:\n  - Create a basic calculator.\n  - Build a simple API client using requests."
                ],
                "intermediate": [
                    "• OOP: Explore advanced OOP concepts like abstract classes and method overriding.",
                    "• Modules & Libraries: Use libraries like NumPy for numerical computations.",
                    "• Error Handling: Implement logging with custom exceptions.",
                    "• Practice:\n  - Build a budget tracker using OOP.\n  - Create a weather app with an API."
                ],
                "advanced": [
                    "• OOP: Use design patterns like Singleton and Factory.",
                    "• Modules & Libraries: Integrate advanced libraries like TensorFlow for ML.",
                    "• Error Handling: Build robust error handling with logging and monitoring.",
                    "• Practice:\n  - Create a plugin system using OOP.\n  - Build an ML model API client."
                ]
            },
            "Phase 4": {
                "beginner": [
                    "• Advanced Data Structures: Explore list comprehensions, generators, and decorators.",
                    "• Concurrency: Understand threading, multiprocessing, and async/await for basic parallel tasks.",
                    "• Databases: Connect to SQLite or MySQL, perform CRUD operations, and use an ORM like SQLAlchemy.",
                    "• Practice:\n  - Build a web scraper.\n  - Create a small Flask app."
                ],
                "intermediate": [
                    "• Advanced Data Structures: Use generators and comprehensions for memory efficiency.",
                    "• Concurrency: Implement async I/O for network tasks.",
                    "• Databases: Work with NoSQL databases like MongoDB.",
                    "• Practice:\n  - Scrape and store data in a database.\n  - Build a REST API with Flask."
                ],
                "advanced": [
                    "• Advanced Data Structures: Implement custom data structures like tries.",
                    "• Concurrency: Use advanced concurrency patterns like worker pools.",
                    "• Databases: Optimize queries and use database indexing.",
                    "• Practice:\n  - Build a distributed web scraper.\n  - Create a scalable Flask app with load balancing."
                ]
            },
            "Phase 5": {
                "beginner": [
                    "• Frameworks: Learn Flask or Django for web development, and create a simple web app.",
                    "• Data Science: If interested, explore NumPy, pandas, and matplotlib for data analysis.",
                    "• Automation: Write scripts to automate tasks (e.g., file organization, email sending).",
                    "• Contribute: Join open-source Python projects on GitHub to gain experience."
                ],
                "intermediate": [
                    "• Frameworks: Build a full-stack app with Django and PostgreSQL.",
                    "• Data Science: Perform data analysis with pandas and visualize with seaborn.",
                    "• Automation: Automate workflows with APIs (e.g., Google Sheets API).",
                    "• Contribute: Contribute to intermediate-level open-source projects."
                ],
                "advanced": [
                    "• Frameworks: Deploy a production-ready app with Django, Docker, and AWS.",
                    "• Data Science: Build ML models with scikit-learn and deploy them.",
                    "• Automation: Create a CI/CD pipeline for automation.",
                    "• Contribute: Lead an open-source project or mentor others."
                ]
            }
        }

        # Adjust Phase 5 based on focus area
        if focus_area:
            phase_5_content = {
                "web development": [
                    "• Frameworks: Learn Flask or Django and build a full web app with user authentication.",
                    "• Frontend: Integrate HTML, CSS, and JavaScript for a dynamic UI.",
                    "• Deployment: Deploy your app using Heroku or AWS.",
                    "• Practice:\n  - Create a blog app.\n  - Add user login/logout features."
                ],
                "data science": [
                    "• Data Science: Master NumPy, pandas, and matplotlib for data analysis.",
                    "• ML Basics: Learn scikit-learn for machine learning basics.",
                    "• Visualization: Use seaborn and plotly for advanced visualizations.",
                    "• Practice:\n  - Analyze a dataset (e.g., Titanic dataset).\n  - Build a simple ML model."
                ],
                "automation": [
                    "• Automation: Write scripts to automate repetitive tasks (e.g., file organization, email sending).",
                    "• APIs: Use APIs to automate workflows (e.g., Google Sheets API).",
                    "• Scheduling: Schedule tasks with tools like cron or APScheduler.",
                    "• Practice:\n  - Automate file backups.\n  - Send automated email reminders."
                ]
            }
            if "Phase 5" in roadmap_content and focus_area in phase_5_content:
                roadmap_content["Phase 5"][difficulty] = phase_5_content[focus_area]

        # Build the roadmap
        roadmap = (
            "=======================================\n"
            f"🚀 Python Learning Roadmap (Year {user_year}, {department})\n"
            "=======================================\n\n"
        )

        for phase_name, _ in phases:
            phase_key = phase_name.split(":")[0]
            roadmap += f"🌟 {phase_name}\n"
            roadmap += "----------------------------------------\n"
            for item in roadmap_content[phase_key][difficulty]:
                roadmap += f"{item}\n"
            roadmap += "\n"

        roadmap += (
            "🎯 Pro Tips\n"
            "----------------------------------------\n"
            "• Code daily to build muscle memory.\n"
            "• Use resources like Python’s official docs.\n"
            "• Join communities like Reddit’s r/learnpython for support.\n"
        )

        return roadmap