"""
University Performance Analyzer

A comprehensive Streamlit application for analyzing university student performance data.
Provides GPA calculation, subject analytics, and PDF report generation.
"""

__version__ = "1.0.0"
__author__ = "University Performance Analyzer Team"
__email__ = "team@example.com"

# Core modules
from .config import Settings, get_settings
from .models import StudentRecord, ParsedStudent, CohortSummary, SubjectStats
from .data_loader import load_csv, validate_csv_columns, aggregate_student_records
from .grading import GradeScale, compute_gpa
from .analytics import cohort_summary, subject_stats, top_n_students
from .pdf_report import generate_pdf_report
from .ui import kpi_card, plot_gpa_histogram, plot_subject_averages

__all__ = [
    # Configuration
    "Settings",
    "get_settings",
    # Models
    "StudentRecord",
    "ParsedStudent", 
    "CohortSummary",
    "SubjectStats",
    # Data loading
    "load_csv",
    "validate_csv_columns",
    "aggregate_student_records",
    # Grading
    "GradeScale",
    "compute_gpa",
    # Analytics
    "cohort_summary",
    "subject_stats", 
    "top_n_students",
    # PDF generation
    "generate_pdf_report",
    # UI components
    "kpi_card",
    "plot_gpa_histogram",
    "plot_subject_averages",
]
