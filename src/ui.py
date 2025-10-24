"""
UI components module for the University Performance Analyzer.

This module provides reusable Streamlit UI components and helper functions
for creating a consistent and responsive user interface.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

from .config import DEFAULT_CHART_HEIGHT, KPI_CARDS_PER_ROW

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def kpi_card(title: str, value: Any, delta: Optional[float] = None, delta_label: Optional[str] = None) -> None:
    """
    Create a KPI card with title, value, and optional delta.
    
    Args:
        title: Card title
        value: Main value to display
        delta: Delta value (positive/negative)
        delta_label: Label for delta (e.g., "vs last period")
    """
    with st.container():
        st.metric(
            label=title,
            value=value,
            delta=delta,
            delta_color="normal" if delta is None else ("normal" if delta >= 0 else "inverse")
        )


def plot_gpa_histogram(gpa_series: pd.Series, title: str = "GPA Distribution") -> go.Figure:
    """
    Create a histogram of GPA distribution.
    
    Args:
        gpa_series: Series of GPA values
        title: Chart title
        
    Returns:
        Plotly figure
    """
    try:
        fig = px.histogram(
            gpa_series,
            nbins=20,
            title=title,
            labels={'value': 'GPA', 'count': 'Number of Students'},
            color_discrete_sequence=['#1f77b4']
        )
        
        fig.update_layout(
            height=DEFAULT_CHART_HEIGHT,
            showlegend=False,
            xaxis_title="GPA",
            yaxis_title="Number of Students",
            title_x=0.5
        )
        
        # Add mean line
        mean_gpa = gpa_series.mean()
        fig.add_vline(
            x=mean_gpa,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_gpa:.3f}",
            annotation_position="top"
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating GPA histogram: {str(e)}")
        st.error(f"Error creating GPA histogram: {str(e)}")
        return go.Figure()


def plot_subject_averages(df: pd.DataFrame, title: str = "Subject Performance") -> go.Figure:
    """
    Create a bar chart of subject average marks.
    
    Args:
        df: DataFrame with subject data
        title: Chart title
        
    Returns:
        Plotly figure
    """
    try:
        # Calculate subject averages
        subject_avg = df.groupby('CourseCode').agg({
            'Marks': 'mean',
            'CourseName': 'first'
        }).reset_index()
        
        # Sort by average marks
        subject_avg = subject_avg.sort_values('Marks', ascending=True)
        
        # Limit to top 15 subjects for readability
        subject_avg = subject_avg.tail(15)
        
        fig = px.bar(
            subject_avg,
            x='Marks',
            y='CourseCode',
            title=title,
            labels={'Marks': 'Average Marks', 'CourseCode': 'Course Code'},
            color='Marks',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            height=DEFAULT_CHART_HEIGHT,
            xaxis_title="Average Marks",
            yaxis_title="Course Code",
            title_x=0.5,
            showlegend=False
        )
        
        # Add hover information
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>Average Marks: %{x:.1f}<extra></extra>"
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating subject averages chart: {str(e)}")
        st.error(f"Error creating subject averages chart: {str(e)}")
        return go.Figure()


def plot_pass_fail_pie(df: pd.DataFrame, scale: Optional[Any] = None) -> go.Figure:
    """
    Create a pie chart showing pass/fail distribution.
    
    Args:
        df: DataFrame with student data
        scale: GradeScale instance for pass/fail calculation
        
    Returns:
        Plotly figure
    """
    try:
        # Calculate pass/fail counts
        if scale and 'Marks' in df.columns and 'CreditHours' in df.columns:
            # Calculate GPA for each student
            student_gpas = []
            for student_id in df['StudentID'].unique():
                student_records = df[df['StudentID'] == student_id]
                gpa = _calculate_student_gpa(student_records, scale)
                student_gpas.append(gpa)
            
            # Determine pass/fail based on GPA
            passing_threshold = scale.grade_to_points(scale.passing_grade)
            pass_count = sum(1 for gpa in student_gpas if gpa >= passing_threshold)
            fail_count = len(student_gpas) - pass_count
        else:
            # Use marks threshold (60%) as proxy
            if 'Marks' in df.columns:
                student_avg_marks = df.groupby('StudentID')['Marks'].mean()
                pass_count = (student_avg_marks >= 60).sum()
                fail_count = len(student_avg_marks) - pass_count
            else:
                pass_count = fail_count = 0
        
        # Create pie chart data
        labels = ['Pass', 'Fail']
        values = [pass_count, fail_count]
        colors = ['#2E8B57', '#DC143C']  # Green for pass, red for fail
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='auto'
        )])
        
        fig.update_layout(
            title="Pass/Fail Distribution",
            height=DEFAULT_CHART_HEIGHT,
            title_x=0.5
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating pass/fail pie chart: {str(e)}")
        st.error(f"Error creating pass/fail pie chart: {str(e)}")
        return go.Figure()


def plot_department_performance(df: pd.DataFrame, scale: Optional[Any] = None) -> go.Figure:
    """
    Create a bar chart showing department performance.
    
    Args:
        df: DataFrame with student data
        scale: GradeScale instance for GPA calculation
        
    Returns:
        Plotly figure
    """
    try:
        if 'Department' not in df.columns:
            return go.Figure()
        
        # Calculate department statistics
        dept_stats = []
        for dept in df['Department'].unique():
            dept_df = df[df['Department'] == dept]
            
            if scale and 'Marks' in dept_df.columns and 'CreditHours' in dept_df.columns:
                # Calculate average GPA for department
                dept_gpas = []
                for student_id in dept_df['StudentID'].unique():
                    student_records = dept_df[dept_df['StudentID'] == student_id]
                    gpa = _calculate_student_gpa(student_records, scale)
                    dept_gpas.append(gpa)
                
                avg_gpa = np.mean(dept_gpas) if dept_gpas else 0
            else:
                # Use average marks as proxy
                avg_gpa = dept_df['Marks'].mean() / 25 if 'Marks' in dept_df.columns else 0
            
            dept_stats.append({
                'Department': dept,
                'Average_GPA': avg_gpa,
                'Student_Count': dept_df['StudentID'].nunique()
            })
        
        dept_df = pd.DataFrame(dept_stats)
        dept_df = dept_df.sort_values('Average_GPA', ascending=True)
        
        fig = px.bar(
            dept_df,
            x='Average_GPA',
            y='Department',
            title="Department Performance",
            labels={'Average_GPA': 'Average GPA', 'Department': 'Department'},
            color='Average_GPA',
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(
            height=DEFAULT_CHART_HEIGHT,
            xaxis_title="Average GPA",
            yaxis_title="Department",
            title_x=0.5,
            showlegend=False
        )
        
        # Add hover information
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>Average GPA: %{x:.3f}<extra></extra>"
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating department performance chart: {str(e)}")
        st.error(f"Error creating department performance chart: {str(e)}")
        return go.Figure()


def plot_semester_trends(df: pd.DataFrame, scale: Optional[Any] = None) -> go.Figure:
    """
    Create a line chart showing performance trends over semesters.
    
    Args:
        df: DataFrame with student data
        scale: GradeScale instance for GPA calculation
        
    Returns:
        Plotly figure
    """
    try:
        if 'Semester' not in df.columns:
            return go.Figure()
        
        # Calculate semester statistics
        semester_stats = []
        for semester in sorted(df['Semester'].unique()):
            sem_df = df[df['Semester'] == semester]
            
            if scale and 'Marks' in sem_df.columns and 'CreditHours' in sem_df.columns:
                # Calculate average GPA for semester
                sem_gpas = []
                for student_id in sem_df['StudentID'].unique():
                    student_records = sem_df[sem_df['StudentID'] == student_id]
                    gpa = _calculate_student_gpa(student_records, scale)
                    sem_gpas.append(gpa)
                
                avg_gpa = np.mean(sem_gpas) if sem_gpas else 0
            else:
                # Use average marks as proxy
                avg_gpa = sem_df['Marks'].mean() / 25 if 'Marks' in sem_df.columns else 0
            
            semester_stats.append({
                'Semester': semester,
                'Average_GPA': avg_gpa,
                'Student_Count': sem_df['StudentID'].nunique()
            })
        
        sem_df = pd.DataFrame(semester_stats)
        
        fig = px.line(
            sem_df,
            x='Semester',
            y='Average_GPA',
            title="Performance Trends by Semester",
            labels={'Average_GPA': 'Average GPA', 'Semester': 'Semester'},
            markers=True
        )
        
        fig.update_layout(
            height=DEFAULT_CHART_HEIGHT,
            xaxis_title="Semester",
            yaxis_title="Average GPA",
            title_x=0.5
        )
        
        # Add hover information
        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>Average GPA: %{y:.3f}<extra></extra>"
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating semester trends chart: {str(e)}")
        st.error(f"Error creating semester trends chart: {str(e)}")
        return go.Figure()


def create_leaderboard_table(df: pd.DataFrame, scale: Optional[Any] = None, n: int = 10) -> pd.DataFrame:
    """
    Create a leaderboard table of top students.
    
    Args:
        df: DataFrame with student data
        scale: GradeScale instance for GPA calculation
        n: Number of top students to return
        
    Returns:
        DataFrame with leaderboard data
    """
    try:
        # Calculate GPA for each student
        student_gpas = []
        for student_id in df['StudentID'].unique():
            student_records = df[df['StudentID'] == student_id]
            
            if scale and 'Marks' in student_records.columns and 'CreditHours' in student_records.columns:
                gpa = _calculate_student_gpa(student_records, scale)
            else:
                # Use average marks as proxy
                gpa = student_records['Marks'].mean() / 25 if 'Marks' in student_records.columns else 0
            
            student_info = {
                'Student_ID': student_id,
                'Name': student_records['Name'].iloc[0] if 'Name' in student_records.columns else 'Unknown',
                'Department': student_records['Department'].iloc[0] if 'Department' in student_records.columns else 'Unknown',
                'GPA': gpa,
                'Courses': len(student_records),
                'Total_Credits': student_records['CreditHours'].sum() if 'CreditHours' in student_records.columns else 0
            }
            
            student_gpas.append(student_info)
        
        # Sort by GPA and take top N
        student_gpas.sort(key=lambda x: x['GPA'], reverse=True)
        top_students = student_gpas[:n]
        
        return pd.DataFrame(top_students)
        
    except Exception as e:
        logger.error(f"Error creating leaderboard table: {str(e)}")
        return pd.DataFrame()


def create_subject_leaderboard(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a leaderboard table of subject performance.
    
    Args:
        df: DataFrame with subject data
        
    Returns:
        DataFrame with subject leaderboard data
    """
    try:
        if 'CourseCode' not in df.columns:
            return pd.DataFrame()
        
        # Calculate subject statistics
        subject_stats = df.groupby('CourseCode').agg({
            'Marks': ['mean', 'count'],
            'CourseName': 'first',
            'Department': 'first'
        }).reset_index()
        
        # Flatten column names
        subject_stats.columns = ['CourseCode', 'Average_Marks', 'Student_Count', 'CourseName', 'Department']
        
        # Sort by average marks
        subject_stats = subject_stats.sort_values('Average_Marks', ascending=False)
        
        return subject_stats
        
    except Exception as e:
        logger.error(f"Error creating subject leaderboard: {str(e)}")
        return pd.DataFrame()


