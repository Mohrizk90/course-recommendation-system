# --------------------------
# File: app.py
# --------------------------

import streamlit as st
import pandas as pd
from pathlib import Path
import os
import csv
from experta import *

# --------------------------
# EXPERT SYSTEM CLASSES
# --------------------------
class StudentInfo(Fact):
    """Fact to store student information"""
    pass

class Course(Fact):
    """Fact to store course information"""
    pass

class Recommendation(Fact):
    """Fact to store course recommendations"""
    pass

class Explanation(Fact):
    """Fact to store explanation for recommendations"""
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
        self.explanations = []  # Store detailed explanations
        
    def load_courses_from_dataframe(self, df):
        """Load courses from pandas DataFrame"""
        self.courses = []
        for _, row in df.iterrows():
            course = {
                'code': str(row['Course Code']).strip() if pd.notna(row['Course Code']) else '',
                'name': str(row['Course Name']).strip() if pd.notna(row['Course Name']) else '',
                'description': str(row['Description']).strip() if pd.notna(row['Description']) else '',
                'prerequisites': self._parse_course_list(row['Prerequisites']),
                'corequisites': self._parse_course_list(row['Co-requisites']),
                'credit_hours': int(row['Credit Hours']) if pd.notna(row['Credit Hours']) else 0,
                'semester_offered': str(row['Semester Offered']).strip() if pd.notna(row['Semester Offered']) else '',
                'program_track': str(row['Program/Track']).strip() if pd.notna(row['Program/Track']) else ''
            }
            self.courses.append(course)
    
    def _parse_course_list(self, course_string):
        """Parse comma-separated course codes"""
        if pd.isna(course_string) or str(course_string).strip() == '' or str(course_string).strip().lower() == 'none':
            return []
        return [code.strip() for code in str(course_string).split(',') if code.strip()]
    
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
    
    def _generate_explanation(self, course, reason_type, details=None):
        """Generate a detailed explanation for a course recommendation or restriction"""
        explanation = {
            'code': course['code'],
            'name': course['name'],
            'type': reason_type,
            'details': details or {}
        }
        self.explanations.append(explanation)
        return explanation

    def _add_recommendation_explanation(self, course, passed_courses):
        """Add detailed explanation for a recommended course"""
        details = {
            'prerequisites_met': [prereq for prereq in course['prerequisites'] if prereq in passed_courses],
            'corequisites_met': [coreq for coreq in course['corequisites'] if coreq in passed_courses],
            'semester_match': course['semester_offered'],
            'track_match': course['program_track']
        }
        return self._generate_explanation(course, 'recommended', details)

    def _add_restriction_explanation(self, course, reason, details=None):
        """Add detailed explanation for a restricted course"""
        return self._generate_explanation(course, 'restricted', {
            'reason': reason,
            **(details or {})
        })

    @Rule(StudentInfo(cgpa=MATCH.cgpa, 
                     semester=MATCH.semester, 
                     passed_courses=MATCH.passed, 
                     failed_courses=MATCH.failed))
    def recommend_courses(self, cgpa, semester, passed, failed):
        """Main rule to recommend courses"""
        for course in self.courses:
            course_code = course['code']
            course_name = course['name']
            credit_hours = course['credit_hours']
            
            # Skip if already passed
            if course_code in passed:
                self._add_restriction_explanation(course, 'already_passed', {
                    'semester_passed': 'Previously completed'
                })
                continue
                
            # Skip if currently failed (might need retaking)
            if course_code in failed:
                self._add_restriction_explanation(course, 'previously_failed', {
                    'priority': 'high',
                    'action_needed': 'Consider retaking'
                })
                self.skipped_courses.append({
                    'code': course_code,
                    'name': course_name,
                    'reason': 'Course previously failed - may need retaking'
                })
                continue
            
            # Check track eligibility
            if not self._is_track_eligible(course['program_track']):
                self._add_restriction_explanation(course, 'track_mismatch', {
                    'current_track': 'Computer Engineering',
                    'course_track': course['program_track']
                })
                self.skipped_courses.append({
                    'code': course_code,
                    'name': course_name,
                    'reason': f"Track mismatch - {course['program_track']}"
                })
                continue
            
            # Check semester eligibility
            if not self._is_semester_eligible(course['semester_offered'], semester):
                self._add_restriction_explanation(course, 'semester_mismatch', {
                    'current_semester': semester,
                    'offered_semester': course['semester_offered']
                })
                self.skipped_courses.append({
                    'code': course_code,
                    'name': course_name,
                    'reason': f"Not offered in {semester} semester"
                })
                continue
            
            # Check prerequisites
            if not self._has_prerequisites(course['prerequisites'], passed):
                missing_prereqs = [p for p in course['prerequisites'] if p not in passed]
                self._add_restriction_explanation(course, 'missing_prerequisites', {
                    'missing_courses': missing_prereqs,
                    'required_courses': course['prerequisites']
                })
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
                self._add_restriction_explanation(course, 'missing_corequisites', {
                    'missing_courses': missing_coreqs,
                    'required_courses': course['corequisites']
                })
                self.skipped_courses.append({
                    'code': course_code,
                    'name': course_name,
                    'reason': f"Missing corequisites: {', '.join(missing_coreqs)}"
                })
                continue
            
            # Check credit limit
            if self.total_credits + credit_hours > self.max_credits:
                self._add_restriction_explanation(course, 'credit_limit', {
                    'current_credits': self.total_credits,
                    'course_credits': credit_hours,
                    'max_credits': self.max_credits
                })
                self.skipped_courses.append({
                    'code': course_code,
                    'name': course_name,
                    'reason': f"Would exceed credit limit ({self.total_credits + credit_hours} > {self.max_credits})"
                })
                continue
            
            # Course is eligible - add to recommendations with explanation
            self.recommended_courses.append({
                'code': course_code,
                'name': course_name,
                'credit_hours': credit_hours
            })
            self.total_credits += credit_hours
            self._add_recommendation_explanation(course, passed)
    
    def get_recommendations(self, cgpa, semester, passed_courses, failed_courses):
        """Get course recommendations"""
        # Reset state
        self.recommended_courses = []
        self.total_credits = 0
        self.max_credits = 0
        self.skipped_courses = []
        
        # Declare facts
        self.declare(StudentInfo(
            cgpa=cgpa,
            semester=semester,
            passed_courses=passed_courses,
            failed_courses=failed_courses
        ))
        
        # Run the engine
        self.run()
        
        return self.recommended_courses, self.skipped_courses, self.total_credits, self.max_credits, self.explanations

