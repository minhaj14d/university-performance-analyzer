"""
Unit tests for the data_loader module.

This module tests CSV loading, validation, and data preprocessing functionality.
"""

import pytest
import pandas as pd
import io
from typing import Dict, List, Any
import tempfile
import os

from src.data_loader import (
    load_csv, validate_csv_columns, normalize_column_names, coerce_data_types,
    aggregate_student_records, load_sample_data, validate_student_records,
    get_data_summary, DataLoaderError, ValidationError
)


class TestCSVLoading:
    """Test cases for CSV loading functionality."""
    
    def test_load_csv_valid_data(self, sample_csv_bytes):
        """Test loading valid CSV data."""
        csv_io = io.BytesIO(sample_csv_bytes)
        df = load_csv(csv_io)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 6
        assert 'StudentID' in df.columns
        assert 'Name' in df.columns
        assert 'Department' in df.columns
        assert 'Semester' in df.columns
        assert 'CourseCode' in df.columns
        assert 'CourseName' in df.columns
        assert 'CreditHours' in df.columns
        assert 'Marks' in df.columns
    
    def test_load_csv_empty_file(self):
        """Test loading empty CSV file."""
        empty_csv = io.BytesIO(b"")
        
        with pytest.raises(DataLoaderError, match="Could not decode CSV file"):
            load_csv(empty_csv)
    
    def test_load_csv_invalid_format(self):
        """Test loading CSV with invalid format."""
        invalid_csv = io.BytesIO(b"invalid,csv,data\nwith,no,proper,format")
        
        with pytest.raises(DataLoaderError):
            load_csv(invalid_csv)
    
    def test_load_csv_missing_columns(self):
        """Test loading CSV with missing required columns."""
        incomplete_csv = io.BytesIO(b"StudentID,Name\nS001,John")
        
        with pytest.raises(ValidationError, match="Required columns missing"):
            load_csv(incomplete_csv)
    
    def test_load_csv_different_encodings(self):
        """Test loading CSV with different encodings."""
        # Test UTF-8 encoding
        utf8_csv = io.BytesIO("StudentID,Name,Department,Semester,CourseCode,CourseName,CreditHours,Marks\nS001,John,CS,Fall,CS101,Programming,3.0,85.0".encode('utf-8'))
        df = load_csv(utf8_csv)
        assert len(df) == 1
        
        # Test Latin-1 encoding
        latin1_csv = io.BytesIO("StudentID,Name,Department,Semester,CourseCode,CourseName,CreditHours,Marks\nS001,José,CS,Fall,CS101,Programming,3.0,85.0".encode('latin-1'))
        df = load_csv(latin1_csv)
        assert len(df) == 1


