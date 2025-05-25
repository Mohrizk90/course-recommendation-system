# Course Recommendation System Setup Guide

This guide provides detailed instructions for setting up and running the Course Recommendation Expert System.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git (optional, for version control)

## Installation Steps

1. **Clone the Repository** (if using Git):
   ```bash
   git clone <repository-url>
   cd course-recommendation-system
   ```

2. **Create a Virtual Environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Installation**:
   ```bash
   python -c "import experta; import pandas; import streamlit; print('Installation successful!')"
   ```

## Project Structure Setup

1. **Create Required Directories**:
   ```bash
   mkdir -p data src tests docs demo
   ```

2. **Move Files to Correct Locations**:
   - Move `CE_Cloud.csv` to `data/`
   - Move Python source files to `src/`
   - Move test files to `tests/`
   - Move documentation to `docs/`

## Running the System

### Command Line Interface

1. **Basic Usage**:
   ```bash
   python src/cli_advisor.py --cgpa 3.2 --semester Fall --passed MAT111,CSE014
   ```

2. **Available Options**:
   ```bash
   python src/cli_advisor.py --help
   ```

### Web Interface

1. **Start the Streamlit App**:
   ```bash
   streamlit run src/streamlit_app.py
   ```

2. **Access the Web Interface**:
   - Open your browser
   - Navigate to `http://localhost:8501`

### Knowledge Base Editor

1. **Start the Editor**:
   ```bash
   python src/knowledge_base_editor.py
   ```

2. **Using the Editor**:
   - Add new courses
   - Modify existing courses
   - Export/Import course data

## Testing

1. **Run All Tests**:
   ```bash
   pytest tests/
   ```

2. **Run Specific Tests**:
   ```bash
   pytest tests/test_specific_feature.py
   ```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**:
   - Ensure virtual environment is activated
   - Verify all dependencies are installed
   - Check Python path

2. **CSV File Not Found**:
   - Verify `CE_Cloud.csv` is in `data/` directory
   - Check file permissions

3. **Streamlit Connection Issues**:
   - Check if port 8501 is available
   - Verify network settings

### Getting Help

- Check the [README.md](../README.md) for general information
- Review the [final report](final_report.pdf) for detailed documentation
- Open an issue on the project repository

## Development

### Adding New Features

1. Create a new branch:
   ```bash
   git checkout -b feature/new-feature
   ```

2. Make changes and test:
   ```bash
   pytest tests/
   ```

3. Update documentation

4. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions
- Include unit tests for new features

## Maintenance

### Regular Tasks

1. Update dependencies:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. Run tests:
   ```bash
   pytest tests/
   ```

3. Update documentation

### Backup

1. Regular database backups:
   ```bash
   cp data/CE_Cloud.csv data/backup/CE_Cloud_$(date +%Y%m%d).csv
   ```

2. Version control:
   ```bash
   git add .
   git commit -m "Regular backup"
   git push
   ``` 