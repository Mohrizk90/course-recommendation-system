#!/usr/bin/env python3
"""
Script to reorganize the project files into the new structure.
"""

import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Create the required directory structure."""
    directories = [
        'data',
        'src',
        'tests',
        'docs',
        'demo',
        'data/backup'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def move_files():
    """Move files to their new locations."""
    # Define file movements (source -> destination)
    movements = {
        'CE_Cloud.csv': 'data/CE_Cloud.csv',
        'inference_engine.py': 'src/inference_engine.py',
        'kb_editor.py': 'src/knowledge_base_editor.py',
        'app.py': 'src/streamlit_app.py',
        'course_advisor_test_cases.txt': 'tests/course_advisor_test_cases.txt',
        'README.md': 'README.md',
        'requirements.txt': 'requirements.txt',
        'docs/setup_guide.md': 'docs/setup_guide.md'
    }
    
    # Create CLI advisor
    cli_content = '''#!/usr/bin/env python3
"""
Command-line interface for the course recommendation system.
"""

import argparse
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent
sys.path.append(str(src_path))

from inference_engine import run_advisor, load_course_database

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Course Recommendation System CLI')
    parser.add_argument('--cgpa', type=float, required=True,
                      help='Student CGPA (0.0 to 4.0)')
    parser.add_argument('--semester', type=str, required=True,
                      choices=['Fall', 'Spring', 'Summer'],
                      help='Current semester')
    parser.add_argument('--passed', type=str, required=True,
                      help='Comma-separated list of passed courses')
    parser.add_argument('--failed', type=str, default='',
                      help='Comma-separated list of failed courses')
    return parser.parse_args()

def main():
    """Main function to run the CLI advisor."""
    args = parse_args()
    
    # Convert comma-separated strings to lists
    passed = [c.strip() for c in args.passed.split(',') if c.strip()]
    failed = [c.strip() for c in args.failed.split(',') if c.strip()]
    
    try:
        # Load course database
        kb_path = Path(__file__).parent.parent / 'data' / 'CE_Cloud.csv'
        df = load_course_database(str(kb_path))
        
        # Run advisor
        recommendations = run_advisor(
            args.cgpa,
            args.semester,
            passed,
            failed,
            df
        )
        
        # Print recommendations
        if not recommendations:
            print("No courses recommended.")
            sys.exit(1)
            
        print("\\nRecommended Courses:")
        print("=" * 80)
        for code, name, description, credits in recommendations:
            print(f"Course Code: {code}")
            print(f"Course Name: {name}")
            print(f"Description: {description}")
            print(f"Credit Hours: {credits}")
            print("-" * 80)
        
        print(f"\\nTotal Credit Hours: {sum(c for _, _, _, c in recommendations)}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
'''
    
    # Write CLI advisor
    with open('src/cli_advisor.py', 'w') as f:
        f.write(cli_content)
    print("✅ Created CLI advisor: src/cli_advisor.py")
    
    # Move existing files
    for source, dest in movements.items():
        if os.path.exists(source):
            # Create backup if destination exists
            if os.path.exists(dest):
                backup = f"{dest}.bak"
                shutil.copy2(dest, backup)
                print(f"⚠️  Created backup: {backup}")
            
            # Move file
            shutil.move(source, dest)
            print(f"✅ Moved {source} -> {dest}")

def main():
    """Main function to reorganize the project."""
    print("🚀 Starting project reorganization...")
    
    # Create directory structure
    create_directory_structure()
    
    # Move files
    move_files()
    
    print("\n✨ Project reorganization complete!")
    print("\nNext steps:")
    print("1. Review the new structure")
    print("2. Test the system:")
    print("   - CLI: python src/cli_advisor.py --cgpa 3.2 --semester Fall --passed MAT111,CSE014")
    print("   - Web: streamlit run src/streamlit_app.py")
    print("3. Update any import statements in your code")
    print("4. Run tests to verify everything works")

if __name__ == '__main__':
    main() 