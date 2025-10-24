"""
Unit tests for the analytics module.

This module tests cohort analysis, subject statistics, and performance analytics functionality.
"""

import pytest
import pandas as pd
import numpy as np
from typing import Dict, List, Any

from src.analytics import (
    cohort_summary, subject_stats, top_n_students, department_analysis,
    semester_analysis, get_performance_trends, _calculate_student_gpa
)
from src.grading import GradeScale, DEFAULT_4_0_SCALE


class TestCohortSummary:
    """Test cases for cohort summary functionality."""
    
    def test_cohort_summary_valid_data(self, sample_student_data, grade_scale_4_0):
        """Test cohort summary with valid data."""
        summary = cohort_summary(sample_student_data, grade_scale_4_0)
        
        assert isinstance(summary, dict)
        assert 'total_students' in summary
        assert 'total_courses' in summary
        assert 'average_gpa' in summary
        assert 'median_gpa' in summary
        assert 'pass_rate' in summary
        assert 'fail_count' in summary
        assert 'gpa_std_dev' in summary
        assert 'total_credits' in summary
        
        # Check summary values are reasonable
        assert summary['total_students'] == 3
        assert summary['total_courses'] == 6
        assert 0 <= summary['average_gpa'] <= 4
        assert 0 <= summary['median_gpa'] <= 4
        assert 0 <= summary['pass_rate'] <= 100
        assert summary['fail_count'] >= 0
        assert summary['gpa_std_dev'] >= 0
        assert summary['total_credits'] > 0
    
    def test_cohort_summary_empty_data(self, grade_scale_4_0):
        """Test cohort summary with empty data."""
        empty_df = pd.DataFrame()
        summary = cohort_summary(empty_df, grade_scale_4_0)
        
        assert summary['total_students'] == 0
        assert summary['total_courses'] == 0
        assert summary['average_gpa'] == 0.0
        assert summary['median_gpa'] == 0.0
        assert summary['pass_rate'] == 0.0
        assert summary['fail_count'] == 0
        assert summary['gpa_std_dev'] == 0.0
        assert summary['total_credits'] == 0.0
    
    def test_cohort_summary_no_scale(self, sample_student_data):
        """Test cohort summary without grade scale."""
        summary = cohort_summary(sample_student_data, None)
        
        # Should use marks as proxy for GPA
        assert summary['total_students'] == 3
        assert summary['total_courses'] == 6
        assert summary['average_gpa'] > 0  # Should be calculated from marks
        assert summary['pass_rate'] >= 0
    
    def test_cohort_summary_missing_columns(self, grade_scale_4_0):
        """Test cohort summary with missing columns."""
        incomplete_df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John']
        })
        
        summary = cohort_summary(incomplete_df, grade_scale_4_0)
        
        # Should handle missing columns gracefully
        assert summary['total_students'] == 1
        assert summary['total_courses'] == 0
        assert summary['average_gpa'] == 0.0
    
    def test_cohort_summary_failing_students(self, sample_student_data_failing, grade_scale_4_0):
        """Test cohort summary with failing students."""
        summary = cohort_summary(sample_student_data_failing, grade_scale_4_0)
        
        # Should have some failing students
        assert summary['fail_count'] > 0
        assert summary['pass_rate'] < 100.0


class TestSubjectStats:
    """Test cases for subject statistics functionality."""
    
    def test_subject_stats_valid_data(self, sample_student_data, grade_scale_4_0):
        """Test subject statistics with valid data."""
        stats = subject_stats(sample_student_data, grade_scale_4_0)
        
        assert isinstance(stats, list)
        assert len(stats) == 6  # Six unique courses
        
        for stat in stats:
            assert 'course_code' in stat
            assert 'course_name' in stat
            assert 'department' in stat
            assert 'total_students' in stat
            assert 'average_marks' in stat
            assert 'pass_rate' in stat
            assert 'top_scorer' in stat
            assert 'top_score' in stat
            assert 'credit_hours' in stat
            
            # Check values are reasonable
            assert stat['total_students'] > 0
            assert 0 <= stat['average_marks'] <= 100
            assert 0 <= stat['pass_rate'] <= 100
            assert stat['credit_hours'] > 0
    
    def test_subject_stats_empty_data(self, grade_scale_4_0):
        """Test subject statistics with empty data."""
        empty_df = pd.DataFrame()
        stats = subject_stats(empty_df, grade_scale_4_0)
        
        assert stats == []
    
    def test_subject_stats_missing_course_code(self, grade_scale_4_0):
        """Test subject statistics with missing CourseCode column."""
        incomplete_df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John'],
            'Department': ['CS'],
            'Semester': ['Fall'],
            'CourseName': ['Programming'],
            'CreditHours': [3.0],
            'Marks': [85.0]
        })
        
        stats = subject_stats(incomplete_df, grade_scale_4_0)
        
        assert stats == []
    
    def test_subject_stats_sorted_by_average_marks(self, sample_student_data, grade_scale_4_0):
        """Test that subject statistics are sorted by average marks."""
        stats = subject_stats(sample_student_data, grade_scale_4_0)
        
        # Should be sorted by average marks (descending)
        for i in range(len(stats) - 1):
            assert stats[i]['average_marks'] >= stats[i + 1]['average_marks']


