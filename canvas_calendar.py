import requests
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import os
from dotenv import load_dotenv
import json
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class CanvasCalendar:
    def __init__(self, access_token=None):
        # Load environment variables
        load_dotenv()
        self.canvas_url = os.getenv('CANVAS_URL')
        
        # Use provided access token or fall back to environment variable
        self.api_token = access_token or os.getenv('CANVAS_API_TOKEN')
        
        # Validate environment variables
        if not self.api_token:
            logger.error("No access token provided")
            raise ValueError("Access token is required")
        if not self.canvas_url:
            logger.error("CANVAS_URL is not set")
            raise ValueError("CANVAS_URL environment variable is not set")
            
        logger.info(f"Using Canvas URL: {self.canvas_url}")
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        self.assignments = []
        self.start_date = datetime(2025, 4, 1)  # Only show Spring 2025 assignments

    def get_assignments(self):
        """Get all assignments and their due dates using Canvas API"""
        try:
            print("Fetching assignments from Canvas API...")
            
            # First, get all courses
            courses_response = requests.get(
                f"{self.canvas_url}/api/v1/courses",
                headers=self.headers
            )
            courses_response.raise_for_status()
            courses = courses_response.json()
            
            print(f"Found {len(courses)} courses")
            
            # Get assignments for each course
            for course in courses:
                try:
                    course_id = course['id']
                    course_name = course.get('name', 'Unknown Course')
                    
                    # Get assignments for this course
                    assignments_response = requests.get(
                        f"{self.canvas_url}/api/v1/courses/{course_id}/assignments",
                        headers=self.headers
                    )
                    assignments_response.raise_for_status()
                    assignments = assignments_response.json()
                    
                    # Process each assignment
                    for assignment in assignments:
                        if assignment.get('due_at'):  # Only include assignments with due dates
                            due_date = datetime.strptime(
                                assignment['due_at'], 
                                '%Y-%m-%dT%H:%M:%SZ'
                            )
                            
                            # Only include assignments from March 20th onwards
                            if due_date >= self.start_date:
                                self.assignments.append({
                                    'course': course_name,
                                    'title': assignment['name'],
                                    'due_date': due_date,
                                    'description': assignment.get('description', ''),
                                    'points_possible': assignment.get('points_possible', 0)
                                })
                    
                except Exception as e:
                    print(f"Error fetching assignments for course {course_name}: {e}")
                    continue
            
            # Sort assignments by due date
            self.assignments.sort(key=lambda x: x['due_date'])
            print(f"Successfully fetched {len(self.assignments)} assignments from March 20th onwards")
            return self.assignments
            
        except Exception as e:
            print(f"Error getting assignments: {e}")
            return []

    def display_weekly_assignments(self):
        """Display assignments grouped by week"""
        if not self.assignments:
            print("No assignments found")
            return

        # Group assignments by week
        weekly_assignments = defaultdict(list)
        for assignment in self.assignments:
            # Get the start of the week (Monday)
            due_date = assignment['due_date']
            week_start = due_date - timedelta(days=due_date.weekday())
            weekly_assignments[week_start].append(assignment)

        # Display assignments by week
        print("\nWeekly Assignment Schedule:")
        print("=" * 50)
        
        for week_start in sorted(weekly_assignments.keys()):
            week_end = week_start + timedelta(days=6)
            print(f"\nWeek of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d')}")
            print("-" * 50)
            
            # Sort assignments within the week by due date
            week_assignments = sorted(weekly_assignments[week_start], key=lambda x: x['due_date'])
            
            for assignment in week_assignments:
                due_date = assignment['due_date']
                print(f"\nCourse: {assignment['course']}")
                print(f"Title: {assignment['title']}")
                print(f"Due: {due_date.strftime('%A, %B %d at %I:%M %p')}")
                if assignment['points_possible']:
                    print(f"Points: {assignment['points_possible']}")
                if assignment['description']:
                    print(f"Description: {assignment['description'][:100]}...")  # Show first 100 chars
                print("-" * 30)

    def create_calendar(self):
        """Create an iCalendar file from assignments"""
        cal = Calendar()
        cal.add('prodid', '-//Canvas Calendar//example.com//')
        cal.add('version', '2.0')
        
        for assignment in self.assignments:
            try:
                event = Event()
                event.add('summary', f"{assignment['course']}: {assignment['title']}")
                event.add('dtstart', assignment['due_date'])
                event.add('dtend', assignment['due_date'] + timedelta(hours=1))
                
                # Add more details to the description
                description = f"""
Course: {assignment['course']}
Assignment: {assignment['title']}
Points Possible: {assignment['points_possible']}
                """
                if assignment['description']:
                    description += f"\nDescription: {assignment['description']}"
                
                event.add('description', description)
                cal.add_component(event)
            except Exception as e:
                print(f"Error creating calendar event for {assignment.get('title', 'unknown')}: {e}")
                continue
        
        # Save calendar to file
        with open('canvas_calendar.ics', 'wb') as f:
            f.write(cal.to_ical())
        print("\nCalendar saved as canvas_calendar.ics")

def main():
    calendar = CanvasCalendar()
    
    try:
        assignments = calendar.get_assignments()
        if assignments:
            # Display weekly view
            calendar.display_weekly_assignments()
            
            # Create calendar file
            calendar.create_calendar()
        else:
            print("No assignments found")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 