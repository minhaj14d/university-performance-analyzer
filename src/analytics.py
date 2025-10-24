"""
Analytics module for the University Performance Analyzer.

This module provides functions for computing various analytics and insights
from student performance data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

from .models import CohortSummary, SubjectStats, ParsedStudent
from .grading import GradeScale

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cohort_summary(df: pd.DataFrame, scale: Optional[GradeScale] = None) -> Dict[str, Any]:
    """
    Compute comprehensive cohort summary statistics.
    
    Args:
        df: DataFrame with student records
        scale: GradeScale instance for GPA calculation
        
    Returns:
        Dictionary with cohort summary statistics
    """
    try:
        if df.empty:
            return {
                'total_students': 0,
                'total_courses': 0,
                'average_gpa': 0.0,
                'median_gpa': 0.0,
                'pass_rate': 0.0,
                'fail_count': 0,
                'gpa_std_dev': 0.0,
                'total_credits': 0.0
            }
        
        # Basic counts
        total_students = df['StudentID'].nunique() if 'StudentID' in df.columns else 0
        total_courses = df['CourseCode'].nunique() if 'CourseCode' in df.columns else 0
        total_credits = df['CreditHours'].sum() if 'CreditHours' in df.columns else 0.0
        
        # GPA calculation if scale is provided
        if scale and 'Marks' in df.columns and 'CreditHours' in df.columns:
            # Calculate GPA for each student
            student_gpas = []
            for student_id in df['StudentID'].unique():
                student_records = df[df['StudentID'] == student_id]
                gpa = _calculate_student_gpa(student_records, scale)
                student_gpas.append(gpa)
            
            if student_gpas:
                average_gpa = np.mean(student_gpas)
                median_gpa = np.median(student_gpas)
                gpa_std_dev = np.std(student_gpas)
            else:
                average_gpa = median_gpa = gpa_std_dev = 0.0
        else:
            # Use marks as proxy for GPA if no scale provided
            if 'Marks' in df.columns:
                average_gpa = df['Marks'].mean() / 25  # Rough conversion to 4.0 scale
                median_gpa = df['Marks'].median() / 25
                gpa_std_dev = df['Marks'].std() / 25
            else:
                average_gpa = median_gpa = gpa_std_dev = 0.0
        
        # Pass/fail calculation
        if scale and 'Marks' in df.columns:
            passing_threshold = scale.grade_to_points(scale.passing_grade)
            passing_students = 0
            
            for student_id in df['StudentID'].unique():
                student_records = df[df['StudentID'] == student_id]
                student_gpa = _calculate_student_gpa(student_records, scale)
                if student_gpa >= passing_threshold:
                    passing_students += 1
            
            pass_rate = (passing_students / total_students * 100) if total_students > 0 else 0
            fail_count = total_students - passing_students
        else:
            # Use marks threshold (60%) as proxy
            if 'Marks' in df.columns:
                passing_students = 0
                for student_id in df['StudentID'].unique():
                    student_records = df[df['StudentID'] == student_id]
                    avg_marks = student_records['Marks'].mean()
                    if avg_marks >= 60:
                        passing_students += 1
                
                pass_rate = (passing_students / total_students * 100) if total_students > 0 else 0
                fail_count = total_students - passing_students
            else:
                pass_rate = 0.0
                fail_count = total_students
        
        summary = {
            'total_students': int(total_students),
            'total_courses': int(total_courses),
            'average_gpa': round(float(average_gpa), 3),
            'median_gpa': round(float(median_gpa), 3),
            'pass_rate': round(float(pass_rate), 2),
            'fail_count': int(fail_count),
            'gpa_std_dev': round(float(gpa_std_dev), 3),
            'total_credits': round(float(total_credits), 1)
        }
        
        logger.info(f"Computed cohort summary for {total_students} students")
        return summary
        
    except Exception as e:
        logger.error(f"Error computing cohort summary: {str(e)}")
        raise ValueError(f"Error computing cohort summary: {str(e)}")


def subject_stats(df: pd.DataFrame, scale: Optional[GradeScale] = None) -> List[Dict[str, Any]]:
    """
    Compute subject-wise statistics.
    
    Args:
        df: DataFrame with student records
        scale: GradeScale instance for grade calculation
        
    Returns:
        List of dictionaries with subject statistics
    """
    try:
        if df.empty or 'CourseCode' not in df.columns:
            return []
        
        subject_stats_list = []
        
        for course_code in df['CourseCode'].unique():
            course_df = df[df['CourseCode'] == course_code]
            
            # Basic course info
            course_name = course_df['CourseName'].iloc[0] if 'CourseName' in course_df.columns else course_code
            department = course_df['Department'].iloc[0] if 'Department' in course_df.columns else 'Unknown'
            credit_hours = course_df['CreditHours'].iloc[0] if 'CreditHours' in course_df.columns else 0
            
            # Student statistics
            total_students = len(course_df)
            average_marks = course_df['Marks'].mean() if 'Marks' in course_df.columns else 0
            
            # Top scorer
            if 'Marks' in course_df.columns and 'Name' in course_df.columns:
                top_idx = course_df['Marks'].idxmax()
                top_scorer = course_df.loc[top_idx, 'Name']
                top_score = course_df.loc[top_idx, 'Marks']
            else:
                top_scorer = None
                top_score = None
            
            # Pass rate calculation
            if scale and 'Marks' in course_df.columns:
                passing_threshold = scale.grade_to_points(scale.passing_grade) * 25  # Convert to marks scale
                passing_students = (course_df['Marks'] >= passing_threshold).sum()
                pass_rate = (passing_students / total_students * 100) if total_students > 0 else 0
            else:
                # Use 60% as default passing threshold
                passing_students = (course_df['Marks'] >= 60).sum() if 'Marks' in course_df.columns else 0
                pass_rate = (passing_students / total_students * 100) if total_students > 0 else 0
            
            subject_stat = {
                'course_code': course_code,
                'course_name': course_name,
                'department': department,
                'total_students': int(total_students),
                'average_marks': round(float(average_marks), 2),
                'pass_rate': round(float(pass_rate), 2),
                'top_scorer': top_scorer,
                'top_score': round(float(top_score), 2) if top_score is not None else None,
                'credit_hours': round(float(credit_hours), 1)
            }
            
            subject_stats_list.append(subject_stat)
        
        # Sort by average marks (descending)
        subject_stats_list.sort(key=lambda x: x['average_marks'], reverse=True)
        
        logger.info(f"Computed statistics for {len(subject_stats_list)} subjects")
        return subject_stats_list
        
    except Exception as e:
        logger.error(f"Error computing subject statistics: {str(e)}")
        raise ValueError(f"Error computing subject statistics: {str(e)}")


def top_n_students(df: pd.DataFrame, n: int = 10, scale: Optional[GradeScale] = None) -> List[Dict[str, Any]]:
    """
    Get top N students by GPA.
    
    Args:
        df: DataFrame with student records
        n: Number of top students to return
        scale: GradeScale instance for GPA calculation
        
    Returns:
        List of dictionaries with top student information
    """
    try:
        if df.empty or 'StudentID' not in df.columns:
            return []
        
        # Calculate GPA for each student
        student_gpas = []
        
        for student_id in df['StudentID'].unique():
            student_records = df[df['StudentID'] == student_id]
            
            if scale and 'Marks' in student_records.columns and 'CreditHours' in student_records.columns:
                gpa = _calculate_student_gpa(student_records, scale)
            else:
                # Use average marks as proxy for GPA
                gpa = student_records['Marks'].mean() / 25 if 'Marks' in student_records.columns else 0
            
            # Get student info
            student_info = {
                'student_id': student_id,
                'name': student_records['Name'].iloc[0] if 'Name' in student_records.columns else 'Unknown',
                'department': student_records['Department'].iloc[0] if 'Department' in student_records.columns else 'Unknown',
                'semester': student_records['Semester'].iloc[0] if 'Semester' in student_records.columns else 'Unknown',
                'gpa': round(float(gpa), 3),
                'total_credits': student_records['CreditHours'].sum() if 'CreditHours' in student_records.columns else 0,
                'courses_count': len(student_records)
            }
            
            student_gpas.append(student_info)
        
        # Sort by GPA (descending)
        student_gpas.sort(key=lambda x: x['gpa'], reverse=True)
        
        # Return top N students
        top_students = student_gpas[:n]
        
        logger.info(f"Computed top {len(top_students)} students")
        return top_students
        
    except Exception as e:
        logger.error(f"Error computing top students: {str(e)}")
        raise ValueError(f"Error computing top students: {str(e)}")


def department_analysis(df: pd.DataFrame, scale: Optional[GradeScale] = None) -> Dict[str, Any]:
    """
    Analyze performance by department.
    
    Args:
        df: DataFrame with student records
        scale: GradeScale instance for GPA calculation
        
    Returns:
        Dictionary with department-wise analysis
    """
    try:
        if df.empty or 'Department' not in df.columns:
            return {}
        
        dept_analysis = {}
        
        for dept in df['Department'].unique():
            dept_df = df[df['Department'] == dept]
            
            # Basic statistics
            total_students = dept_df['StudentID'].nunique()
            total_courses = dept_df['CourseCode'].nunique()
            
            # GPA calculation
            if scale and 'Marks' in dept_df.columns and 'CreditHours' in dept_df.columns:
                dept_gpas = []
                for student_id in dept_df['StudentID'].unique():
                    student_records = dept_df[dept_df['StudentID'] == student_id]
                    gpa = _calculate_student_gpa(student_records, scale)
                    dept_gpas.append(gpa)
                
                if dept_gpas:
                    avg_gpa = np.mean(dept_gpas)
                    median_gpa = np.median(dept_gpas)
                    gpa_std = np.std(dept_gpas)
                else:
                    avg_gpa = median_gpa = gpa_std = 0.0
            else:
                # Use marks as proxy
                if 'Marks' in dept_df.columns:
                    avg_gpa = dept_df['Marks'].mean() / 25
                    median_gpa = dept_df['Marks'].median() / 25
                    gpa_std = dept_df['Marks'].std() / 25
                else:
                    avg_gpa = median_gpa = gpa_std = 0.0
            
            # Pass rate
            if scale and 'Marks' in dept_df.columns:
                passing_threshold = scale.grade_to_points(scale.passing_grade)
                passing_students = 0
                
                for student_id in dept_df['StudentID'].unique():
                    student_records = dept_df[dept_df['StudentID'] == student_id]
                    student_gpa = _calculate_student_gpa(student_records, scale)
                    if student_gpa >= passing_threshold:
                        passing_students += 1
                
                pass_rate = (passing_students / total_students * 100) if total_students > 0 else 0
            else:
                # Use 60% marks threshold
                if 'Marks' in dept_df.columns:
                    passing_students = 0
                    for student_id in dept_df['StudentID'].unique():
                        student_records = dept_df[dept_df['StudentID'] == student_id]
                        avg_marks = student_records['Marks'].mean()
                        if avg_marks >= 60:
                            passing_students += 1
                    
                    pass_rate = (passing_students / total_students * 100) if total_students > 0 else 0
                else:
                    pass_rate = 0.0
            
            dept_analysis[dept] = {
                'total_students': int(total_students),
                'total_courses': int(total_courses),
                'average_gpa': round(float(avg_gpa), 3),
                'median_gpa': round(float(median_gpa), 3),
                'gpa_std_dev': round(float(gpa_std), 3),
                'pass_rate': round(float(pass_rate), 2)
            }
        
        logger.info(f"Computed department analysis for {len(dept_analysis)} departments")
        return dept_analysis
        
    except Exception as e:
        logger.error(f"Error computing department analysis: {str(e)}")
        raise ValueError(f"Error computing department analysis: {str(e)}")


def semester_analysis(df: pd.DataFrame, scale: Optional[GradeScale] = None) -> Dict[str, Any]:
    """
    Analyze performance by semester.
    
    Args:
        df: DataFrame with student records
        scale: GradeScale instance for GPA calculation
        
    Returns:
        Dictionary with semester-wise analysis
    """
    try:
        if df.empty or 'Semester' not in df.columns:
            return {}
        
        semester_analysis = {}
        
        for semester in df['Semester'].unique():
            sem_df = df[df['Semester'] == semester]
            
            # Basic statistics
            total_students = sem_df['StudentID'].nunique()
            total_courses = sem_df['CourseCode'].nunique()
            
            # GPA calculation
            if scale and 'Marks' in sem_df.columns and 'CreditHours' in sem_df.columns:
                sem_gpas = []
                for student_id in sem_df['StudentID'].unique():
                    student_records = sem_df[sem_df['StudentID'] == student_id]
                    gpa = _calculate_student_gpa(student_records, scale)
                    sem_gpas.append(gpa)
                
                if sem_gpas:
                    avg_gpa = np.mean(sem_gpas)
                    median_gpa = np.median(sem_gpas)
                else:
                    avg_gpa = median_gpa = 0.0
            else:
                # Use marks as proxy
                if 'Marks' in sem_df.columns:
                    avg_gpa = sem_df['Marks'].mean() / 25
                    median_gpa = sem_df['Marks'].median() / 25
                else:
                    avg_gpa = median_gpa = 0.0
            
            semester_analysis[semester] = {
                'total_students': int(total_students),
                'total_courses': int(total_courses),
                'average_gpa': round(float(avg_gpa), 3),
                'median_gpa': round(float(median_gpa), 3)
            }
        
        logger.info(f"Computed semester analysis for {len(semester_analysis)} semesters")
        return semester_analysis
        
    except Exception as e:
        logger.error(f"Error computing semester analysis: {str(e)}")
        raise ValueError(f"Error computing semester analysis: {str(e)}")


def _calculate_student_gpa(student_records: pd.DataFrame, scale: GradeScale) -> float:
    """
    Calculate GPA for a single student.
    
    Args:
        student_records: DataFrame with student's course records
        scale: GradeScale instance
        
    Returns:
        GPA for the student
    """
    if student_records.empty or 'Marks' not in student_records.columns or 'CreditHours' not in student_records.columns:
        return 0.0
    
    # Calculate weighted average
    total_points = 0.0
    total_credits = 0.0
    
    for _, record in student_records.iterrows():
        marks = record['Marks']
        credits = record['CreditHours']
        
        if credits > 0:  # Only include courses with credits
            points = scale.marks_to_points(marks)
            total_points += points * credits
            total_credits += credits
    
    if total_credits == 0:
        return 0.0
    
    return round(total_points / total_credits, 3)


def get_performance_trends(df: pd.DataFrame, scale: Optional[GradeScale] = None) -> Dict[str, Any]:
    """
    Analyze performance trends over time.
    
    Args:
        df: DataFrame with student records
        scale: GradeScale instance for GPA calculation
        
    Returns:
        Dictionary with trend analysis
    """
    try:
        if df.empty or 'Semester' not in df.columns:
            return {}
        
        # Sort by semester
        semesters = sorted(df['Semester'].unique())
        
        trends = {
            'semesters': semesters,
            'average_gpa_by_semester': [],
            'pass_rate_by_semester': [],
            'total_students_by_semester': []
        }
        
        for semester in semesters:
            sem_df = df[df['Semester'] == semester]
            
            # Calculate average GPA for semester
            if scale and 'Marks' in sem_df.columns and 'CreditHours' in sem_df.columns:
                sem_gpas = []
                for student_id in sem_df['StudentID'].unique():
                    student_records = sem_df[sem_df['StudentID'] == student_id]
                    gpa = _calculate_student_gpa(student_records, scale)
                    sem_gpas.append(gpa)
                
                avg_gpa = np.mean(sem_gpas) if sem_gpas else 0.0
            else:
                avg_gpa = sem_df['Marks'].mean() / 25 if 'Marks' in sem_df.columns else 0.0
            
            # Calculate pass rate
            if scale and 'Marks' in sem_df.columns:
                passing_threshold = scale.grade_to_points(scale.passing_grade)
                passing_students = 0
                total_students = sem_df['StudentID'].nunique()
                
                for student_id in sem_df['StudentID'].unique():
                    student_records = sem_df[sem_df['StudentID'] == student_id]
                    student_gpa = _calculate_student_gpa(student_records, scale)
                    if student_gpa >= passing_threshold:
                        passing_students += 1
                
                pass_rate = (passing_students / total_students * 100) if total_students > 0 else 0
            else:
                pass_rate = 0.0
            
            trends['average_gpa_by_semester'].append(round(float(avg_gpa), 3))
            trends['pass_rate_by_semester'].append(round(float(pass_rate), 2))
            trends['total_students_by_semester'].append(int(sem_df['StudentID'].nunique()))
        
        logger.info(f"Computed performance trends for {len(semesters)} semesters")
        return trends
        
    except Exception as e:
        logger.error(f"Error computing performance trends: {str(e)}")
        raise ValueError(f"Error computing performance trends: {str(e)}")