class TestTopNStudents:
    """Test cases for top N students functionality."""
    
    def test_top_n_students_valid_data(self, sample_student_data, grade_scale_4_0):
        """Test top N students with valid data."""
        top_students = top_n_students(sample_student_data, n=5, scale=grade_scale_4_0)
        
        assert isinstance(top_students, list)
        assert len(top_students) <= 5
        
        for student in top_students:
            assert 'student_id' in student
            assert 'name' in student
            assert 'department' in student
            assert 'semester' in student
            assert 'gpa' in student
            assert 'total_credits' in student
            assert 'courses_count' in student
            
            # Check values are reasonable
            assert 0 <= student['gpa'] <= 4
            assert student['total_credits'] > 0
            assert student['courses_count'] > 0
    
    def test_top_n_students_empty_data(self, grade_scale_4_0):
        """Test top N students with empty data."""
        empty_df = pd.DataFrame()
        top_students = top_n_students(empty_df, n=5, scale=grade_scale_4_0)
        
        assert top_students == []
    
    def test_top_n_students_missing_student_id(self, grade_scale_4_0):
        """Test top N students with missing StudentID column."""
        incomplete_df = pd.DataFrame({
            'Name': ['John'],
            'Department': ['CS'],
            'Semester': ['Fall'],
            'CourseCode': ['CS101'],
            'CourseName': ['Programming'],
            'CreditHours': [3.0],
            'Marks': [85.0]
        })
        
        top_students = top_n_students(incomplete_df, n=5, scale=grade_scale_4_0)
        
        assert top_students == []
    
    def test_top_n_students_sorted_by_gpa(self, sample_student_data, grade_scale_4_0):
        """Test that top students are sorted by GPA."""
        top_students = top_n_students(sample_student_data, n=10, scale=grade_scale_4_0)
        
        # Should be sorted by GPA (descending)
        for i in range(len(top_students) - 1):
            assert top_students[i]['gpa'] >= top_students[i + 1]['gpa']
    
    def test_top_n_students_no_scale(self, sample_student_data):
        """Test top N students without grade scale."""
        top_students = top_n_students(sample_student_data, n=5, scale=None)
        
        assert isinstance(top_students, list)
        assert len(top_students) <= 5
        
        for student in top_students:
            assert 'gpa' in student
            assert student['gpa'] > 0  # Should be calculated from marks


