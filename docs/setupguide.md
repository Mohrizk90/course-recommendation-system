# Project Setup Guide

This guide will help you set up and run the project on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- Git
- A virtual environment tool (venv is recommended)

## Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd prj
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On Unix/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   # Install main dependencies
   pip install -r requirements.txt

   # Install test dependencies (optional)
   pip install -r requirements-test.txt
   ```

## Project Structure

```
prj/
├── src/           # Source code
├── tests/         # Test files
├── data/          # Data files
├── demo/          # Demo applications
├── docs/          # Documentation
├── requirements.txt        # Main dependencies
└── requirements-test.txt   # Test dependencies
```

## Running the Project

1. **Activate the Virtual Environment** (if not already activated)
   ```bash
   # On Windows
   .\venv\Scripts\activate

   # On Unix/MacOS
   source venv/bin/activate
   ```

2. **Run the Application**
   ```bash
   # Navigate to the src directory
   cd src
   python main.py
   ```

## Running Tests

To run the test suite:
```bash
# From the project root
python -m pytest tests/
```

## Common Issues and Troubleshooting

### Virtual Environment Issues
- If you get a "command not found" error when activating the virtual environment, ensure you're in the correct directory and using the correct activation command for your OS.
- If pip install fails, try upgrading pip: `python -m pip install --upgrade pip`

### Dependency Issues
- If you encounter dependency conflicts, try creating a fresh virtual environment and reinstalling dependencies.
- Make sure you're using the correct Python version as specified in the prerequisites.

### Running Issues
- Ensure you're in the correct directory when running commands
- Check that the virtual environment is activated (you should see `(venv)` in your terminal prompt)
- Verify that all dependencies are installed correctly

## Getting Help

If you encounter any issues not covered in this guide:
1. Check the project's README.md for additional information
2. Review the project's issue tracker for known issues
3. Create a new issue if you believe you've found a bug

## Contributing

If you'd like to contribute to the project:
1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the terms included in the LICENSE file. 