# --------------------------
# ADVISOR FUNCTION
# --------------------------
def run_advisor(cgpa, semester, passed, failed, kb_df):
    """Run the course advisor and return recommendations"""
    system = CourseRecommendationSystem()
    system.load_courses_from_dataframe(kb_df)
    
    recommendations, skipped_courses, total_credits, max_credits, explanations = system.get_recommendations(
        cgpa, semester, passed, failed
    )
    
    return recommendations, skipped_courses, total_credits, max_credits, explanations

# --------------------------
# CONFIGURATION
# --------------------------
KB_FILE = os.getenv('KB_FILE', 'CE_Cloud.csv')
MAX_CREDITS = 18  # General advisory warning limit

# --------------------------
# LOAD KNOWLEDGE BASE
# --------------------------
@st.cache_data
def load_kb():
    file_path = Path(KB_FILE)
    if not file_path.exists():
        raise FileNotFoundError(f"Knowledge base file '{KB_FILE}' not found.")

    df = pd.read_csv(file_path)
    df.columns = [col.strip() for col in df.columns]

    # Drop rows with missing or non-numeric credit hours
    df = df[pd.to_numeric(df['Credit Hours'], errors='coerce').notna()]
    df['Credit Hours'] = df['Credit Hours'].astype(int)

    if df.empty:
        raise ValueError("The knowledge base file is empty.")

    return df

try:
    kb_df = load_kb()
except Exception as e:
    st.error(f"❌ Failed to load knowledge base: {e}")
    st.stop()

# --------------------------
# UI - HEADER
# --------------------------
st.title("📘 AIU Course Registration Advisor")
st.subheader("🎓 Cloud Computing Track")

# Display system info
st.info(f"📊 Knowledge Base: {len(kb_df)} courses loaded from {KB_FILE}")

# --------------------------
# SIDEBAR - STUDENT INPUT
# --------------------------
st.sidebar.header("🧑‍🎓 Student Information")

cgpa = st.sidebar.number_input("Enter your CGPA", min_value=0.0, max_value=4.0, step=0.01, value=0.0)
semester = st.sidebar.selectbox("Current Semester", ["Fall", "Spring", "Summer"])

all_courses = kb_df['Course Code'].dropna().unique().tolist()
passed = st.sidebar.multiselect("✅ Passed Courses", options=all_courses)
failed = st.sidebar.multiselect("❌ Failed Courses", options=[c for c in all_courses if c not in passed])

# Credit limit info based on CGPA
if cgpa > 0:
    if cgpa < 2.0:
        credit_limit = 12
    elif cgpa <= 3.0:
        credit_limit = 15
    else:
        credit_limit = 18
    st.sidebar.info(f"📊 Your credit limit: {credit_limit} hours (based on CGPA: {cgpa})")

# Show test case button
if st.sidebar.button("🧪 Load Test Case"):
    st.session_state.test_cgpa = 3.2
    st.session_state.test_semester = "Fall"
    st.session_state.test_passed = ["MAT111", "CSE014"]
    st.session_state.test_failed = []