class TestColumnValidation:
    """Test cases for column validation functionality."""
    
    def test_validate_csv_columns_valid(self, sample_student_data):
        """Test validation with valid columns."""
        # Should not raise any exception
        validate_csv_columns(sample_student_data)
    
    def test_validate_csv_columns_empty_dataframe(self):
        """Test validation with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValidationError, match="Uploaded file is empty"):
            validate_csv_columns(empty_df)
    
    def test_validate_csv_columns_missing_columns(self):
        """Test validation with missing required columns."""
        incomplete_df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John']
        })
        
        with pytest.raises(ValidationError, match="Required columns missing"):
            validate_csv_columns(incomplete_df)
    
    def test_validate_csv_columns_case_insensitive(self):
        """Test validation with case-insensitive column names."""
        df = pd.DataFrame({
            'studentid': ['S001'],
            'name': ['John'],
            'department': ['CS'],
            'semester': ['Fall'],
            'coursecode': ['CS101'],
            'coursename': ['Programming'],
            'credithours': [3.0],
            'marks': [85.0]
        })
        
        # Should not raise any exception
        validate_csv_columns(df)


class TestColumnNormalization:
    """Test cases for column name normalization."""
    
    def test_normalize_column_names_standard(self):
        """Test normalization of standard column names."""
        df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John'],
            'Department': ['CS'],
            'Semester': ['Fall'],
            'CourseCode': ['CS101'],
            'CourseName': ['Programming'],
            'CreditHours': [3.0],
            'Marks': [85.0]
        })
        
        normalized_df = normalize_column_names(df)
        
        # Should remain the same
        assert list(normalized_df.columns) == list(df.columns)
    
    def test_normalize_column_names_flexible(self):
        """Test normalization of flexible column names."""
        df = pd.DataFrame({
            'student_id': ['S001'],
            'student_name': ['John'],
            'dept': ['CS'],
            'sem': ['Fall'],
            'course_code': ['CS101'],
            'course_name': ['Programming'],
            'credits': [3.0],
            'marks': [85.0]
        })
        
        normalized_df = normalize_column_names(df)
        
        # Should be normalized to standard names
        expected_columns = ['StudentID', 'Name', 'Department', 'Semester', 'CourseCode', 'CourseName', 'CreditHours', 'Marks']
        assert list(normalized_df.columns) == expected_columns
    
    def test_normalize_column_names_mixed_case(self):
        """Test normalization of mixed case column names."""
        df = pd.DataFrame({
            'studentid': ['S001'],
            'NAME': ['John'],
            'Department': ['CS'],
            'semester': ['Fall'],
            'CourseCode': ['CS101'],
            'coursename': ['Programming'],
            'CreditHours': [3.0],
            'MARKS': [85.0]
        })
        
        normalized_df = normalize_column_names(df)
        
        # Should normalize to standard names
        expected_columns = ['StudentID', 'Name', 'Department', 'Semester', 'CourseCode', 'CourseName', 'CreditHours', 'Marks']
        assert list(normalized_df.columns) == expected_columns


class TestDataTypeCoercion:
    """Test cases for data type coercion functionality."""
    
    def test_coerce_data_types_valid(self, sample_student_data):
        """Test data type coercion with valid data."""
        coerced_df = coerce_data_types(sample_student_data)
        
        assert isinstance(coerced_df, pd.DataFrame)
        assert len(coerced_df) == len(sample_student_data)
        
        # Check data types
        assert pd.api.types.is_numeric_dtype(coerced_df['CreditHours'])
        assert pd.api.types.is_numeric_dtype(coerced_df['Marks'])
        assert pd.api.types.is_object_dtype(coerced_df['StudentID'])
        assert pd.api.types.is_object_dtype(coerced_df['Name'])
    
    def test_coerce_data_types_invalid_numeric(self):
        """Test data type coercion with invalid numeric data."""
        df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John'],
            'Department': ['CS'],
            'Semester': ['Fall'],
            'CourseCode': ['CS101'],
            'CourseName': ['Programming'],
            'CreditHours': ['invalid'],
            'Marks': ['not_a_number']
        })
        
        coerced_df = coerce_data_types(df)
        
        # Invalid numeric values should become NaN
        assert pd.isna(coerced_df['CreditHours'].iloc[0])
        assert pd.isna(coerced_df['Marks'].iloc[0])
    
    def test_coerce_data_types_missing_critical_data(self):
        """Test data type coercion with missing critical data."""
        df = pd.DataFrame({
            'StudentID': ['S001', 'S002', 'S003'],
            'Name': ['John', 'Jane', None],
            'Department': ['CS', 'Math', 'Physics'],
            'Semester': ['Fall', 'Fall', 'Fall'],
            'CourseCode': ['CS101', 'MATH101', 'PHYS101'],
            'CourseName': ['Programming', 'Calculus', 'Mechanics'],
            'CreditHours': [3.0, 4.0, 3.0],
            'Marks': [85.0, 90.0, 88.0]
        })
        
        initial_rows = len(df)
        coerced_df = coerce_data_types(df)
        
        # Should remove rows with missing critical data
        assert len(coerced_df) < initial_rows
        assert len(coerced_df) == 2  # Only first two rows should remain


class TestStudentRecordAggregation:
    """Test cases for student record aggregation functionality."""
    
    def test_aggregate_student_records_valid(self, sample_student_data):
        """Test aggregation of valid student records."""
        aggregated_df = aggregate_student_records(sample_student_data)
        
        assert isinstance(aggregated_df, pd.DataFrame)
        assert len(aggregated_df) == 3  # Three unique students
        
        # Check aggregated columns
        expected_columns = ['StudentID', 'Name', 'Department', 'Semester', 'TotalCredits', 'AverageMarks', 'CoursesCount', 'CoursesList', 'PassFailStatus']
        assert list(aggregated_df.columns) == expected_columns
        
        # Check aggregation logic
        for _, row in aggregated_df.iterrows():
            assert row['TotalCredits'] > 0
            assert row['AverageMarks'] > 0
            assert row['CoursesCount'] > 0
            assert row['PassFailStatus'] in ['Pass', 'Fail']
    
    def test_aggregate_student_records_empty_data(self):
        """Test aggregation with empty data."""
        empty_df = pd.DataFrame()
        
        with pytest.raises(DataLoaderError, match="Error aggregating student records"):
            aggregate_student_records(empty_df)
    
    def test_aggregate_student_records_single_student(self):
        """Test aggregation with single student."""
        single_student_df = pd.DataFrame({
            'StudentID': ['S001', 'S001'],
            'Name': ['John', 'John'],
            'Department': ['CS', 'CS'],
            'Semester': ['Fall', 'Fall'],
            'CourseCode': ['CS101', 'CS102'],
            'CourseName': ['Programming I', 'Programming II'],
            'CreditHours': [3.0, 3.0],
            'Marks': [85.0, 90.0]
        })
        
        aggregated_df = aggregate_student_records(single_student_df)
        
        assert len(aggregated_df) == 1
        assert aggregated_df.iloc[0]['TotalCredits'] == 6.0
        assert aggregated_df.iloc[0]['AverageMarks'] == 87.5
        assert aggregated_df.iloc[0]['CoursesCount'] == 2


class TestStudentRecordValidation:
    """Test cases for student record validation functionality."""
    
    def test_validate_student_records_valid(self, sample_student_data):
        """Test validation of valid student records."""
        records = validate_student_records(sample_student_data)
        
        assert isinstance(records, list)
        assert len(records) == len(sample_student_data)
        
        for record in records:
            assert isinstance(record, StudentRecord)
            assert record.student_id is not None
            assert record.name is not None
            assert record.department is not None
            assert record.semester is not None
            assert record.course_code is not None
            assert record.course_name is not None
            assert record.credit_hours > 0
            assert 0 <= record.marks <= 100
    
    def test_validate_student_records_invalid_data(self):
        """Test validation with invalid student data."""
        invalid_df = pd.DataFrame({
            'StudentID': ['S001', 'S002'],
            'Name': ['', 'Jane'],  # Empty name
            'Department': ['CS', 'Math'],
            'Semester': ['Fall', 'Fall'],
            'CourseCode': ['CS101', 'MATH101'],
            'CourseName': ['Programming', 'Calculus'],
            'CreditHours': [3.0, 4.0],
            'Marks': [85.0, 90.0]
        })
        
        with pytest.raises(ValidationError, match="Validation errors found"):
            validate_student_records(invalid_df)
    
    def test_validate_student_records_invalid_marks(self):
        """Test validation with invalid marks."""
        invalid_df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John'],
            'Department': ['CS'],
            'Semester': ['Fall'],
            'CourseCode': ['CS101'],
            'CourseName': ['Programming'],
            'CreditHours': [3.0],
            'Marks': [150.0]  # Invalid marks > 100
        })
        
        with pytest.raises(ValidationError, match="Validation errors found"):
            validate_student_records(invalid_df)
    
    def test_validate_student_records_invalid_credits(self):
        """Test validation with invalid credit hours."""
        invalid_df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John'],
            'Department': ['CS'],
            'Semester': ['Fall'],
            'CourseCode': ['CS101'],
            'CourseName': ['Programming'],
            'CreditHours': [-3.0],  # Invalid negative credits
            'Marks': [85.0]
        })
        
        with pytest.raises(ValidationError, match="Validation errors found"):
            validate_student_records(invalid_df)


class TestDataSummary:
    """Test cases for data summary functionality."""
    
    def test_get_data_summary_valid(self, sample_student_data):
        """Test data summary generation with valid data."""
        summary = get_data_summary(sample_student_data)
        
        assert isinstance(summary, dict)
        assert 'total_records' in summary
        assert 'unique_students' in summary
        assert 'unique_courses' in summary
        assert 'departments' in summary
        assert 'semesters' in summary
        assert 'date_range' in summary
        assert 'marks_range' in summary
        assert 'credits_range' in summary
        
        # Check summary values
        assert summary['total_records'] == 6
        assert summary['unique_students'] == 3
        assert summary['unique_courses'] == 6
        assert len(summary['departments']) == 3
        assert len(summary['semesters']) == 1
    
    def test_get_data_summary_empty_data(self):
        """Test data summary with empty data."""
        empty_df = pd.DataFrame()
        summary = get_data_summary(empty_df)
        
        assert summary['total_records'] == 0
        assert summary['unique_students'] == 0
        assert summary['unique_courses'] == 0
        assert summary['departments'] == []
        assert summary['semesters'] == []
    
    def test_get_data_summary_missing_columns(self):
        """Test data summary with missing columns."""
        incomplete_df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John']
        })
        
        summary = get_data_summary(incomplete_df)
        
        # Should handle missing columns gracefully
        assert summary['total_records'] == 1
        assert summary['unique_students'] == 1
        assert summary['unique_courses'] == 0  # No CourseCode column


class TestSampleDataLoading:
    """Test cases for sample data loading functionality."""
    
    def test_load_sample_data_file_not_found(self):
        """Test loading sample data when file doesn't exist."""
        with pytest.raises(DataLoaderError, match="Sample data file not found"):
            load_sample_data()
    
    def test_load_sample_data_valid_file(self, tmp_path):
        """Test loading sample data from valid file."""
        # Create a temporary sample data file
        sample_data_path = tmp_path / "sample_students.csv"
        sample_data_path.write_text("""StudentID,Name,Department,Semester,CourseCode,CourseName,CreditHours,Marks
S001,John Doe,Computer Science,Fall 2023,CS101,Programming I,3.0,85.0
S002,Jane Smith,Mathematics,Fall 2023,MATH101,Calculus I,4.0,78.0""")
        
        # Mock the SAMPLE_DATA_PATH
        import src.data_loader
        original_path = src.data_loader.SAMPLE_DATA_PATH
        src.data_loader.SAMPLE_DATA_PATH = str(sample_data_path)
        
        try:
            df = load_sample_data()
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert 'StudentID' in df.columns
        finally:
            src.data_loader.SAMPLE_DATA_PATH = original_path