class TestDepartmentAnalysis:
    """Test cases for department analysis functionality."""
    
    def test_department_analysis_valid_data(self, sample_student_data, grade_scale_4_0):
        """Test department analysis with valid data."""
        dept_analysis = department_analysis(sample_student_data, grade_scale_4_0)
        
        assert isinstance(dept_analysis, dict)
        assert len(dept_analysis) == 3  # Three unique departments
        
        for dept, stats in dept_analysis.items():
            assert 'total_students' in stats
            assert 'total_courses' in stats
            assert 'average_gpa' in stats
            assert 'median_gpa' in stats
            assert 'gpa_std_dev' in stats
            assert 'pass_rate' in stats
            
            # Check values are reasonable
            assert stats['total_students'] > 0
            assert 0 <= stats['average_gpa'] <= 4
            assert 0 <= stats['median_gpa'] <= 4
            assert stats['gpa_std_dev'] >= 0
            assert 0 <= stats['pass_rate'] <= 100
    
    def test_department_analysis_empty_data(self, grade_scale_4_0):
        """Test department analysis with empty data."""
        empty_df = pd.DataFrame()
        dept_analysis = department_analysis(empty_df, grade_scale_4_0)
        
        assert dept_analysis == {}
    
    def test_department_analysis_missing_department(self, grade_scale_4_0):
        """Test department analysis with missing Department column."""
        incomplete_df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John'],
            'Semester': ['Fall'],
            'CourseCode': ['CS101'],
            'CourseName': ['Programming'],
            'CreditHours': [3.0],
            'Marks': [85.0]
        })
        
        dept_analysis = department_analysis(incomplete_df, grade_scale_4_0)
        
        assert dept_analysis == {}
    
    def test_department_analysis_no_scale(self, sample_student_data):
        """Test department analysis without grade scale."""
        dept_analysis = department_analysis(sample_student_data, None)
        
        assert isinstance(dept_analysis, dict)
        assert len(dept_analysis) == 3
        
        for dept, stats in dept_analysis.items():
            assert 'average_gpa' in stats
            assert stats['average_gpa'] > 0  # Should be calculated from marks


class TestSemesterAnalysis:
    """Test cases for semester analysis functionality."""
    
    def test_semester_analysis_valid_data(self, sample_student_data, grade_scale_4_0):
        """Test semester analysis with valid data."""
        sem_analysis = semester_analysis(sample_student_data, grade_scale_4_0)
        
        assert isinstance(sem_analysis, dict)
        assert len(sem_analysis) == 1  # One unique semester
        
        for semester, stats in sem_analysis.items():
            assert 'total_students' in stats
            assert 'total_courses' in stats
            assert 'average_gpa' in stats
            assert 'median_gpa' in stats
            
            # Check values are reasonable
            assert stats['total_students'] > 0
            assert 0 <= stats['average_gpa'] <= 4
            assert 0 <= stats['median_gpa'] <= 4
    
    def test_semester_analysis_empty_data(self, grade_scale_4_0):
        """Test semester analysis with empty data."""
        empty_df = pd.DataFrame()
        sem_analysis = semester_analysis(empty_df, grade_scale_4_0)
        
        assert sem_analysis == {}
    
    def test_semester_analysis_missing_semester(self, grade_scale_4_0):
        """Test semester analysis with missing Semester column."""
        incomplete_df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John'],
            'Department': ['CS'],
            'CourseCode': ['CS101'],
            'CourseName': ['Programming'],
            'CreditHours': [3.0],
            'Marks': [85.0]
        })
        
        sem_analysis = semester_analysis(incomplete_df, grade_scale_4_0)
        
        assert sem_analysis == {}
    
    def test_semester_analysis_multiple_semesters(self, grade_scale_4_0):
        """Test semester analysis with multiple semesters."""
        multi_semester_df = pd.DataFrame({
            'StudentID': ['S001', 'S001', 'S002', 'S002'],
            'Name': ['John', 'John', 'Jane', 'Jane'],
            'Department': ['CS', 'CS', 'Math', 'Math'],
            'Semester': ['Fall 2023', 'Spring 2024', 'Fall 2023', 'Spring 2024'],
            'CourseCode': ['CS101', 'CS102', 'MATH101', 'MATH102'],
            'CourseName': ['Programming I', 'Programming II', 'Calculus I', 'Calculus II'],
            'CreditHours': [3.0, 3.0, 4.0, 4.0],
            'Marks': [85.0, 90.0, 78.0, 82.0]
        })
        
        sem_analysis = semester_analysis(multi_semester_df, grade_scale_4_0)
        
        assert len(sem_analysis) == 2  # Two unique semesters
        assert 'Fall 2023' in sem_analysis
        assert 'Spring 2024' in sem_analysis


