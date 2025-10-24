"""
Pytest configuration and fixtures for the University Performance Analyzer.

This module provides common fixtures and test utilities used across all test modules.
"""

import pytest
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import tempfile
import os
from pathlib import Path

from src.grading import GradeScale, DEFAULT_4_0_SCALE, DEFAULT_100_SCALE
from src.models import StudentRecord, ParsedStudent, CohortSummary


@pytest.fixture
def sample_student_data():
    """Sample student data for testing."""
    return pd.DataFrame({
        'StudentID': ['S001', 'S001', 'S002', 'S002', 'S003', 'S003'],
        'Name': ['John Doe', 'John Doe', 'Jane Smith', 'Jane Smith', 'Bob Johnson', 'Bob Johnson'],
        'Department': ['Computer Science', 'Computer Science', 'Mathematics', 'Mathematics', 'Physics', 'Physics'],
        'Semester': ['Fall 2023', 'Fall 2023', 'Fall 2023', 'Fall 2023', 'Fall 2023', 'Fall 2023'],
        'CourseCode': ['CS101', 'CS102', 'MATH101', 'MATH102', 'PHYS101', 'PHYS102'],
        'CourseName': ['Programming I', 'Programming II', 'Calculus I', 'Calculus II', 'Mechanics', 'Thermodynamics'],
        'CreditHours': [3.0, 3.0, 4.0, 4.0, 3.0, 3.0],
        'Marks': [85.0, 90.0, 78.0, 82.0, 88.0, 85.0]
    })


@pytest.fixture
def sample_student_data_with_grades():
    """Sample student data with grade information."""
    return pd.DataFrame({
        'StudentID': ['S001', 'S001', 'S002', 'S002', 'S003', 'S003'],
        'Name': ['John Doe', 'John Doe', 'Jane Smith', 'Jane Smith', 'Bob Johnson', 'Bob Johnson'],
        'Department': ['Computer Science', 'Computer Science', 'Mathematics', 'Mathematics', 'Physics', 'Physics'],
        'Semester': ['Fall 2023', 'Fall 2023', 'Fall 2023', 'Fall 2023', 'Fall 2023', 'Fall 2023'],
        'CourseCode': ['CS101', 'CS102', 'MATH101', 'MATH102', 'PHYS101', 'PHYS102'],
        'CourseName': ['Programming I', 'Programming II', 'Calculus I', 'Calculus II', 'Mechanics', 'Thermodynamics'],
        'CreditHours': [3.0, 3.0, 4.0, 4.0, 3.0, 3.0],
        'Marks': [85.0, 90.0, 78.0, 82.0, 88.0, 85.0],
        'Grade': ['B', 'A-', 'C+', 'B-', 'B+', 'B']
    })


@pytest.fixture
def sample_student_data_failing():
    """Sample student data with some failing grades."""
    return pd.DataFrame({
        'StudentID': ['S001', 'S001', 'S002', 'S002', 'S003', 'S003'],
        'Name': ['John Doe', 'John Doe', 'Jane Smith', 'Jane Smith', 'Bob Johnson', 'Bob Johnson'],
        'Department': ['Computer Science', 'Computer Science', 'Mathematics', 'Mathematics', 'Physics', 'Physics'],
        'Semester': ['Fall 2023', 'Fall 2023', 'Fall 2023', 'Fall 2023', 'Fall 2023', 'Fall 2023'],
        'CourseCode': ['CS101', 'CS102', 'MATH101', 'MATH102', 'PHYS101', 'PHYS102'],
        'CourseName': ['Programming I', 'Programming II', 'Calculus I', 'Calculus II', 'Mechanics', 'Thermodynamics'],
        'CreditHours': [3.0, 3.0, 4.0, 4.0, 3.0, 3.0],
        'Marks': [45.0, 50.0, 78.0, 82.0, 88.0, 85.0]  # First two are failing
    })


@pytest.fixture
def grade_scale_4_0():
    """4.0 grade scale for testing."""
    return DEFAULT_4_0_SCALE


@pytest.fixture
def grade_scale_100():
    """100-point grade scale for testing."""
    return DEFAULT_100_SCALE


