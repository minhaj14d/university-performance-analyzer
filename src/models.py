"""
Pydantic models for the University Performance Analyzer.

This module defines the data models used throughout the application,
including validation rules and type hints.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator, root_validator


class StudentRecord(BaseModel):
    """Model for individual student course records."""
    
    student_id: str = Field(..., description="Unique student identifier")
    name: str = Field(..., description="Student full name")
    department: str = Field(..., description="Academic department")
    semester: str = Field(..., description="Academic semester")
    course_code: str = Field(..., description="Course code")
    course_name: str = Field(..., description="Course name")
    credit_hours: float = Field(..., ge=0, le=10, description="Credit hours for the course")
    marks: float = Field(..., ge=0, le=100, description="Marks obtained (0-100)")
    grade: Optional[str] = Field(None, description="Letter grade")
    gpa_points: Optional[float] = Field(None, ge=0, le=4, description="GPA points for this course")
    
    @validator('student_id')
    def validate_student_id(cls, v):
        """Validate student ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Student ID cannot be empty")
        return v.strip()
    
    @validator('name')
    def validate_name(cls, v):
        """Validate student name."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Student name cannot be empty")
        return v.strip().title()
    
    @validator('department')
    def validate_department(cls, v):
        """Validate department name."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Department cannot be empty")
        return v.strip().title()
    
    @validator('semester')
    def validate_semester(cls, v):
        """Validate semester format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Semester cannot be empty")
        return v.strip()
    
    @validator('course_code')
    def validate_course_code(cls, v):
        """Validate course code format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Course code cannot be empty")
        return v.strip().upper()
    
    @validator('course_name')
    def validate_course_name(cls, v):
        """Validate course name."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Course name cannot be empty")
        return v.strip()
    
    @validator('marks')
    def validate_marks(cls, v):
        """Validate marks are within acceptable range."""
        if v < 0 or v > 100:
            raise ValueError("Marks must be between 0 and 100")
        return round(v, 2)
    
    @validator('credit_hours')
    def validate_credit_hours(cls, v):
        """Validate credit hours."""
        if v <= 0:
            raise ValueError("Credit hours must be positive")
        return round(v, 1)
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True


class ParsedStudent(BaseModel):
    """Model for aggregated student data with GPA calculation."""
    
    student_id: str = Field(..., description="Unique student identifier")
    name: str = Field(..., description="Student full name")
    department: str = Field(..., description="Academic department")
    semester: str = Field(..., description="Academic semester")
    total_credits: float = Field(..., ge=0, description="Total credit hours")
    total_marks: float = Field(..., ge=0, description="Total marks obtained")
    gpa: float = Field(..., ge=0, le=4, description="Calculated GPA")
    courses_count: int = Field(..., ge=1, description="Number of courses taken")
    pass_fail_status: str = Field(..., description="Pass/Fail status")
    grade_distribution: Dict[str, int] = Field(default_factory=dict, description="Grade distribution")
    
    @validator('gpa')
    def validate_gpa(cls, v):
        """Validate GPA is within acceptable range."""
        if v < 0 or v > 4:
            raise ValueError("GPA must be between 0 and 4")
        return round(v, 3)
    
    @validator('pass_fail_status')
    def validate_pass_fail_status(cls, v):
        """Validate pass/fail status."""
        if v not in ['Pass', 'Fail']:
            raise ValueError("Pass/Fail status must be 'Pass' or 'Fail'")
        return v
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class CohortSummary(BaseModel):
    """Model for cohort-level analytics summary."""
    
    total_students: int = Field(..., ge=0, description="Total number of students")
    total_courses: int = Field(..., ge=0, description="Total number of courses")
    average_gpa: float = Field(..., ge=0, le=4, description="Average GPA across all students")
    median_gpa: float = Field(..., ge=0, le=4, description="Median GPA across all students")
    pass_rate: float = Field(..., ge=0, le=100, description="Percentage of students who passed")
    fail_count: int = Field(..., ge=0, description="Number of students who failed")
    gpa_std_dev: float = Field(..., ge=0, description="Standard deviation of GPA")
    total_credits: float = Field(..., ge=0, description="Total credit hours across all students")
    
    @validator('pass_rate')
    def validate_pass_rate(cls, v):
        """Validate pass rate is a percentage."""
        if v < 0 or v > 100:
            raise ValueError("Pass rate must be between 0 and 100")
        return round(v, 2)
    
    @validator('average_gpa', 'median_gpa')
    def validate_gpa_values(cls, v):
        """Validate GPA values."""
        if v < 0 or v > 4:
            raise ValueError("GPA values must be between 0 and 4")
        return round(v, 3)
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class SubjectStats(BaseModel):
    """Model for subject-wise analytics."""
    
    course_code: str = Field(..., description="Course code")
    course_name: str = Field(..., description="Course name")
    department: str = Field(..., description="Academic department")
    total_students: int = Field(..., ge=0, description="Number of students in this course")
    average_marks: float = Field(..., ge=0, le=100, description="Average marks in this course")
    pass_rate: float = Field(..., ge=0, le=100, description="Pass rate for this course")
    top_scorer: Optional[str] = Field(None, description="Student with highest marks")
    top_score: Optional[float] = Field(None, ge=0, le=100, description="Highest marks obtained")
    credit_hours: float = Field(..., ge=0, description="Credit hours for this course")
    
    @validator('average_marks', 'top_score')
    def validate_marks(cls, v):
        """Validate marks values."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Marks must be between 0 and 100")
        return round(v, 2) if v is not None else v
    
    @validator('pass_rate')
    def validate_pass_rate(cls, v):
        """Validate pass rate."""
        if v < 0 or v > 100:
            raise ValueError("Pass rate must be between 0 and 100")
        return round(v, 2)
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class GradeScaleConfig(BaseModel):
    """Model for grade scale configuration."""
    
    scale_name: str = Field(..., description="Name of the grade scale")
    scale_type: str = Field(..., description="Type of scale (4.0, 100, etc.)")
    grade_mappings: Dict[str, float] = Field(..., description="Grade to points mapping")
    grade_boundaries: Dict[str, tuple] = Field(..., description="Grade boundaries")
    passing_grade: str = Field(default="D", description="Minimum passing grade")
    
    @validator('scale_type')
    def validate_scale_type(cls, v):
        """Validate scale type."""
        if v not in ['4.0', '100', 'custom']:
            raise ValueError("Scale type must be '4.0', '100', or 'custom'")
        return v
    
    @validator('grade_mappings')
    def validate_grade_mappings(cls, v):
        """Validate grade mappings."""
        if not v:
            raise ValueError("Grade mappings cannot be empty")
        return v
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class FilterOptions(BaseModel):
    """Model for data filtering options."""
    
    departments: Optional[List[str]] = Field(None, description="Filter by departments")
    semesters: Optional[List[str]] = Field(None, description="Filter by semesters")
    min_gpa: Optional[float] = Field(None, ge=0, le=4, description="Minimum GPA filter")
    max_gpa: Optional[float] = Field(None, ge=0, le=4, description="Maximum GPA filter")
    student_search: Optional[str] = Field(None, description="Search term for student names")
    pass_fail_filter: Optional[str] = Field(None, description="Filter by pass/fail status")
    
    @validator('min_gpa', 'max_gpa')
    def validate_gpa_range(cls, v):
        """Validate GPA range values."""
        if v is not None and (v < 0 or v > 4):
            raise ValueError("GPA values must be between 0 and 4")
        return v
    
    @validator('pass_fail_filter')
    def validate_pass_fail_filter(cls, v):
        """Validate pass/fail filter."""
        if v is not None and v not in ['Pass', 'Fail', 'All']:
            raise ValueError("Pass/Fail filter must be 'Pass', 'Fail', or 'All'")
        return v
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class PDFReportConfig(BaseModel):
    """Model for PDF report configuration."""
    
    title: str = Field(default="University Performance Report", description="Report title")
    institution: str = Field(default="University", description="Institution name")
    cohort_info: str = Field(default="", description="Cohort information")
    include_charts: bool = Field(default=True, description="Include charts in report")
    include_leaderboard: bool = Field(default=True, description="Include leaderboard")
    include_subject_stats: bool = Field(default=True, description="Include subject statistics")
    anonymize_names: bool = Field(default=False, description="Anonymize student names")
    selected_students: Optional[List[str]] = Field(None, description="Specific students to include")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


# Response models for API-like interfaces
class AnalysisResponse(BaseModel):
    """Response model for analysis results."""
    
    success: bool = Field(..., description="Whether the analysis was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Analysis data")
    errors: Optional[List[str]] = Field(None, description="List of errors if any")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class ExportResponse(BaseModel):
    """Response model for data export."""
    
    success: bool = Field(..., description="Whether the export was successful")
    message: str = Field(..., description="Response message")
    file_path: Optional[str] = Field(None, description="Path to exported file")
    file_size: Optional[int] = Field(None, description="Size of exported file in bytes")
    timestamp: datetime = Field(default_factory=datetime.now, description="Export timestamp")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