class TestPerformanceTrends:
    """Test cases for performance trends functionality."""
    
    def test_get_performance_trends_valid_data(self, sample_student_data, grade_scale_4_0):
        """Test performance trends with valid data."""
        trends = get_performance_trends(sample_student_data, grade_scale_4_0)
        
        assert isinstance(trends, dict)
        assert 'semesters' in trends
        assert 'average_gpa_by_semester' in trends
        assert 'pass_rate_by_semester' in trends
        assert 'total_students_by_semester' in trends
        
        # Check trends data
        assert len(trends['semesters']) == 1
        assert len(trends['average_gpa_by_semester']) == 1
        assert len(trends['pass_rate_by_semester']) == 1
        assert len(trends['total_students_by_semester']) == 1
        
        # Check values are reasonable
        assert 0 <= trends['average_gpa_by_semester'][0] <= 4
        assert 0 <= trends['pass_rate_by_semester'][0] <= 100
        assert trends['total_students_by_semester'][0] > 0
    
    def test_get_performance_trends_empty_data(self, grade_scale_4_0):
        """Test performance trends with empty data."""
        empty_df = pd.DataFrame()
        trends = get_performance_trends(empty_df, grade_scale_4_0)
        
        assert trends == {}
    
    def test_get_performance_trends_missing_semester(self, grade_scale_4_0):
        """Test performance trends with missing Semester column."""
        incomplete_df = pd.DataFrame({
            'StudentID': ['S001'],
            'Name': ['John'],
            'Department': ['CS'],
            'CourseCode': ['CS101'],
            'CourseName': ['Programming'],
            'CreditHours': [3.0],
            'Marks': [85.0]
        })
        
        trends = get_performance_trends(incomplete_df, grade_scale_4_0)
        
        assert trends == {}
    
    def test_get_performance_trends_multiple_semesters(self, grade_scale_4_0):
        """Test performance trends with multiple semesters."""
        multi_semester_df = pd.DataFrame({
            'StudentID': ['S001', 'S001', 'S002', 'S002'],
            'Name': ['John', 'John', 'Jane', 'Jane'],
            'Department': ['CS', 'CS', 'Math', 'Math'],
            'Semester': ['Fall 2023', 'Spring 2024', 'Fall 2023', 'Spring 2024'],
            'CourseCode': ['CS101', 'CS102', 'MATH101', 'MATH102'],
            'CourseName': ['Programming I', 'Programming II', 'Calculus I', 'Calculus II'],
            'CreditHours': [3.0, 3.0, 4.0, 4.0],
            'Marks': [85.0, 90.0, 78.0, 82.0]
        })
        
        trends = get_performance_trends(multi_semester_df, grade_scale_4_0)
        
        assert len(trends['semesters']) == 2
        assert len(trends['average_gpa_by_semester']) == 2
        assert len(trends['pass_rate_by_semester']) == 2
        assert len(trends['total_students_by_semester']) == 2


class TestStudentGPACalculation:
    """Test cases for student GPA calculation functionality."""
    
    def test_calculate_student_gpa_valid_data(self, grade_scale_4_0):
        """Test student GPA calculation with valid data."""
        student_records = pd.DataFrame({
            'Marks': [85.0, 90.0, 78.0],
            'CreditHours': [3.0, 3.0, 4.0]
        })
        
        gpa = _calculate_student_gpa(student_records, grade_scale_4_0)
        
        assert isinstance(gpa, float)
        assert 0 <= gpa <= 4
        
        # Expected GPA: (3.7*3 + 4.0*3 + 2.3*4) / 10 = 3.23
        expected_gpa = (3.7*3 + 4.0*3 + 2.3*4) / 10
        assert abs(gpa - expected_gpa) < 0.01
    
    def test_calculate_student_gpa_empty_data(self, grade_scale_4_0):
        """Test student GPA calculation with empty data."""
        empty_df = pd.DataFrame()
        gpa = _calculate_student_gpa(empty_df, grade_scale_4_0)
        
        assert gpa == 0.0
    
    def test_calculate_student_gpa_missing_columns(self, grade_scale_4_0):
        """Test student GPA calculation with missing columns."""
        incomplete_df = pd.DataFrame({
            'Marks': [85.0, 90.0]
        })
        
        gpa = _calculate_student_gpa(incomplete_df, grade_scale_4_0)
        
        assert gpa == 0.0
    
    def test_calculate_student_gpa_zero_credits(self, grade_scale_4_0):
        """Test student GPA calculation with zero credits."""
        student_records = pd.DataFrame({
            'Marks': [85.0, 90.0],
            'CreditHours': [0.0, 0.0]
        })
        
        gpa = _calculate_student_gpa(student_records, grade_scale_4_0)
        
        assert gpa == 0.0
    
    def test_calculate_student_gpa_single_course(self, grade_scale_4_0):
        """Test student GPA calculation with single course."""
        student_records = pd.DataFrame({
            'Marks': [85.0],
            'CreditHours': [3.0]
        })
        
        gpa = _calculate_student_gpa(student_records, grade_scale_4_0)
        
        # Should be 3.7 (A- grade)
        assert abs(gpa - 3.7) < 0.01


