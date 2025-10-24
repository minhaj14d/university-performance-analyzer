# 🎓 University Performance Analyzer

A comprehensive Streamlit application for analyzing university student performance data. This application provides GPA calculation, subject analytics, performance insights, and PDF report generation for educational institutions.

## ✨ Features

### 📊 **Performance Analytics**
- **GPA Calculation**: Automatic GPA computation with configurable grade scales (4.0, 100-point, custom)
- **Cohort Analysis**: Comprehensive summary statistics for student cohorts
- **Subject Performance**: Detailed analytics for individual courses and subjects
- **Department Analysis**: Performance comparison across academic departments
- **Semester Trends**: Track performance changes over time

### 📈 **Interactive Visualizations**
- **GPA Distribution**: Histogram showing GPA distribution across students
- **Pass/Fail Analysis**: Pie charts and statistics for student success rates
- **Subject Leaderboards**: Bar charts showing top-performing subjects
- **Department Comparison**: Performance metrics across departments
- **Trend Analysis**: Line charts showing performance over time

### 📋 **Data Management**
- **CSV Upload**: Easy upload of student performance data
- **Data Validation**: Comprehensive validation with helpful error messages
- **Flexible Filtering**: Filter by department, semester, GPA range, and student search
- **Data Export**: Export filtered data and analytics summaries

### 📄 **Report Generation**
- **PDF Reports**: Professional reports with charts, tables, and analytics
- **Customizable Content**: Include/exclude sections based on needs
- **Student Selection**: Generate reports for specific students or entire cohorts
- **Anonymization**: Privacy-friendly options for sensitive data

### 🔧 **Technical Features**
- **Scalable Architecture**: Handles large datasets efficiently
- **Intelligent Caching**: Optimized performance with Streamlit caching
- **Type Safety**: Full type hints and Pydantic validation
- **Professional UI**: Clean, responsive, and user-friendly interface
- **Docker Support**: Easy deployment with containerization

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/university-performance-analyzer.git
   cd university-performance-analyzer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

### Using Docker

1. **Build the Docker image**
   ```bash
   docker build -t university-performance-analyzer .
   ```

2. **Run the container**
   ```bash
   docker run -p 8501:8501 university-performance-analyzer
   ```

## 📊 Sample Data Format

The application expects CSV files with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `StudentID` | Unique student identifier | `S001` |
| `Name` | Student full name | `John Doe` |
| `Department` | Academic department | `Computer Science` |
| `Semester` | Academic semester | `Fall 2023` |
| `CourseCode` | Course code | `CS101` |
| `CourseName` | Course name | `Programming I` |
| `CreditHours` | Credit hours for the course | `3.0` |
| `Marks` | Marks obtained (0-100) | `85.0` |

### Sample CSV Structure
```csv
StudentID,Name,Department,Semester,CourseCode,CourseName,CreditHours,Marks
S001,John Doe,Computer Science,Fall 2023,CS101,Programming I,3.0,85.0
S001,John Doe,Computer Science,Fall 2023,CS102,Programming II,3.0,90.0
S002,Jane Smith,Mathematics,Fall 2023,MATH101,Calculus I,4.0,78.0
```

## 🎯 How It Works

### Data Pipeline
1. **CSV Upload**: Users upload student performance data
2. **Validation**: Data is validated for required columns and formats
3. **Processing**: Data is cleaned and normalized
4. **GPA Calculation**: Student GPAs are computed using configurable grade scales
5. **Analytics**: Comprehensive analytics are generated
6. **Visualization**: Interactive charts and tables are created
7. **Reporting**: PDF reports can be generated and downloaded

### Grade Scale Configuration
The application supports multiple grade scales:

- **4.0 Scale**: Standard US university grading (A=4.0, B=3.0, etc.)
- **100-Point Scale**: Percentage-based grading
- **Custom Scales**: Configurable grade boundaries and point mappings

### Analytics Engine
- **Cohort Summary**: Total students, average GPA, pass rates, etc.
- **Subject Analysis**: Course-wise performance metrics
- **Department Comparison**: Cross-department performance analysis
- **Trend Analysis**: Performance changes over time
- **Top Performers**: Student and subject leaderboards

