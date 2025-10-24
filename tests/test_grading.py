"""
Unit tests for the grading module.

This module tests grade conversion, GPA calculation, and grade scale functionality.
"""

import pytest
import pandas as pd
import numpy as np
from typing import Dict, List, Any

from src.grading import (
    GradeScale, compute_gpa, compute_student_gpa, get_grade_statistics,
    create_custom_grade_scale, validate_grade_scale, DEFAULT_4_0_SCALE,
    DEFAULT_100_SCALE, EUROPEAN_SCALE
)


class TestGradeScale:
    """Test cases for GradeScale class."""
    
    def test_grade_scale_initialization(self, grade_scale_4_0):
        """Test grade scale initialization."""
        assert grade_scale_4_0.scale_type == "4.0"
        assert "A" in grade_scale_4_0.grade_mappings
        assert "A" in grade_scale_4_0.grade_boundaries
        assert grade_scale_4_0.passing_grade == "D"
    
    def test_marks_to_grade(self, grade_scale_4_0):
        """Test marks to grade conversion."""
        # Test various mark ranges
        assert grade_scale_4_0.marks_to_grade(95) == "A+"
        assert grade_scale_4_0.marks_to_grade(90) == "A"
        assert grade_scale_4_0.marks_to_grade(85) == "A-"
        assert grade_scale_4_0.marks_to_grade(80) == "B-"
        assert grade_scale_4_0.marks_to_grade(75) == "B"
        assert grade_scale_4_0.marks_to_grade(70) == "C-"
        assert grade_scale_4_0.marks_to_grade(65) == "C"
        assert grade_scale_4_0.marks_to_grade(60) == "D"
        assert grade_scale_4_0.marks_to_grade(55) == "F"
        
        # Test edge cases
        assert grade_scale_4_0.marks_to_grade(100) == "A+"
        assert grade_scale_4_0.marks_to_grade(0) == "F"
        assert grade_scale_4_0.marks_to_grade(97) == "A+"
        assert grade_scale_4_0.marks_to_grade(62) == "F"
    
    def test_grade_to_points(self, grade_scale_4_0):
        """Test grade to points conversion."""
        assert grade_scale_4_0.grade_to_points("A+") == 4.0
        assert grade_scale_4_0.grade_to_points("A") == 4.0
        assert grade_scale_4_0.grade_to_points("A-") == 3.7
        assert grade_scale_4_0.grade_to_points("B+") == 3.3
        assert grade_scale_4_0.grade_to_points("B") == 3.0
        assert grade_scale_4_0.grade_to_points("B-") == 2.7
        assert grade_scale_4_0.grade_to_points("C+") == 2.3
        assert grade_scale_4_0.grade_to_points("C") == 2.0
        assert grade_scale_4_0.grade_to_points("C-") == 1.7
        assert grade_scale_4_0.grade_to_points("D+") == 1.3
        assert grade_scale_4_0.grade_to_points("D") == 1.0
        assert grade_scale_4_0.grade_to_points("F") == 0.0
        
        # Test invalid grade
        assert grade_scale_4_0.grade_to_points("X") == 0.0
        assert grade_scale_4_0.grade_to_points("") == 0.0
    
    def test_marks_to_points(self, grade_scale_4_0):
        """Test direct marks to points conversion."""
        assert grade_scale_4_0.marks_to_points(95) == 4.0  # A+
        assert grade_scale_4_0.marks_to_points(90) == 4.0   # A
        assert grade_scale_4_0.marks_to_points(85) == 3.7    # A-
        assert grade_scale_4_0.marks_to_points(80) == 2.7    # B-
        assert grade_scale_4_0.marks_to_points(75) == 3.0   # B
        assert grade_scale_4_0.marks_to_points(70) == 1.7    # C-
        assert grade_scale_4_0.marks_to_points(65) == 2.0    # C
        assert grade_scale_4_0.marks_to_points(60) == 1.0    # D
        assert grade_scale_4_0.marks_to_points(55) == 0.0   # F
    
    def test_is_passing_grade(self, grade_scale_4_0):
        """Test pass/fail grade determination."""
        assert grade_scale_4_0.is_passing_grade("A+") == True
        assert grade_scale_4_0.is_passing_grade("A") == True
        assert grade_scale_4_0.is_passing_grade("B") == True
        assert grade_scale_4_0.is_passing_grade("C") == True
        assert grade_scale_4_0.is_passing_grade("D") == True
        assert grade_scale_4_0.is_passing_grade("F") == False
        
        # Test invalid grades
        assert grade_scale_4_0.is_passing_grade("X") == False
        assert grade_scale_4_0.is_passing_grade("") == False
    
    def test_get_grade_distribution(self, grade_scale_4_0):
        """Test grade distribution calculation."""
        marks_series = pd.Series([95, 90, 85, 80, 75, 70, 65, 60, 55])
        distribution = grade_scale_4_0.get_grade_distribution(marks_series)
        
        expected = {
            'A+': 1, 'A': 1, 'A-': 1, 'B-': 1, 'B': 1,
            'C-': 1, 'C': 1, 'D': 1, 'F': 1
        }
        
        assert distribution == expected
    
    def test_custom_grade_scale(self, custom_grade_scale):
        """Test custom grade scale functionality."""
        assert custom_grade_scale.scale_type == "custom"
        assert custom_grade_scale.grade_to_points("A") == 4.0
        assert custom_grade_scale.grade_to_points("B") == 3.0
        assert custom_grade_scale.grade_to_points("C") == 2.0
        assert custom_grade_scale.grade_to_points("D") == 1.0
        assert custom_grade_scale.grade_to_points("F") == 0.0
        
        assert custom_grade_scale.marks_to_grade(95) == "A"
        assert custom_grade_scale.marks_to_grade(85) == "B"
        assert custom_grade_scale.marks_to_grade(75) == "C"
        assert custom_grade_scale.marks_to_grade(65) == "D"
        assert custom_grade_scale.marks_to_grade(55) == "F"
    
    def test_export_config(self, grade_scale_4_0, tmp_path):
        """Test grade scale configuration export."""
        config_path = tmp_path / "grade_scale.yaml"
        grade_scale_4_0.export_config(str(config_path))
        
        assert config_path.exists()
        
        # Test loading from YAML
        loaded_scale = GradeScale.from_yaml(str(config_path))
        assert loaded_scale.scale_type == grade_scale_4_0.scale_type
        assert loaded_scale.grade_mappings == grade_scale_4_0.grade_mappings
        assert loaded_scale.grade_boundaries == grade_scale_4_0.grade_boundaries


