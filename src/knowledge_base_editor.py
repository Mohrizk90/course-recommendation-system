import pandas as pd
import os

# CSV file path
KB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "CE_Cloud.csv")

# Load Knowledge Base
def load_kb():
    print(f"Looking for CSV file at: {KB_FILE}")
    if os.path.exists(KB_FILE):
        print("CSV file found!")
        try:
            # Read CSV and drop duplicates
            df = pd.read_csv(KB_FILE)
            print(f"Initial DataFrame shape: {df.shape}")
            
            # Drop duplicate rows
            df = df.drop_duplicates()
            print(f"After dropping duplicates: {df.shape}")
            
            # Clean column names
            df.columns = [col.strip() for col in df.columns]
            
            # Remove any completely empty rows
            df = df.dropna(how='all')
            
            # Reset index
            df = df.reset_index(drop=True)
            
            print(f"Final DataFrame shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            return df
        except Exception as e:
            print(f"Error reading CSV: {str(e)}")
            return pd.DataFrame(columns=[
                'Course Code', 'Course Name', 'Description',
                'Prerequisites', 'Co-requisites',
                'Credit Hours', 'Semester Offered', 'Program/Track'
            ])
    else:
        print("CSV file not found!")
        return pd.DataFrame(columns=[
            'Course Code', 'Course Name', 'Description',
            'Prerequisites', 'Co-requisites',
            'Credit Hours', 'Semester Offered', 'Program/Track'
        ])

# Save Knowledge Base
def save_kb(df):
    # Drop duplicates before saving
    df = df.drop_duplicates()
    df.to_csv(KB_FILE, index=False)
    print("✅ Knowledge base saved to", KB_FILE)

# View Courses
def view_courses(df):
    print(f"\nDataFrame info:")
    print(f"Number of rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    if df.empty:
        print("\n📚 No courses found in the knowledge base.\n")
    else:
        print("\n📚 Current Courses:\n")
        print(df.to_string(index=False))

# Add a New Course
def add_course(df):
    course_code = input("Course Code: ").strip().upper()
    if course_code in df['Course Code'].values:
        print("⚠️ Course already exists.")
        return df

    course_name = input("Course Name: ").strip()
    description = input("Description: ").strip()
    prerequisites = input("Prerequisites (comma-separated or None): ").strip()
    corequisites = input("Co-requisites (comma-separated or None): ").strip()

    try:
        credit_hours = int(input("Credit Hours: "))
        if credit_hours <= 0:
            raise ValueError
    except ValueError:
        print("❌ Credit hours must be a positive integer.")
        return df

    semester_offered = input("Semester Offered (Fall/Spring/Both): ").strip().capitalize()
    program_track = input("Program/Track: ").strip()

    # Validate prerequisites
    existing_codes = df['Course Code'].tolist()
    if prerequisites.lower() != 'none':
        for pre in prerequisites.split(','):
            if pre.strip() not in existing_codes:
                print(f"❌ Prerequisite '{pre.strip()}' does not exist in the current knowledge base.")
                return df

    new_course = {
        'Course Code': course_code,
        'Course Name': course_name,
        'Description': description,
        'Prerequisites': prerequisites,
        'Co-requisites': corequisites,
        'Credit Hours': credit_hours,
        'Semester Offered': semester_offered,
        'Program/Track': program_track
    }

    df = pd.concat([df, pd.DataFrame([new_course])], ignore_index=True)
    print("✅ Course added.")
    return df

# Edit a Course
def edit_course(df):
    code = input("Enter course code to edit: ").strip().upper()
    if code not in df['Course Code'].values:
        print("❌ Course not found.")
        return df

    idx = df[df['Course Code'] == code].index[0]
    print(f"\nEditing {code} — Leave blank to keep current value.")

    for col in df.columns:
        if col == 'Course Code':
            continue
        current = df.at[idx, col]
        new_value = input(f"{col} (current: {current}): ").strip()
        if new_value:
            if col == 'Credit Hours':
                try:
                    new_value = int(new_value)
                    if new_value <= 0:
                        raise ValueError
                except ValueError:
                    print("❌ Invalid credit hours. Skipping this field.")
                    continue
            df.at[idx, col] = new_value

    print("✅ Course updated.")
    return df

# Delete a Course
def delete_course(df):
    code = input("Enter course code to delete: ").strip().upper()
    if code in df['Course Code'].values:
        df = df[df['Course Code'] != code]
        print(f"✅ Course '{code}' deleted.")
    else:
        print("❌ Course not found.")
    return df

# Menu
def menu():
    df = load_kb()

    while True:
        print("\n🔧 Knowledge Base Editor")
        print("1. View Courses")
        print("2. Add Course")
        print("3. Edit Course")
        print("4. Delete Course")
        print("5. Save and Exit")
        choice = input("Select an option (1–5): ").strip()

        if choice == '1':
            view_courses(df)
        elif choice == '2':
            df = add_course(df)
        elif choice == '3':
            df = edit_course(df)
        elif choice == '4':
            df = delete_course(df)
        elif choice == '5':
            save_kb(df)
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    menu()
