"""
Grading system module for the University Performance Analyzer.

This module handles grade conversion, GPA calculation, and grade scale management.
"""

import yaml
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import numpy as np
from pathlib import Path

from .config import DEFAULT_GRADE_MAPPINGS, GRADE_BOUNDARIES, get_grade_mapping, get_grade_boundaries
from .models import GradeScaleConfig


class GradeScale:
    """
    Configurable grade scale for converting marks to grades and GPA.
    
    Supports multiple grade scales (4.0, 100-point, custom) with flexible
    grade boundaries and point mappings.
    """
    
    def __init__(self, scale_type: str = "4.0", custom_config: Optional[Dict[str, Any]] = None):
        """
        Initialize grade scale.
        
        Args:
            scale_type: Type of grade scale ("4.0", "100", "custom")
            custom_config: Custom configuration for grade scale
        """
        self.scale_type = scale_type
        self.grade_mappings = get_grade_mapping(scale_type)
        self.grade_boundaries = get_grade_boundaries(scale_type)
        self.passing_grade = "D"
        
        if custom_config:
            self._apply_custom_config(custom_config)
    
    def _apply_custom_config(self, config: Dict[str, Any]) -> None:
        """Apply custom configuration to grade scale."""
        if 'grade_mappings' in config:
            self.grade_mappings = config['grade_mappings']
        if 'grade_boundaries' in config:
            self.grade_boundaries = config['grade_boundaries']
        if 'passing_grade' in config:
            self.passing_grade = config['passing_grade']
    
    def marks_to_grade(self, marks: float) -> str:
        """
        Convert numeric marks to letter grade.
        
        Args:
            marks: Numeric marks (0-100)
            
        Returns:
            Letter grade
        """
        if not isinstance(marks, (int, float)) or np.isnan(marks):
            return "F"
        
        marks = float(marks)
        
        # Find the appropriate grade based on boundaries
        for grade, (min_bound, max_bound) in self.grade_boundaries.items():
            if min_bound <= marks <= max_bound:
                return grade
        
        # Default to F if no grade found
        return "F"
    
    def grade_to_points(self, grade: str) -> float:
        """
        Convert letter grade to GPA points.
        
        Args:
            grade: Letter grade
            
        Returns:
            GPA points
        """
        if not grade or grade not in self.grade_mappings:
            return 0.0
        
        return self.grade_mappings[grade]
    
    def marks_to_points(self, marks: float) -> float:
        """
        Convert numeric marks directly to GPA points.
        
        Args:
            marks: Numeric marks (0-100)
            
        Returns:
            GPA points
        """
        grade = self.marks_to_grade(marks)
        return self.grade_to_points(grade)
    
    def is_passing_grade(self, grade: str) -> bool:
        """
        Check if a grade is passing.
        
        Args:
            grade: Letter grade
            
        Returns:
            True if passing, False otherwise
        """
        if not grade:
            return False
        
        # Get the grade boundaries for the passing grade
        if self.passing_grade in self.grade_boundaries:
            passing_min = self.grade_boundaries[self.passing_grade][0]
            grade_points = self.grade_to_points(grade)
            return grade_points >= self.grade_to_points(self.passing_grade)
        
        return grade != "F"
    
    def get_grade_distribution(self, marks_series: pd.Series) -> Dict[str, int]:
        """
        Get grade distribution for a series of marks.
        
        Args:
            marks_series: Series of marks
            
        Returns:
            Dictionary with grade counts
        """
        grades = marks_series.apply(self.marks_to_grade)
        return grades.value_counts().to_dict()
    
    def export_config(self, file_path: str) -> None:
        """
        Export grade scale configuration to YAML file.
        
        Args:
            file_path: Path to save configuration
        """
        config = {
            'scale_type': self.scale_type,
            'grade_mappings': self.grade_mappings,
            'grade_boundaries': self.grade_boundaries,
            'passing_grade': self.passing_grade
        }
        
        with open(file_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    @classmethod
    def from_yaml(cls, file_path: str) -> 'GradeScale':
        """
        Create GradeScale from YAML configuration file.
        
        Args:
            file_path: Path to YAML configuration file
            
        Returns:
            GradeScale instance
        """
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return cls(
            scale_type=config.get('scale_type', '4.0'),
            custom_config=config
        )


def compute_gpa(records: pd.DataFrame, scale: GradeScale) -> pd.Series:
    """
    Compute GPA for each student using credit-weighted average.
    
    Args:
        records: DataFrame with student course records
        scale: GradeScale instance for grade conversion
        
    Returns:
        Series with GPA for each student
    """
    try:
        # Ensure required columns exist
        required_cols = ['StudentID', 'Marks', 'CreditHours']
        missing_cols = [col for col in required_cols if col not in records.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Calculate GPA points for each course
        records = records.copy()
        records['GPA_Points'] = records['Marks'].apply(scale.marks_to_points)
        
        # Calculate credit-weighted GPA for each student
        gpa_calculation = records.groupby('StudentID').apply(
            lambda group: np.average(
                group['GPA_Points'], 
                weights=group['CreditHours']
            )
        )
        
        # Round to 3 decimal places
        gpa_calculation = gpa_calculation.round(3)
        
        return gpa_calculation
        
    except Exception as e:
        raise ValueError(f"Error computing GPA: {str(e)}")


def compute_student_gpa(student_records: List[Dict[str, Any]], scale: GradeScale) -> float:
    """
    Compute GPA for a single student.
    
    Args:
        student_records: List of course records for the student
        scale: GradeScale instance
        
    Returns:
        GPA for the student
    """
    if not student_records:
        return 0.0
    
    total_points = 0.0
    total_credits = 0.0
    
    for record in student_records:
        marks = record.get('Marks', 0)
        credits = record.get('CreditHours', 0)
        
        if credits > 0:  # Only include courses with credits
            points = scale.marks_to_points(marks)
            total_points += points * credits
            total_credits += credits
    
    if total_credits == 0:
        return 0.0
    
    return round(total_points / total_credits, 3)


def get_grade_statistics(df: pd.DataFrame, scale: GradeScale) -> Dict[str, Any]:
    """
    Get comprehensive grade statistics.
    
    Args:
        df: DataFrame with student records
        scale: GradeScale instance
        
    Returns:
        Dictionary with grade statistics
    """
    try:
        # Convert marks to grades
        df = df.copy()
        df['Grade'] = df['Marks'].apply(scale.marks_to_grade)
        df['GPA_Points'] = df['Marks'].apply(scale.marks_to_points)
        
        # Grade distribution
        grade_dist = df['Grade'].value_counts().to_dict()
        
        # Pass/fail statistics
        passing_grades = [grade for grade in grade_dist.keys() 
                         if scale.is_passing_grade(grade)]
        passing_count = sum(grade_dist[grade] for grade in passing_grades)
        total_count = len(df)
        pass_rate = (passing_count / total_count * 100) if total_count > 0 else 0
        
        # GPA statistics
        gpa_stats = {
            'mean': df['GPA_Points'].mean(),
            'median': df['GPA_Points'].median(),
            'std': df['GPA_Points'].std(),
            'min': df['GPA_Points'].min(),
            'max': df['GPA_Points'].max()
        }
        
        # Department-wise statistics
        dept_stats = {}
        if 'Department' in df.columns:
            for dept in df['Department'].unique():
                dept_df = df[df['Department'] == dept]
                dept_stats[dept] = {
                    'total_students': dept_df['StudentID'].nunique(),
                    'average_gpa': dept_df['GPA_Points'].mean(),
                    'pass_rate': (dept_df['GPA_Points'] >= scale.grade_to_points(scale.passing_grade)).mean() * 100
                }
        
        return {
            'grade_distribution': grade_dist,
            'pass_rate': round(pass_rate, 2),
            'passing_count': passing_count,
            'failing_count': total_count - passing_count,
            'gpa_statistics': gpa_stats,
            'department_statistics': dept_stats,
            'total_records': total_count
        }
        
    except Exception as e:
        raise ValueError(f"Error computing grade statistics: {str(e)}")


def create_custom_grade_scale(
    scale_name: str,
    grade_mappings: Dict[str, float],
    grade_boundaries: Dict[str, Tuple[float, float]],
    passing_grade: str = "D"
) -> GradeScale:
    """
    Create a custom grade scale.
    
    Args:
        scale_name: Name of the grade scale
        grade_mappings: Grade to points mapping
        grade_boundaries: Grade boundaries (min, max)
        passing_grade: Minimum passing grade
        
    Returns:
        GradeScale instance
    """
    custom_config = {
        'grade_mappings': grade_mappings,
        'grade_boundaries': grade_boundaries,
        'passing_grade': passing_grade
    }
    
    return GradeScale(scale_type="custom", custom_config=custom_config)


def validate_grade_scale(scale: GradeScale) -> List[str]:
    """
    Validate a grade scale configuration.
    
    Args:
        scale: GradeScale instance to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check if all grades in boundaries have mappings
    for grade in scale.grade_boundaries.keys():
        if grade not in scale.grade_mappings:
            errors.append(f"Grade '{grade}' in boundaries but not in mappings")
    
    # Check if all grades in mappings have boundaries
    for grade in scale.grade_mappings.keys():
        if grade not in scale.grade_boundaries:
            errors.append(f"Grade '{grade}' in mappings but not in boundaries")
    
    # Check for overlapping boundaries
    boundaries = list(scale.grade_boundaries.values())
    for i, (min1, max1) in enumerate(boundaries):
        for j, (min2, max2) in enumerate(boundaries):
            if i != j and not (max1 < min2 or max2 < min1):
                errors.append(f"Overlapping grade boundaries detected")
                break
    
    # Check if passing grade exists
    if scale.passing_grade not in scale.grade_mappings:
        errors.append(f"Passing grade '{scale.passing_grade}' not found in mappings")
    
    return errors


# Default grade scales for common use cases
DEFAULT_4_0_SCALE = GradeScale(scale_type="4.0")
DEFAULT_100_SCALE = GradeScale(scale_type="100")

# European grade scale example
EUROPEAN_SCALE = create_custom_grade_scale(
    scale_name="European",
    grade_mappings={
        "A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0
    },
    grade_boundaries={
        "A": (90, 100), "B": (80, 89), "C": (70, 79), 
        "D": (60, 69), "F": (0, 59)
    },
    passing_grade="D"
)
