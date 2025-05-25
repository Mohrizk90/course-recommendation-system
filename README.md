# Course Recommendation Expert System 🎓

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.22.0%2B-red)](https://streamlit.io/)
[![Experta](https://img.shields.io/badge/Experta-2.0.0%2B-green)](https://experta.readthedocs.io/)

An intelligent course recommendation system built using Python and the Experta library. The system uses a rule-based expert system to recommend university courses based on student information and academic policies.

## 🌟 Features

- **Intelligent Course Recommendations**
  - Rule-based expert system using Experta
  - Support for prerequisites and co-requisites
  - Credit hour limits based on CGPA
  - Semester and track-based filtering
  - Detailed explanations for recommendations

- **Multiple Interfaces**
  - Modern Streamlit web application
  - Command-line interface
  - Knowledge base editor for course management

- **Smart Features**
  - Transparent reasoning for recommendations
  - Detailed course analysis
  - Export recommendations to CSV
  - Test case support
  - Comprehensive error handling

## 📋 Project Structure

```
project-root/
├── README.md                 # Project documentation
├── requirements.txt          # Project dependencies
├── requirements-test.txt     # Test dependencies
├── app.py                    # Main Streamlit application
├── inference_engine.py       # Core expert system
├── kb_editor.py             # Knowledge base editor
├── CE_Cloud.csv             # Course database
├── course_advisor_test_cases.txt  # Test cases
└── docs/                    # Documentation
    └── setup_guide.md       # Setup instructions
```

## 🚀 Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/course-recommendation-system.git
   cd course-recommendation-system
   ```

2. **Create a Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the System**
   ```bash
   # Web Interface
   streamlit run app.py

   # Command Line Interface
   python inference_engine.py
   ```

## 💻 Usage

### Web Interface
1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. Open your browser at `http://localhost:8501`
3. Enter your:
   - CGPA
   - Current semester
   - Passed courses
   - Failed courses
4. Get personalized course recommendations

### Command Line Interface
```bash
python inference_engine.py --cgpa 3.2 --semester Fall --passed MAT111,CSE014
```

### Knowledge Base Editor
```bash
python kb_editor.py
```

## 🧪 Testing

Run the test suite:
```bash
pip install -r requirements-test.txt
pytest
```

## 📚 Documentation

- [Setup Guide](docs/setup_guide.md)
- [API Documentation](docs/api.md)
- [User Guide](docs/user_guide.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Mohamed Yasser
- Ahmed Hanny
- Islam Ali
  

## 🙏 Acknowledgments

- Experta library for expert system implementation
- Streamlit for the web interface
- AIU for course data and requirements

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers. 
