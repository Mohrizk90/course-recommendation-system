import csv
from experta import *
import re

class StudentInfo(Fact):
    """Fact to store student information"""
    pass

class Course(Fact):
    """Fact to store course information"""
    pass

class Recommendation(Fact):
    """Fact to store course recommendations"""
    pass

class CourseRecommendationSystem(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.courses = []
        self.recommended_courses = []
        self.total_credits = 0
        self.max_credits = 0
        self.student_data = {}
        self.skipped_courses = []
        
    def load_courses_from_csv(self, filename):
        """Load courses from CSV file"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Clean and process the data
                    course = {
                        'code': row['Course Code'].strip(),
                        'name': row['Course Name'].strip(),
                        'description': row['Description'].strip(),
                        'prerequisites': self._parse_course_list(row['Prerequisites']),
                        'corequisites': self._parse_course_list(row['Co-requisites']),
                        'credit_hours': int(row['Credit Hours']) if row['Credit Hours'].strip() else 0,
                        'semester_offered': row['Semester Offered'].strip(),
                        'program_track': row['Program/Track'].strip()
                    }
                    self.courses.append(course)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return False
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
        return True
    
    def _parse_course_list(self, course_string):
        """Parse comma-separated course codes"""
        if not course_string or course_string.strip() == '' or course_string.strip().lower() == 'none':
            return []
        return [code.strip() for code in course_string.split(',') if code.strip()]
    
    def _is_track_eligible(self, program_track):
        """Check if course is eligible for Computer Engineering track"""
        track_lower = program_track.lower()
        return 'all' in track_lower or 'computer engineering' in track_lower
    
    def _is_semester_eligible(self, semester_offered, current_semester):
        """Check if course is offered in current semester"""
        return (semester_offered.lower() == current_semester.lower() or 
                semester_offered.lower() == 'both')
    
    def _has_prerequisites(self, prerequisites, passed_courses):
        """Check if student has completed all prerequisites"""
        return all(prereq in passed_courses for prereq in prerequisites)
    
    def _has_corequisites(self, corequisites, passed_courses, current_recommendations):
        """Check if corequisites are satisfied (passed or being taken concurrently)"""
        for coreq in corequisites:
            if coreq not in passed_courses and coreq not in current_recommendations:
                return False
        return True
    
    @Rule(StudentInfo(cgpa=MATCH.cgpa))
    def set_credit_limit(self, cgpa):
        """Set maximum credit hours based on CGPA"""
        if cgpa < 2.0:
            self.max_credits = 12
        elif cgpa <= 3.0:
            self.max_credits = 15
        else:
            self.max_credits = 18
        
        print(f"Maximum credit hours allowed: {self.max_credits}")
    
    @Rule(StudentInfo(cgpa=MATCH.cgpa, 
                     semester=MATCH.semester, 
                     passed_courses=MATCH.passed, 
                     failed_courses=MATCH.failed))
    def recommend_courses(self, cgpa, semester, passed, failed):
        """Main rule to recommend courses"""
        print("\n=== COURSE ANALYSIS ===")
        
        for course in self.courses:
            course_code = course['code']
            course_name = course['name']
            credit_hours = course['credit_hours']
            
            # Skip if already passed
            if course_code in passed:
                continue
                
            # Skip if currently failed (might need retaking)
            if course_code in failed:
                self.skipped_courses.append({
                    'code': course_code,
                    'name': course_name,
                    'reason': 'Course previously failed - may need retaking'
                })
                continue
            
            # Check track eligibility
            if not self._is_track_eligible(course['program_track']):
                self.skipped_courses.append({
                    'code': course_code,
                    'name': course_name,
                    'reason': f"Track mismatch - {course['program_track']}"
                })
                continue
            
            # Check semester eligibility
            if not self._is_semester_eligible(course['semester_offered'], semester):
                self.skipped_courses.append({
                    'code': course_code,
                    'name': course_name,
                    'reason': f"Not offered in {semester} semester"
                })
                continue
            
            # Check prerequisites
            if not self._has_prerequisites(course['prerequisites'], passed):
                missing_prereqs = [p for p in course['prerequisites'] if p not in passed]
                self.skipped_courses.append({
                    'code': course_code,
                    'name': course_name,
                    'reason': f"Missing prerequisites: {', '.join(missing_prereqs)}"
                })
                continue
            
            # Check corequisites
            current_recommendation_codes = [r['code'] for r in self.recommended_courses]
            if not self._has_corequisites(course['corequisites'], passed, current_recommendation_codes):
                missing_coreqs = [c for c in course['corequisites'] 
                                if c not in passed and c not in current_recommendation_codes]
                self.skipped_courses.append({
                    'code': course_code,
                    'name': course_name,
                    'reason': f"Missing corequisites: {', '.join(missing_coreqs)}"
                })
                continue
            
            # Check credit limit
            if self.total_credits + credit_hours > self.max_credits:
                self.skipped_courses.append({
                    'code': course_code,
                    'name': course_name,
                    'reason': f"Would exceed credit limit ({self.total_credits + credit_hours} > {self.max_credits})"
                })
                continue
            
            # Course is eligible - add to recommendations
            self.recommended_courses.append({
                'code': course_code,
                'name': course_name,
                'credit_hours': credit_hours
            })
            self.total_credits += credit_hours
            
            print(f"✓ RECOMMENDED: {course_code} - {course_name} ({credit_hours} credits)")
    
    def get_student_input(self):
        """Get student information from user input"""
        print("=== University Course Recommendation System ===\n")
        
        # Get CGPA
        while True:
            try:
                cgpa = float(input("Enter your CGPA (0.0 - 4.0): "))
                if 0.0 <= cgpa <= 4.0:
                    break
                else:
                    print("CGPA must be between 0.0 and 4.0")
            except ValueError:
                print("Please enter a valid number")
        
        # Get semester
        while True:
            semester = input("Enter current semester (Fall/Spring/Summer): ").strip()
            if semester.lower() in ['fall', 'spring', 'summer']:
                break
            else:
                print("Please enter Fall, Spring, or Summer")
        
        # Get passed courses
        print("\nEnter passed courses (comma-separated, or press Enter for none):")
        passed_input = input().strip()
        passed_courses = [course.strip() for course in passed_input.split(',') if course.strip()] if passed_input else []
        
        # Get failed courses
        print("\nEnter failed courses (comma-separated, or press Enter for none):")
        failed_input = input().strip()
        failed_courses = [course.strip() for course in failed_input.split(',') if course.strip()] if failed_input else []
        
        return cgpa, semester, passed_courses, failed_courses
    
    def run_recommendation(self, cgpa=None, semester=None, passed_courses=None, failed_courses=None):
        """Run the recommendation system"""
        # Reset state
        self.recommended_courses = []
        self.total_credits = 0
        self.max_credits = 0
        self.skipped_courses = []
        
        # Get input from user or use provided parameters
        if cgpa is None:
            cgpa, semester, passed_courses, failed_courses = self.get_student_input()
        
        print(f"\n=== STUDENT PROFILE ===")
        print(f"CGPA: {cgpa}")
        print(f"Semester: {semester}")
        print(f"Passed Courses: {passed_courses}")
        print(f"Failed Courses: {failed_courses}")
        
        # Declare facts
        self.declare(StudentInfo(
            cgpa=cgpa,
            semester=semester,
            passed_courses=passed_courses,
            failed_courses=failed_courses
        ))
        
        # Run the engine
        self.run()
        
        # Display results
        self.display_results()
    
    def display_results(self):
        """Display recommendation results"""
        print(f"\n=== COURSE RECOMMENDATIONS ===")
        
        if self.recommended_courses:
            print(f"Recommended courses for this semester:")
            for course in self.recommended_courses:
                print(f"• {course['code']} - {course['name']} ({course['credit_hours']} credits)")
            print(f"\nTotal recommended credits: {self.total_credits}/{self.max_credits}")
        else:
            print("No courses can be recommended for this semester.")
        
        if self.skipped_courses:
            print(f"\n=== COURSES NOT RECOMMENDED ===")
            for course in self.skipped_courses:
                print(f"• {course['code']} - {course['name']}")
                print(f"  Reason: {course['reason']}")

def run_test_case():
    """Run the test case as specified"""
    print("=== RUNNING TEST CASE ===")
    system = CourseRecommendationSystem()
    
    # Load courses from CSV
    if not system.load_courses_from_csv('CE_Cloud.csv'):
        print("Failed to load course data")
        return
    
    # Run test case
    system.run_recommendation(
        cgpa=3.2,
        semester="Fall",
        passed_courses=["MAT111", "CSE014"],
        failed_courses=[]
    )

def main():
    """Main function"""
    system = CourseRecommendationSystem()
    
    # Load courses from CSV
    if not system.load_courses_from_csv('CE_Cloud.csv'):
        print("Failed to load course data")
        return
    
    print(f"Loaded {len(system.courses)} courses from CSV file.\n")
    
    while True:
        print("\n" + "="*50)
        print("1. Get course recommendations")
        print("2. Run test case (CGPA: 3.2, Semester: Fall, Passed: MAT111, CSE014)")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            system.run_recommendation()
        elif choice == '2':
            run_test_case()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()