## 🛠️ Development

### Project Structure
```
university-performance-analyzer/
├── .github/workflows/ci.yml    # CI/CD pipeline
├── Dockerfile                   # Docker configuration
├── Makefile                    # Development commands
├── pyproject.toml              # Project configuration
├── requirements.txt            # Core dependencies
├── requirements-optional.txt    # Optional dependencies
├── streamlit.toml              # Streamlit configuration
├── app.py                      # Main Streamlit application
├── src/                        # Source code
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── models.py              # Pydantic models
│   ├── data_loader.py         # CSV loading and validation
│   ├── grading.py             # Grade scale and GPA calculation
│   ├── analytics.py           # Performance analytics
│   ├── pdf_report.py          # PDF report generation
│   └── ui.py                  # UI components
├── tests/                      # Test suite
│   ├── test_grading.py
│   ├── test_data_loader.py
│   └── test_analytics.py
├── sample_data/               # Sample datasets
│   └── sample_students.csv
└── README.md                  # This file
```

### Development Commands

```bash
# Install dependencies
make install

# Run the application
make run

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Clean up
make clean

# Docker commands
make docker-build
make docker-run
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_grading.py
```

### Code Quality
The project uses several tools for code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing

## 🚀 Deployment

### Streamlit Cloud
1. Fork this repository
2. Connect your GitHub account to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy the app with the following settings:
   - **Repository**: Your forked repository
   - **Branch**: `main`
   - **Main file path**: `app.py`

### Docker Deployment
```bash
# Build image
docker build -t university-performance-analyzer .

# Run container
docker run -p 8501:8501 university-performance-analyzer

# Run with environment variables
docker run -p 8501:8501 -e APP_ENV=production university-performance-analyzer
```

### Environment Variables
- `APP_ENV`: Application environment (`development`, `production`)
- `SECRET_KEY`: Secret key for security
- `DEBUG`: Enable debug mode (`true`, `false`)

## 📸 Screenshots

### Dashboard Overview
![Dashboard Overview](https://via.placeholder.com/800x400/1f77b4/ffffff?text=Dashboard+Overview)

### Analytics Charts
![Analytics Charts](https://via.placeholder.com/800x400/ff7f0e/ffffff?text=Analytics+Charts)

### PDF Report
![PDF Report](https://via.placeholder.com/800x400/2ca02c/ffffff?text=PDF+Report)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Add tests for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit** for the amazing web framework
- **Plotly** for interactive visualizations
- **Pandas** for data manipulation
- **Pydantic** for data validation
- **ReportLab** for PDF generation

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-username/university-performance-analyzer/issues) page
2. Create a new issue with detailed information
3. Contact the development team

## 🔮 Future Enhancements

### Planned Features
1. **Authentication**: User authentication and role-based access
2. **Database Integration**: PostgreSQL backend for large datasets
3. **Background Processing**: Celery/RQ for heavy computations
4. **Cloud Storage**: S3 integration for file storage
5. **API Endpoints**: RESTful API for external integrations
6. **Machine Learning**: Predictive analytics and insights
7. **Multi-language Support**: Internationalization
8. **Advanced Reporting**: More report templates and customization

### Roadmap
- **Q1 2024**: Authentication and user management
- **Q2 2024**: Database integration and scalability improvements
- **Q3 2024**: Machine learning features and advanced analytics
- **Q4 2024**: API development and external integrations

## 📊 Performance Metrics

- **Data Processing**: Handles datasets with 10,000+ students
- **Response Time**: < 2 seconds for most operations
- **Memory Usage**: Optimized for efficient resource utilization
- **Scalability**: Docker-ready for horizontal scaling

## 🔒 Security & Privacy

- **Data Privacy**: All data processing happens in memory
- **No Data Storage**: Uploaded files are not permanently stored
- **Anonymization**: Built-in options for data anonymization
- **Secure Deployment**: Production-ready security configurations

---

**Made with ❤️ for educational institutions worldwide**

*Empowering educators with data-driven insights for student success*