class TestGPAComputation:
    """Test cases for GPA computation functions."""
    
    def test_compute_gpa(self, sample_student_data, grade_scale_4_0):
        """Test GPA computation for multiple students."""
        gpa_series = compute_gpa(sample_student_data, grade_scale_4_0)
        
        assert len(gpa_series) == 3  # Three unique students
        assert 'S001' in gpa_series.index
        assert 'S002' in gpa_series.index
        assert 'S003' in gpa_series.index
        
        # Check GPA values are reasonable
        for gpa in gpa_series.values:
            assert 0.0 <= gpa <= 4.0
    
    def test_compute_student_gpa(self, grade_scale_4_0):
        """Test GPA computation for a single student."""
        student_records = [
            {'Marks': 85.0, 'CreditHours': 3.0},
            {'Marks': 90.0, 'CreditHours': 3.0}
        ]
        
        gpa = compute_student_gpa(student_records, grade_scale_4_0)
        
        # Expected GPA: (3.7 * 3 + 4.0 * 3) / 6 = 3.85
        expected_gpa = (3.7 * 3 + 4.0 * 3) / 6
        assert abs(gpa - expected_gpa) < 0.01
    
    def test_compute_student_gpa_zero_credits(self, grade_scale_4_0):
        """Test GPA computation with zero credits."""
        student_records = [
            {'Marks': 85.0, 'CreditHours': 0.0},
            {'Marks': 90.0, 'CreditHours': 0.0}
        ]
        
        gpa = compute_student_gpa(student_records, grade_scale_4_0)
        assert gpa == 0.0
    
    def test_compute_student_gpa_empty_records(self, grade_scale_4_0):
        """Test GPA computation with empty records."""
        student_records = []
        gpa = compute_student_gpa(student_records, grade_scale_4_0)
        assert gpa == 0.0
    
    def test_compute_gpa_missing_columns(self, grade_scale_4_0):
        """Test GPA computation with missing columns."""
        df = pd.DataFrame({
            'StudentID': ['S001', 'S002'],
            'Name': ['John', 'Jane']
        })
        
        with pytest.raises(ValueError, match="Missing required columns"):
            compute_gpa(df, grade_scale_4_0)