class TestErrorHandling:
    """Test cases for error handling functionality."""
    
    def test_data_loader_error(self):
        """Test DataLoaderError exception."""
        error = DataLoaderError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Test validation error")
        assert str(error) == "Test validation error"
        assert isinstance(error, Exception)
    
    def test_load_csv_parser_error(self):
        """Test CSV loading with parser error."""
        invalid_csv = io.BytesIO(b"invalid,csv,data\nwith,missing,columns")
        
        with pytest.raises(DataLoaderError, match="Error parsing CSV"):
            load_csv(invalid_csv)
    
    def test_coerce_data_types_error(self):
        """Test data type coercion with error."""
        df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John'],
            'Department': ['CS'],
            'Semester': ['Fall'],
            'CourseCode': ['CS101'],
            'CourseName': ['Programming'],
            'CreditHours': ['invalid'],
            'Marks': ['not_a_number']
        })
        
        # Should handle errors gracefully
        try:
            coerced_df = coerce_data_types(df)
            assert isinstance(coerced_df, pd.DataFrame)
        except Exception as e:
            pytest.fail(f"Data type coercion should handle errors gracefully: {e}")


class TestEdgeCases:
    """Test cases for edge cases and boundary conditions."""
    
    def test_load_csv_large_file(self):
        """Test loading large CSV file."""
        # Create a large CSV file
        large_data = []
        for i in range(1000):
            large_data.append(f"S{i:03d},Student {i},CS,Fall,CS{i:03d},Course {i},3.0,{80 + i % 20}")
        
        large_csv = io.BytesIO('\n'.join(large_data).encode('utf-8'))
        df = load_csv(large_csv)
        
        assert len(df) == 1000
        assert len(df.columns) == 8
    
    def test_normalize_column_names_duplicates(self):
        """Test normalization with duplicate column names."""
        df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John'],
            'Department': ['CS'],
            'Semester': ['Fall'],
            'CourseCode': ['CS101'],
            'CourseName': ['Programming'],
            'CreditHours': [3.0],
            'Marks': [85.0]
        })
        
        # Add duplicate column
        df['STUDENTID'] = ['S001']
        
        normalized_df = normalize_column_names(df)
        
        # Should handle duplicates gracefully
        assert 'StudentID' in normalized_df.columns
    
    def test_aggregate_student_records_zero_credits(self):
        """Test aggregation with zero credit hours."""
        df = pd.DataFrame({
            'StudentID': ['S001', 'S001'],
            'Name': ['John', 'John'],
            'Department': ['CS', 'CS'],
            'Semester': ['Fall', 'Fall'],
            'CourseCode': ['CS101', 'CS102'],
            'CourseName': ['Programming I', 'Programming II'],
            'CreditHours': [0.0, 0.0],  # Zero credits
            'Marks': [85.0, 90.0]
        })
        
        aggregated_df = aggregate_student_records(df)
        
        assert len(aggregated_df) == 1
        assert aggregated_df.iloc[0]['TotalCredits'] == 0.0
        assert aggregated_df.iloc[0]['PassFailStatus'] == 'Fail'  # Should fail with zero credits