class TestEdgeCases:
    """Test cases for edge cases and boundary conditions."""
    
    def test_cohort_summary_large_dataset(self, grade_scale_4_0):
        """Test cohort summary with large dataset."""
        # Create large dataset
        large_data = []
        for i in range(1000):
            large_data.append({
                'StudentID': f'S{i:03d}',
                'Name': f'Student {i}',
                'Department': 'CS',
                'Semester': 'Fall 2023',
                'CourseCode': f'CS{i:03d}',
                'CourseName': f'Course {i}',
                'CreditHours': 3.0,
                'Marks': 80.0 + (i % 20)
            })
        
        large_df = pd.DataFrame(large_data)
        summary = cohort_summary(large_df, grade_scale_4_0)
        
        assert summary['total_students'] == 1000
        assert summary['total_courses'] == 1000
        assert summary['total_credits'] == 3000.0
    
    def test_subject_stats_duplicate_courses(self, grade_scale_4_0):
        """Test subject statistics with duplicate courses."""
        duplicate_df = pd.DataFrame({
            'StudentID': ['S001', 'S001', 'S002', 'S002'],
            'Name': ['John', 'John', 'Jane', 'Jane'],
            'Department': ['CS', 'CS', 'CS', 'CS'],
            'Semester': ['Fall', 'Fall', 'Fall', 'Fall'],
            'CourseCode': ['CS101', 'CS101', 'CS101', 'CS101'],
            'CourseName': ['Programming', 'Programming', 'Programming', 'Programming'],
            'CreditHours': [3.0, 3.0, 3.0, 3.0],
            'Marks': [85.0, 90.0, 78.0, 82.0]
        })
        
        stats = subject_stats(duplicate_df, grade_scale_4_0)
        
        assert len(stats) == 1  # Only one unique course
        assert stats[0]['total_students'] == 4  # Four student records
        assert stats[0]['average_marks'] == 83.75  # Average of all marks
    
    def test_top_n_students_n_larger_than_students(self, sample_student_data, grade_scale_4_0):
        """Test top N students when N is larger than number of students."""
        top_students = top_n_students(sample_student_data, n=10, scale=grade_scale_4_0)
        
        assert len(top_students) == 3  # Only 3 students available
        assert len(top_students) <= 10  # Should not exceed N
    
    def test_department_analysis_single_department(self, grade_scale_4_0):
        """Test department analysis with single department."""
        single_dept_df = pd.DataFrame({
            'StudentID': ['S001', 'S002'],
            'Name': ['John', 'Jane'],
            'Department': ['CS', 'CS'],
            'Semester': ['Fall', 'Fall'],
            'CourseCode': ['CS101', 'CS102'],
            'CourseName': ['Programming I', 'Programming II'],
            'CreditHours': [3.0, 3.0],
            'Marks': [85.0, 90.0]
        })
        
        dept_analysis = department_analysis(single_dept_df, grade_scale_4_0)
        
        assert len(dept_analysis) == 1
        assert 'CS' in dept_analysis
        assert dept_analysis['CS']['total_students'] == 2
    
    def test_performance_trends_single_semester(self, grade_scale_4_0):
        """Test performance trends with single semester."""
        single_semester_df = pd.DataFrame({
            'StudentID': ['S001', 'S002'],
            'Name': ['John', 'Jane'],
            'Department': ['CS', 'Math'],
            'Semester': ['Fall 2023', 'Fall 2023'],
            'CourseCode': ['CS101', 'MATH101'],
            'CourseName': ['Programming', 'Calculus'],
            'CreditHours': [3.0, 4.0],
            'Marks': [85.0, 90.0]
        })
        
        trends = get_performance_trends(single_semester_df, grade_scale_4_0)
        
        assert len(trends['semesters']) == 1
        assert trends['semesters'][0] == 'Fall 2023'
        assert len(trends['average_gpa_by_semester']) == 1
        assert len(trends['pass_rate_by_semester']) == 1
        assert len(trends['total_students_by_semester']) == 1