def _calculate_student_gpa(student_records: pd.DataFrame, scale: Any) -> float:
    """Calculate GPA for a single student."""
    if student_records.empty or 'Marks' not in student_records.columns or 'CreditHours' not in student_records.columns:
        return 0.0
    
    total_points = 0.0
    total_credits = 0.0
    
    for _, record in student_records.iterrows():
        marks = record['Marks']
        credits = record['CreditHours']
        
        if credits > 0:
            points = scale.marks_to_points(marks)
            total_points += points * credits
            total_credits += credits
    
    if total_credits == 0:
        return 0.0
    
    return round(total_points / total_credits, 3)


def create_kpi_grid(summary: Dict[str, Any], cols: int = KPI_CARDS_PER_ROW) -> None:
    """
    Create a grid of KPI cards.
    
    Args:
        summary: Dictionary with summary statistics
        cols: Number of columns in the grid
    """
    kpis = [
        ('Total Students', summary.get('total_students', 0)),
        ('Average GPA', f"{summary.get('average_gpa', 0):.3f}"),
        ('Pass Rate', f"{summary.get('pass_rate', 0):.1f}%"),
        ('Total Courses', summary.get('total_courses', 0))
    ]
    
    # Create columns
    col_list = st.columns(cols)
    
    for i, (title, value) in enumerate(kpis):
        with col_list[i % cols]:
            kpi_card(title, value)


