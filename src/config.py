"""
Configuration management for the University Performance Analyzer.

This module provides centralized configuration using Pydantic BaseSettings
for environment variable handling and default values.
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = Field(default="University Performance Analyzer", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Security settings
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    
    # File upload settings
    max_upload_size_mb: int = Field(default=50, env="MAX_UPLOAD_SIZE_MB")
    allowed_file_types: list = Field(default=["csv"], env="ALLOWED_FILE_TYPES")
    
    # Default grade scale configuration
    default_grade_scale: str = Field(default="4.0", env="DEFAULT_GRADE_SCALE")
    
    # PDF generation settings
    pdf_title: str = Field(default="University Performance Report", env="PDF_TITLE")
    pdf_author: str = Field(default="University Performance Analyzer", env="PDF_AUTHOR")
    
    # Streamlit specific settings
    streamlit_theme_primary_color: str = Field(default="#1f77b4", env="STREAMLIT_THEME_PRIMARY_COLOR")
    streamlit_theme_background_color: str = Field(default="#ffffff", env="STREAMLIT_THEME_BACKGROUND_COLOR")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Default grade mappings
DEFAULT_GRADE_MAPPINGS = {
    "4.0": {
        "A+": 4.0, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D+": 1.3, "D": 1.0, "F": 0.0
    },
    "100": {
        "A+": 95, "A": 90, "A-": 85,
        "B+": 80, "B": 75, "B-": 70,
        "C+": 65, "C": 60, "C-": 55,
        "D+": 50, "D": 45, "F": 0
    }
}

# Required CSV columns
REQUIRED_COLUMNS = [
    "StudentID",
    "Name", 
    "Department",
    "Semester",
    "CourseCode",
    "CourseName",
    "CreditHours",
    "Marks"
]

# Column name mappings for flexibility
COLUMN_MAPPINGS = {
    "student_id": "StudentID",
    "student_name": "Name",
    "dept": "Department", 
    "sem": "Semester",
    "course_code": "CourseCode",
    "course_name": "CourseName",
    "credits": "CreditHours",
    "marks": "Marks",
    "grade": "Grade",
    "gpa": "GPA"
}

# Grade boundaries for different scales
GRADE_BOUNDARIES = {
    "4.0": {
        "A+": (97, 100), "A": (93, 96), "A-": (90, 92),
        "B+": (87, 89), "B": (83, 86), "B-": (80, 82),
        "C+": (77, 79), "C": (73, 76), "C-": (70, 72),
        "D+": (67, 69), "D": (63, 66), "F": (0, 62)
    },
    "100": {
        "A+": (95, 100), "A": (90, 94), "A-": (85, 89),
        "B+": (80, 84), "B": (75, 79), "B-": (70, 74),
        "C+": (65, 69), "C": (60, 64), "C-": (55, 59),
        "D+": (50, 54), "D": (45, 49), "F": (0, 44)
    }
}

# Application constants
MIN_GPA = 0.0
MAX_GPA = 4.0
PASSING_GRADE = "D"  # Minimum passing grade
MIN_CREDITS_FOR_GRADUATION = 120  # Typical university requirement

# UI Configuration
KPI_CARDS_PER_ROW = 4
DEFAULT_CHART_HEIGHT = 400
MAX_STUDENTS_IN_LEADERBOARD = 10
MAX_SUBJECTS_IN_CHART = 15

# File paths
SAMPLE_DATA_PATH = "sample_data/sample_students.csv"
TEMP_DIR = "temp"
REPORTS_DIR = "reports"

# Error messages
ERROR_MESSAGES = {
    "missing_columns": "Required columns missing: {missing_columns}",
    "invalid_data_type": "Invalid data type in column '{column}': {error}",
    "empty_file": "Uploaded file is empty",
    "file_too_large": "File size exceeds maximum allowed size of {max_size}MB",
    "invalid_file_type": "Invalid file type. Only CSV files are allowed",
    "no_data_after_filter": "No data found matching the selected filters",
    "gpa_calculation_error": "Error calculating GPA: {error}",
    "pdf_generation_error": "Error generating PDF report: {error}"
}

# Success messages  
SUCCESS_MESSAGES = {
    "file_uploaded": "File uploaded successfully",
    "data_loaded": "Data loaded successfully: {count} records",
    "filters_applied": "Filters applied successfully",
    "pdf_generated": "PDF report generated successfully",
    "data_exported": "Data exported successfully"
}


def get_grade_mapping(scale: str = "4.0") -> Dict[str, float]:
    """Get grade mapping for the specified scale."""
    return DEFAULT_GRADE_MAPPINGS.get(scale, DEFAULT_GRADE_MAPPINGS["4.0"])


def get_grade_boundaries(scale: str = "4.0") -> Dict[str, tuple]:
    """Get grade boundaries for the specified scale."""
    return GRADE_BOUNDARIES.get(scale, GRADE_BOUNDARIES["4.0"])


def is_development() -> bool:
    """Check if running in development mode."""
    return get_settings().app_env == "development"


def is_production() -> bool:
    """Check if running in production mode."""
    return get_settings().app_env == "production"