# Apply test case if loaded
if hasattr(st.session_state, 'test_cgpa'):
    cgpa = st.session_state.test_cgpa
    semester = st.session_state.test_semester
    passed = st.session_state.test_passed
    failed = st.session_state.test_failed
    st.sidebar.success("🧪 Test case loaded!")

# --------------------------
# MAIN - RECOMMENDATION SECTION
# --------------------------
if st.sidebar.button("Get Recommendations") or cgpa > 0:
    if not (0.0 <= cgpa <= 4.0):
        st.error("❌ CGPA must be between 0.0 and 4.0")
    elif cgpa == 0.0:
        st.warning("⚠️ Please enter your CGPA to get recommendations")
    else:
        with st.spinner("🔄 Analyzing courses and generating recommendations..."):
            try:
                # Create expert system instance
                system = CourseRecommendationSystem()
                system.load_courses_from_dataframe(kb_df)
                
                # Get recommendations with explanations
                recommendations, skipped_courses, total_credits, max_credits, explanations = run_advisor(
                    cgpa, semester, passed, failed, kb_df
                )
                
                if not recommendations:
                    st.warning("⚠️ No courses could be recommended based on your profile and university rules.")
                    
                    # Show detailed explanations for skipped courses
                    if explanations:
                        st.subheader("📋 Course Analysis")
                        for exp in explanations:
                            if exp['type'] == 'restricted':
                                with st.expander(f"❌ {exp['code']} - {exp['name']}"):
                                    if exp['details']['reason'] == 'already_passed':
                                        st.success(f"✅ Course already completed")
                                    elif exp['details']['reason'] == 'previously_failed':
                                        st.warning(f"⚠️ Course previously failed - Consider retaking")
                                        st.write("**Priority:** High")
                                    elif exp['details']['reason'] == 'track_mismatch':
                                        st.error(f"❌ Track mismatch")
                                        st.write(f"**Required Track:** {exp['details']['course_track']}")
                                    elif exp['details']['reason'] == 'semester_mismatch':
                                        st.error(f"❌ Not offered this semester")
                                        st.write(f"**Offered in:** {exp['details']['offered_semester']}")
                                    elif exp['details']['reason'] == 'missing_prerequisites':
                                        st.error(f"❌ Missing prerequisites")
                                        st.write("**Required Courses:**")
                                        for course in exp['details']['required_courses']:
                                            st.write(f"- {course}")
                                    elif exp['details']['reason'] == 'missing_corequisites':
                                        st.error(f"❌ Missing corequisites")
                                        st.write("**Required Courses:**")
                                        for course in exp['details']['required_courses']:
                                            st.write(f"- {course}")
                                    elif exp['details']['reason'] == 'credit_limit':
                                        st.error(f"❌ Would exceed credit limit")
                                        st.write(f"**Current Credits:** {exp['details']['current_credits']}")
                                        st.write(f"**Course Credits:** {exp['details']['course_credits']}")
                                        st.write(f"**Maximum Allowed:** {exp['details']['max_credits']}")
                else:
                    st.success("✅ Recommended Courses:")
                    
                    # Display credit summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Total Credits", total_credits)
                    with col2:
                        st.metric("🎯 Credit Limit", max_credits)
                    with col3:
                        remaining = max_credits - total_credits
                        st.metric("⏳ Remaining", remaining)
                    
                    # Display recommendations with explanations
                    st.subheader("📚 Recommended Courses with Explanations")
                    for exp in explanations:
                        if exp['type'] == 'recommended':
                            with st.expander(f"✅ {exp['code']} - {exp['name']}"):
                                st.write("**Why this course is recommended:**")
                                if exp['details']['prerequisites_met']:
                                    st.write("✅ **Prerequisites met:**")
                                    for prereq in exp['details']['prerequisites_met']:
                                        st.write(f"- {prereq}")
                                if exp['details']['corequisites_met']:
                                    st.write("✅ **Corequisites met:**")
                                    for coreq in exp['details']['corequisites_met']:
                                        st.write(f"- {coreq}")
                                st.write(f"✅ **Semester match:** {exp['details']['semester_match']}")
                                st.write(f"✅ **Track match:** {exp['details']['track_match']}")
                                
                                # Show course details
                                course_info = kb_df[kb_df['Course Code'] == exp['code']].iloc[0]
                                st.write("**Course Details:**")
                                st.write(f"**Description:** {course_info['Description']}")
                                if pd.notna(course_info['Prerequisites']) and str(course_info['Prerequisites']).strip():
                                    st.write(f"**Prerequisites:** {course_info['Prerequisites']}")
                                if pd.notna(course_info['Co-requisites']) and str(course_info['Co-requisites']).strip():
                                    st.write(f"**Co-requisites:** {course_info['Co-requisites']}")
                    
                    # Show skipped courses with explanations (only once)
                    if skipped_courses:
                        st.subheader("📋 Courses Not Recommended")
                        for exp in explanations:
                            if exp['type'] == 'restricted':
                                with st.expander(f"❌ {exp['code']} - {exp['name']}"):
                                    if exp['details']['reason'] == 'already_passed':
                                        st.success(f"✅ Course already completed")
                                    elif exp['details']['reason'] == 'previously_failed':
                                        st.warning(f"⚠️ Course previously failed - Consider retaking")
                                        st.write("**Priority:** High")
                                    elif exp['details']['reason'] == 'track_mismatch':
                                        st.error(f"❌ Track mismatch")
                                        st.write(f"**Required Track:** {exp['details']['course_track']}")
                                    elif exp['details']['reason'] == 'semester_mismatch':
                                        st.error(f"❌ Not offered this semester")
                                        st.write(f"**Offered in:** {exp['details']['offered_semester']}")
                                    elif exp['details']['reason'] == 'missing_prerequisites':
                                        st.error(f"❌ Missing prerequisites")
                                        st.write("**Required Courses:**")
                                        for course in exp['details']['required_courses']:
                                            st.write(f"- {course}")
                                    elif exp['details']['reason'] == 'missing_corequisites':
                                        st.error(f"❌ Missing corequisites")
                                        st.write("**Required Courses:**")
                                        for course in exp['details']['required_courses']:
                                            st.write(f"- {course}")
                                    elif exp['details']['reason'] == 'credit_limit':
                                        st.error(f"❌ Would exceed credit limit")
                                        st.write(f"**Current Credits:** {exp['details']['current_credits']}")
                                        st.write(f"**Course Credits:** {exp['details']['course_credits']}")
                                        st.write(f"**Maximum Allowed:** {exp['details']['max_credits']}")
                    
                    # Create detailed recommendations dataframe for export
                    recommended_codes = [rec['code'] for rec in recommendations]
                    export_df = kb_df[kb_df['Course Code'].isin(recommended_codes)].copy()
                    
                    # Add recommendation-specific columns
                    export_df['Recommended'] = 'Yes'
                    export_df['Total Credits'] = total_credits
                    export_df['Credit Limit'] = max_credits
                    export_df['Remaining Credits'] = max_credits - total_credits
                    export_df['Student CGPA'] = cgpa
                    export_df['Current Semester'] = semester
                    
                    # Select and reorder columns for export
                    export_columns = [
                        'Course Code', 'Course Name', 'Credit Hours', 'Description',
                        'Prerequisites', 'Co-requisites', 'Program/Track', 'Semester Offered',
                        'Recommended', 'Total Credits', 'Credit Limit', 'Remaining Credits',
                        'Student CGPA', 'Current Semester'
                    ]
                    export_df = export_df[export_columns]
                    
                    # Export button with improved CSV
                    csv = export_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Detailed Recommendations as CSV",
                        data=csv,
                        file_name=f"course_recommendations_{semester}_{cgpa}.csv",
                        mime="text/csv"
                    )
                    
                    # Show detailed course information
                    st.subheader("📚 Detailed Course Information")
                    for rec in recommendations:
                        course_info = kb_df[kb_df['Course Code'] == rec['code']].iloc[0]
                        with st.expander(f"✅ {rec['code']} - {rec['name']} ({rec['credit_hours']} credits)"):
                            st.write(f"**Description:** {course_info['Description']}")
                            if pd.notna(course_info['Prerequisites']) and str(course_info['Prerequisites']).strip():
                                st.write(f"**Prerequisites:** {course_info['Prerequisites']}")
                            if pd.notna(course_info['Co-requisites']) and str(course_info['Co-requisites']).strip():
                                st.write(f"**Co-requisites:** {course_info['Co-requisites']}")
                            st.write(f"**Program/Track:** {course_info['Program/Track']}")
                            st.write(f"**Semester Offered:** {course_info['Semester Offered']}")
                    
                    # Show skipped courses if any
                    if skipped_courses:
                        st.subheader("📋 Courses Not Recommended")
                        for course in skipped_courses[:10]:  # Show first 10 to avoid cluttering
                            with st.expander(f"❌ {course['code']} - {course['name']}"):
                                st.write(f"**Reason:** {course['reason']}")
                        
                        if len(skipped_courses) > 10:
                            st.info(f"... and {len(skipped_courses) - 10} more courses not shown")
                            
            except Exception as e:
                st.error(f"❌ Error generating recommendations: {e}")
                st.exception(e)

# --------------------------
# FOOTER
# --------------------------
st.markdown("---")
st.markdown("🤖 **Powered by Expert System with Experta** | 📊 **Rule-based Course Recommendation**")