class TestGradeStatistics:
    """Test cases for grade statistics functions."""
    
    def test_get_grade_statistics(self, sample_student_data, grade_scale_4_0):
        """Test grade statistics calculation."""
        stats = get_grade_statistics(sample_student_data, grade_scale_4_0)
        
        assert 'grade_distribution' in stats
        assert 'pass_rate' in stats
        assert 'passing_count' in stats
        assert 'failing_count' in stats
        assert 'gpa_statistics' in stats
        assert 'department_statistics' in stats
        assert 'total_records' in stats
        
        # Check that statistics are reasonable
        assert 0 <= stats['pass_rate'] <= 100
        assert stats['passing_count'] + stats['failing_count'] == stats['total_records']
        assert stats['total_records'] == len(sample_student_data)
    
    def test_get_grade_statistics_empty_data(self, grade_scale_4_0):
        """Test grade statistics with empty data."""
        empty_df = pd.DataFrame()
        stats = get_grade_statistics(empty_df, grade_scale_4_0)
        
        assert stats['total_records'] == 0
        assert stats['pass_rate'] == 0.0
        assert stats['passing_count'] == 0
        assert stats['failing_count'] == 0


class TestCustomGradeScale:
    """Test cases for custom grade scale creation."""
    
    def test_create_custom_grade_scale(self):
        """Test custom grade scale creation."""
        custom_scale = create_custom_grade_scale(
            scale_name="Test Scale",
            grade_mappings={'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0},
            grade_boundaries={'A': (90, 100), 'B': (80, 89), 'C': (70, 79), 'D': (60, 69), 'F': (0, 59)},
            passing_grade="D"
        )
        
        assert custom_scale.scale_type == "custom"
        assert custom_scale.grade_to_points("A") == 4.0
        assert custom_scale.grade_to_points("B") == 3.0
        assert custom_scale.marks_to_grade(95) == "A"
        assert custom_scale.marks_to_grade(85) == "B"
        assert custom_scale.is_passing_grade("D") == True
        assert custom_scale.is_passing_grade("F") == False


class TestGradeScaleValidation:
    """Test cases for grade scale validation."""
    
    def test_validate_grade_scale_valid(self, grade_scale_4_0):
        """Test validation of a valid grade scale."""
        errors = validate_grade_scale(grade_scale_4_0)
        assert len(errors) == 0
    
    def test_validate_grade_scale_missing_mappings(self):
        """Test validation with missing grade mappings."""
        invalid_scale = GradeScale(
            scale_type="custom",
            custom_config={
                'grade_mappings': {'A': 4.0, 'B': 3.0},
                'grade_boundaries': {'A': (90, 100), 'B': (80, 89), 'C': (70, 79)},
                'passing_grade': 'D'
            }
        )
        
        errors = validate_grade_scale(invalid_scale)
        assert len(errors) > 0
        assert any("Grade 'C' in boundaries but not in mappings" in error for error in errors)
    
    def test_validate_grade_scale_missing_boundaries(self):
        """Test validation with missing grade boundaries."""
        invalid_scale = GradeScale(
            scale_type="custom",
            custom_config={
                'grade_mappings': {'A': 4.0, 'B': 3.0, 'C': 2.0},
                'grade_boundaries': {'A': (90, 100), 'B': (80, 89)},
                'passing_grade': 'D'
            }
        )
        
        errors = validate_grade_scale(invalid_scale)
        assert len(errors) > 0
        assert any("Grade 'C' in mappings but not in boundaries" in error for error in errors)
    
    def test_validate_grade_scale_invalid_passing_grade(self):
        """Test validation with invalid passing grade."""
        invalid_scale = GradeScale(
            scale_type="custom",
            custom_config={
                'grade_mappings': {'A': 4.0, 'B': 3.0},
                'grade_boundaries': {'A': (90, 100), 'B': (80, 89)},
                'passing_grade': 'C'  # Not in mappings
            }
        )
        
        errors = validate_grade_scale(invalid_scale)
        assert len(errors) > 0
        assert any("Passing grade 'C' not found in mappings" in error for error in errors)


class TestDefaultScales:
    """Test cases for default grade scales."""
    
    def test_default_4_0_scale(self):
        """Test default 4.0 grade scale."""
        assert DEFAULT_4_0_SCALE.scale_type == "4.0"
        assert DEFAULT_4_0_SCALE.grade_to_points("A") == 4.0
        assert DEFAULT_4_0_SCALE.grade_to_points("F") == 0.0
        assert DEFAULT_4_0_SCALE.marks_to_grade(95) == "A+"
        assert DEFAULT_4_0_SCALE.marks_to_grade(55) == "F"
    
    def test_default_100_scale(self):
        """Test default 100-point grade scale."""
        assert DEFAULT_100_SCALE.scale_type == "100"
        assert DEFAULT_100_SCALE.grade_to_points("A") == 95
        assert DEFAULT_100_SCALE.grade_to_points("F") == 0
        assert DEFAULT_100_SCALE.marks_to_grade(95) == "A+"
        assert DEFAULT_100_SCALE.marks_to_grade(55) == "F"
    
    def test_european_scale(self):
        """Test European grade scale."""
        assert EUROPEAN_SCALE.scale_type == "custom"
        assert EUROPEAN_SCALE.grade_to_points("A") == 4.0
        assert EUROPEAN_SCALE.grade_to_points("B") == 3.0
        assert EUROPEAN_SCALE.grade_to_points("C") == 2.0
        assert EUROPEAN_SCALE.grade_to_points("D") == 1.0
        assert EUROPEAN_SCALE.grade_to_points("F") == 0.0


class TestEdgeCases:
    """Test cases for edge cases and error handling."""
    
    def test_marks_to_grade_edge_cases(self, grade_scale_4_0):
        """Test edge cases for marks to grade conversion."""
        # Test boundary values
        assert grade_scale_4_0.marks_to_grade(97) == "A+"
        assert grade_scale_4_0.marks_to_grade(96) == "A"
        assert grade_scale_4_0.marks_to_grade(93) == "A"
        assert grade_scale_4_0.marks_to_grade(92) == "A-"
        
        # Test invalid inputs
        assert grade_scale_4_0.marks_to_grade(-10) == "F"
        assert grade_scale_4_0.marks_to_grade(150) == "F"
        assert grade_scale_4_0.marks_to_grade(float('nan')) == "F"
    
    def test_grade_to_points_edge_cases(self, grade_scale_4_0):
        """Test edge cases for grade to points conversion."""
        # Test invalid grades
        assert grade_scale_4_0.grade_to_points("") == 0.0
        assert grade_scale_4_0.grade_to_points(None) == 0.0
        assert grade_scale_4_0.grade_to_points("INVALID") == 0.0
    
    def test_compute_gpa_edge_cases(self, grade_scale_4_0):
        """Test edge cases for GPA computation."""
        # Test with all failing grades
        failing_data = pd.DataFrame({
            'StudentID': ['S001', 'S001'],
            'Marks': [50.0, 45.0],
            'CreditHours': [3.0, 3.0]
        })
        
        gpa_series = compute_gpa(failing_data, grade_scale_4_0)
        assert gpa_series['S001'] == 0.0
        
        # Test with mixed grades
        mixed_data = pd.DataFrame({
            'StudentID': ['S001', 'S001', 'S001'],
            'Marks': [95.0, 50.0, 85.0],
            'CreditHours': [3.0, 3.0, 3.0]
        })
        
        gpa_series = compute_gpa(mixed_data, grade_scale_4_0)
        # Should be weighted average: (4.0*3 + 0.0*3 + 3.7*3) / 9 = 2.57
        expected_gpa = (4.0*3 + 0.0*3 + 3.7*3) / 9
        assert abs(gpa_series['S001'] - expected_gpa) < 0.01