def create_filter_sidebar(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create filter sidebar for data filtering.
    
    Args:
        df: DataFrame with student data
        
    Returns:
        Dictionary with filter values
    """
    st.sidebar.header("Filters")
    
    filters = {}
    
    # Department filter
    if 'Department' in df.columns:
        departments = ['All'] + sorted(df['Department'].unique().tolist())
        selected_dept = st.sidebar.selectbox("Department", departments)
        if selected_dept != 'All':
            filters['department'] = selected_dept
    
    # Semester filter
    if 'Semester' in df.columns:
        semesters = ['All'] + sorted(df['Semester'].unique().tolist())
        selected_sem = st.sidebar.selectbox("Semester", semesters)
        if selected_sem != 'All':
            filters['semester'] = selected_sem
    
    # GPA range filter
    if 'Marks' in df.columns:
        min_marks = float(df['Marks'].min())
        max_marks = float(df['Marks'].max())
        
        gpa_range = st.sidebar.slider(
            "GPA Range",
            min_value=min_marks/25,  # Convert to GPA scale
            max_value=max_marks/25,
            value=(min_marks/25, max_marks/25),
            step=0.1
        )
        filters['gpa_range'] = gpa_range
    
    # Student search
    student_search = st.sidebar.text_input("Search Student Name")
    if student_search:
        filters['student_search'] = student_search
    
    return filters


def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply filters to DataFrame.
    
    Args:
        df: DataFrame to filter
        filters: Dictionary with filter values
        
    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()
    
    # Department filter
    if 'department' in filters:
        filtered_df = filtered_df[filtered_df['Department'] == filters['department']]
    
    # Semester filter
    if 'semester' in filters:
        filtered_df = filtered_df[filtered_df['Semester'] == filters['semester']]
    
    # GPA range filter
    if 'gpa_range' in filters:
        min_gpa, max_gpa = filters['gpa_range']
        # Convert GPA back to marks scale
        min_marks = min_gpa * 25
        max_marks = max_gpa * 25
        filtered_df = filtered_df[
            (filtered_df['Marks'] >= min_marks) & 
            (filtered_df['Marks'] <= max_marks)
        ]
    
    # Student search
    if 'student_search' in filters:
        search_term = filters['student_search'].lower()
        filtered_df = filtered_df[
            filtered_df['Name'].str.lower().str.contains(search_term, na=False)
        ]
    
    return filtered_df