@pytest.fixture
def custom_grade_scale():
    """Custom grade scale for testing."""
    return GradeScale(
        scale_type="custom",
        custom_config={
            'grade_mappings': {
                'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0
            },
            'grade_boundaries': {
                'A': (90, 100), 'B': (80, 89), 'C': (70, 79),
                'D': (60, 69), 'F': (0, 59)
            },
            'passing_grade': 'D'
        }
    )


@pytest.fixture
def sample_csv_content():
    """Sample CSV content as string."""
    return """StudentID,Name,Department,Semester,CourseCode,CourseName,CreditHours,Marks
S001,John Doe,Computer Science,Fall 2023,CS101,Programming I,3.0,85.0
S001,John Doe,Computer Science,Fall 2023,CS102,Programming II,3.0,90.0
S002,Jane Smith,Mathematics,Fall 2023,MATH101,Calculus I,4.0,78.0
S002,Jane Smith,Mathematics,Fall 2023,MATH102,Calculus II,4.0,82.0
S003,Bob Johnson,Physics,Fall 2023,PHYS101,Mechanics,3.0,88.0
S003,Bob Johnson,Physics,Fall 2023,PHYS102,Thermodynamics,3.0,85.0"""


@pytest.fixture
def sample_csv_file(sample_csv_content):
    """Sample CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample_csv_content)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def sample_csv_bytes(sample_csv_content):
    """Sample CSV content as bytes."""
    return sample_csv_content.encode('utf-8')


@pytest.fixture
def sample_student_records():
    """Sample StudentRecord objects for testing."""
    return [
        StudentRecord(
            student_id='S001',
            name='John Doe',
            department='Computer Science',
            semester='Fall 2023',
            course_code='CS101',
            course_name='Programming I',
            credit_hours=3.0,
            marks=85.0
        ),
        StudentRecord(
            student_id='S001',
            name='John Doe',
            department='Computer Science',
            semester='Fall 2023',
            course_code='CS102',
            course_name='Programming II',
            credit_hours=3.0,
            marks=90.0
        )
    ]


@pytest.fixture
def sample_parsed_students():
    """Sample ParsedStudent objects for testing."""
    return [
        ParsedStudent(
            student_id='S001',
            name='John Doe',
            department='Computer Science',
            semester='Fall 2023',
            total_credits=6.0,
            total_marks=87.5,
            gpa=3.5,
            courses_count=2,
            pass_fail_status='Pass',
            grade_distribution={'A-': 1, 'B': 1}
        ),
        ParsedStudent(
            student_id='S002',
            name='Jane Smith',
            department='Mathematics',
            semester='Fall 2023',
            total_credits=8.0,
            total_marks=80.0,
            gpa=3.0,
            courses_count=2,
            pass_fail_status='Pass',
            grade_distribution={'B-': 1, 'C+': 1}
        )
    ]


@pytest.fixture
def sample_cohort_summary():
    """Sample CohortSummary object for testing."""
    return CohortSummary(
        total_students=3,
        total_courses=6,
        average_gpa=3.25,
        median_gpa=3.25,
        pass_rate=100.0,
        fail_count=0,
        gpa_std_dev=0.25,
        total_credits=20.0
    )


@pytest.fixture
def sample_subject_stats():
    """Sample subject statistics for testing."""
    return [
        {
            'course_code': 'CS101',
            'course_name': 'Programming I',
            'department': 'Computer Science',
            'total_students': 1,
            'average_marks': 85.0,
            'pass_rate': 100.0,
            'top_scorer': 'John Doe',
            'top_score': 85.0,
            'credit_hours': 3.0
        },
        {
            'course_code': 'MATH101',
            'course_name': 'Calculus I',
            'department': 'Mathematics',
            'total_students': 1,
            'average_marks': 78.0,
            'pass_rate': 100.0,
            'top_scorer': 'Jane Smith',
            'top_score': 78.0,
            'credit_hours': 4.0
        }
    ]


@pytest.fixture
def sample_department_analysis():
    """Sample department analysis for testing."""
    return {
        'Computer Science': {
            'total_students': 1,
            'total_courses': 2,
            'average_gpa': 3.5,
            'median_gpa': 3.5,
            'gpa_std_dev': 0.0,
            'pass_rate': 100.0
        },
        'Mathematics': {
            'total_students': 1,
            'total_courses': 2,
            'average_gpa': 3.0,
            'median_gpa': 3.0,
            'gpa_std_dev': 0.0,
            'pass_rate': 100.0
        }
    }


@pytest.fixture
def sample_performance_trends():
    """Sample performance trends for testing."""
    return {
        'semesters': ['Fall 2023', 'Spring 2024'],
        'average_gpa_by_semester': [3.25, 3.5],
        'pass_rate_by_semester': [100.0, 100.0],
        'total_students_by_semester': [3, 3]
    }


@pytest.fixture
def sample_pdf_config():
    """Sample PDF report configuration for testing."""
    from src.models import PDFReportConfig
    return PDFReportConfig(
        title="Test Report",
        institution="Test University",
        cohort_info="Test Cohort",
        include_charts=True,
        include_leaderboard=True,
        include_subject_stats=True,
        anonymize_names=False,
        selected_students=None
    )


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing."""
    return {
        "Generated on": "January 1, 2024 at 12:00 PM",
        "Total Students": 3,
        "Total Records": 6,
        "Grade Scale": "4.0"
    }


@pytest.fixture
def sample_filter_options():
    """Sample filter options for testing."""
    from src.models import FilterOptions
    return FilterOptions(
        departments=['Computer Science', 'Mathematics'],
        semesters=['Fall 2023'],
        min_gpa=3.0,
        max_gpa=4.0,
        student_search='John',
        pass_fail_filter='Pass'
    )


@pytest.fixture
def sample_grade_scale_config():
    """Sample grade scale configuration for testing."""
    from src.models import GradeScaleConfig
    return GradeScaleConfig(
        scale_name="Test Scale",
        scale_type="4.0",
        grade_mappings={
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'F': 0.0
        },
        grade_boundaries={
            'A+': (97, 100), 'A': (93, 96), 'A-': (90, 92),
            'B+': (87, 89), 'B': (83, 86), 'B-': (80, 82),
            'C+': (77, 79), 'C': (73, 76), 'C-': (70, 72),
            'D+': (67, 69), 'D': (63, 66), 'F': (0, 62)
        },
        passing_grade="D"
    )


@pytest.fixture
def sample_analysis_response():
    """Sample analysis response for testing."""
    from src.models import AnalysisResponse
    return AnalysisResponse(
        success=True,
        message="Analysis completed successfully",
        data={
            'total_students': 3,
            'average_gpa': 3.25,
            'pass_rate': 100.0
        },
        errors=None
    )


@pytest.fixture
def sample_export_response():
    """Sample export response for testing."""
    from src.models import ExportResponse
    return ExportResponse(
        success=True,
        message="Export completed successfully",
        file_path="/tmp/test_export.csv",
        file_size=1024
    )


# Test utilities
def create_test_dataframe(rows: int = 10) -> pd.DataFrame:
    """Create a test DataFrame with specified number of rows."""
    np.random.seed(42)  # For reproducible tests
    
    data = {
        'StudentID': [f'S{i:03d}' for i in range(1, rows + 1)],
        'Name': [f'Student {i}' for i in range(1, rows + 1)],
        'Department': np.random.choice(['Computer Science', 'Mathematics', 'Physics'], rows),
        'Semester': np.random.choice(['Fall 2023', 'Spring 2024'], rows),
        'CourseCode': [f'CS{i:03d}' for i in range(1, rows + 1)],
        'CourseName': [f'Course {i}' for i in range(1, rows + 1)],
        'CreditHours': np.random.choice([3.0, 4.0], rows),
        'Marks': np.random.uniform(60, 100, rows)
    }
    
    return pd.DataFrame(data)


def assert_dataframe_equals(df1: pd.DataFrame, df2: pd.DataFrame, tolerance: float = 1e-6):
    """Assert that two DataFrames are equal within tolerance."""
    pd.testing.assert_frame_equal(df1, df2, check_exact=False, atol=tolerance)


def assert_series_equals(s1: pd.Series, s2: pd.Series, tolerance: float = 1e-6):
    """Assert that two Series are equal within tolerance."""
    pd.testing.assert_series_equal(s1, s2, check_exact=False, atol=tolerance)
