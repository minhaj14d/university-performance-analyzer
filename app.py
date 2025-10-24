"""
University Performance Analyzer - Main Streamlit Application

A comprehensive application for analyzing university student performance data.
Provides GPA calculation, subject analytics, and PDF report generation.
"""

import streamlit as st
import pandas as pd
import io
import tempfile
import os
from typing import Dict, List, Any, Optional
import logging

# Import our modules
from src.config import get_settings, ERROR_MESSAGES, SUCCESS_MESSAGES
from src.data_loader import load_csv, validate_csv_columns, get_data_summary
from src.grading import GradeScale, DEFAULT_4_0_SCALE, DEFAULT_100_SCALE
from src.analytics import cohort_summary, subject_stats, top_n_students, department_analysis
from src.pdf_report import generate_pdf_report, PDFReportConfig
from src.ui import (
    kpi_card, plot_gpa_histogram, plot_subject_averages, plot_pass_fail_pie,
    plot_department_performance, plot_semester_trends, create_leaderboard_table,
    create_subject_leaderboard, create_kpi_grid, create_filter_sidebar, apply_filters
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="University Performance Analyzer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'grade_scale' not in st.session_state:
    st.session_state.grade_scale = DEFAULT_4_0_SCALE
if 'filters' not in st.session_state:
    st.session_state.filters = {}


def main():
    """Main application function."""
    # Header
    st.title("🎓 University Performance Analyzer")
    st.markdown("---")
    
    # Sidebar configuration
    configure_sidebar()
    
    # Main content
    if st.session_state.data_loaded and st.session_state.df is not None:
        display_main_content()
    else:
        display_welcome_screen()


def configure_sidebar():
    """Configure the sidebar with controls and settings."""
    st.sidebar.header("⚙️ Configuration")
    
    # Grade scale selection
    st.sidebar.subheader("Grade Scale")
    grade_scale_type = st.sidebar.selectbox(
        "Select Grade Scale",
        ["4.0", "100", "Custom"],
        index=0,
        help="Choose the grade scale for GPA calculation"
    )
    
    if grade_scale_type == "4.0":
        st.session_state.grade_scale = DEFAULT_4_0_SCALE
    elif grade_scale_type == "100":
        st.session_state.grade_scale = DEFAULT_100_SCALE
    else:
        st.sidebar.info("Custom grade scales coming soon!")
    
    # File upload
    st.sidebar.subheader("📁 Data Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV File",
        type=['csv'],
        help="Upload a CSV file with student performance data"
    )
    
    if uploaded_file is not None:
        try:
            # Load and validate CSV
            df = load_csv(uploaded_file)
            st.session_state.df = df
            st.session_state.data_loaded = True
            
            st.sidebar.success(SUCCESS_MESSAGES["data_loaded"].format(count=len(df)))
            
            # Show data summary
            summary = get_data_summary(df)
            st.sidebar.info(f"📊 **Data Summary:**\n- {summary['total_records']} records\n- {summary['unique_students']} students\n- {summary['unique_courses']} courses")
            
        except Exception as e:
            st.sidebar.error(f"Error loading file: {str(e)}")
            st.session_state.data_loaded = False
    
    # Load sample data option
    if st.sidebar.button("📋 Load Sample Data"):
        try:
            from src.data_loader import load_sample_data
            df = load_sample_data()
            st.session_state.df = df
            st.session_state.data_loaded = True
            st.sidebar.success("Sample data loaded successfully!")
        except Exception as e:
            st.sidebar.error(f"Error loading sample data: {str(e)}")
    
    # Display settings
    st.sidebar.subheader("🎨 Display Settings")
    anonymize_names = st.sidebar.checkbox(
        "Anonymize Student Names",
        value=False,
        help="Hide student names for privacy"
    )
    st.session_state.anonymize_names = anonymize_names


def display_welcome_screen():
    """Display welcome screen with instructions."""
    st.markdown("## Welcome to the University Performance Analyzer! 🎓")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📋 How to Use This Application
        
        1. **Upload Data**: Use the sidebar to upload a CSV file with student performance data
        2. **Configure Settings**: Select your preferred grade scale and display options
        3. **Analyze Performance**: View comprehensive analytics, charts, and insights
        4. **Generate Reports**: Create and download PDF reports for your analysis
        
        ### 📊 Required CSV Format
        
        Your CSV file should contain the following columns:
        - `StudentID`: Unique student identifier
        - `Name`: Student full name
        - `Department`: Academic department
        - `Semester`: Academic semester
        - `CourseCode`: Course code
        - `CourseName`: Course name
        - `CreditHours`: Credit hours for the course
        - `Marks`: Marks obtained (0-100)
        
        ### 🚀 Quick Start
        
        Click "Load Sample Data" in the sidebar to explore the application with sample data!
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Features
        
        - **GPA Calculation**: Automatic GPA computation with configurable grade scales
        - **Performance Analytics**: Comprehensive cohort and subject analysis
        - **Interactive Charts**: Visualize data with interactive Plotly charts
        - **PDF Reports**: Generate professional reports for stakeholders
        - **Data Filtering**: Filter and analyze specific cohorts or time periods
        - **Export Options**: Download filtered data and reports
        
        ### 🔧 Technical Features
        
        - **Scalable Architecture**: Handles large datasets efficiently
        - **Caching**: Optimized performance with intelligent caching
        - **Type Safety**: Full type hints and validation
        - **Professional UI**: Clean, responsive, and user-friendly interface
        """)


def display_main_content():
    """Display the main application content."""
    df = st.session_state.df
    
    # Create filters
    st.session_state.filters = create_filter_sidebar(df)
    
    # Apply filters
    filtered_df = apply_filters(df, st.session_state.filters)
    
    if filtered_df.empty:
        st.warning("No data found matching the selected filters. Please adjust your filter settings.")
        return
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", "📈 Analytics", "🏆 Leaderboards", "📋 Details", "📄 Reports"
    ])
    
    with tab1:
        display_overview_tab(filtered_df)
    
    with tab2:
        display_analytics_tab(filtered_df)
    
    with tab3:
        display_leaderboards_tab(filtered_df)
    
    with tab4:
        display_details_tab(filtered_df)
    
    with tab5:
        display_reports_tab(filtered_df)


def display_overview_tab(df: pd.DataFrame):
    """Display the overview tab with KPIs and summary charts."""
    st.header("📊 Performance Overview")
    
    # Calculate summary statistics
    summary = cohort_summary(df, st.session_state.grade_scale)
    
    # KPI Cards
    st.subheader("Key Performance Indicators")
    create_kpi_grid(summary)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("GPA Distribution")
        if 'Marks' in df.columns and 'CreditHours' in df.columns:
            # Calculate GPA for each student
            student_gpas = []
            for student_id in df['StudentID'].unique():
                student_records = df[df['StudentID'] == student_id]
                gpa = _calculate_student_gpa(student_records, st.session_state.grade_scale)
                student_gpas.append(gpa)
            
            if student_gpas:
                gpa_series = pd.Series(student_gpas)
                fig = plot_gpa_histogram(gpa_series)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No GPA data available")
        else:
            st.info("Marks and CreditHours columns required for GPA calculation")
    
    with col2:
        st.subheader("Pass/Fail Distribution")
        fig = plot_pass_fail_pie(df, st.session_state.grade_scale)
        st.plotly_chart(fig, use_container_width=True)
    
    # Additional charts
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Subject Performance")
        fig = plot_subject_averages(df)
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader("Department Performance")
        fig = plot_department_performance(df, st.session_state.grade_scale)
        st.plotly_chart(fig, use_container_width=True)


def display_analytics_tab(df: pd.DataFrame):
    """Display the analytics tab with detailed analysis."""
    st.header("📈 Detailed Analytics")
    
    # Cohort analysis
    st.subheader("Cohort Analysis")
    summary = cohort_summary(df, st.session_state.grade_scale)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Total Students", summary['total_students'])
    with col2:
        kpi_card("Average GPA", f"{summary['average_gpa']:.3f}")
    with col3:
        kpi_card("Pass Rate", f"{summary['pass_rate']:.1f}%")
    with col4:
        kpi_card("Total Credits", f"{summary['total_credits']:.1f}")
    
    # Department analysis
    st.subheader("Department Analysis")
    dept_analysis = department_analysis(df, st.session_state.grade_scale)
    
    if dept_analysis:
        dept_df = pd.DataFrame([
            {
                'Department': dept,
                'Students': stats['total_students'],
                'Avg GPA': f"{stats['average_gpa']:.3f}",
                'Pass Rate': f"{stats['pass_rate']:.1f}%",
                'Courses': stats['total_courses']
            }
            for dept, stats in dept_analysis.items()
        ])
        
        st.dataframe(dept_df, use_container_width=True)
    
    # Semester trends
    if 'Semester' in df.columns:
        st.subheader("Semester Trends")
        fig = plot_semester_trends(df, st.session_state.grade_scale)
        st.plotly_chart(fig, use_container_width=True)


def display_leaderboards_tab(df: pd.DataFrame):
    """Display the leaderboards tab with top performers."""
    st.header("🏆 Leaderboards")
    
    # Top students
    st.subheader("Top Students by GPA")
    top_students = top_n_students(df, n=10, scale=st.session_state.grade_scale)
    
    if top_students:
        # Create leaderboard table
        leaderboard_data = []
        for i, student in enumerate(top_students, 1):
            name = student['name']
            if st.session_state.get('anonymize_names', False):
                name = f"Student {student['student_id']}"
            
            leaderboard_data.append({
                'Rank': i,
                'Student Name': name,
                'Department': student['department'],
                'GPA': f"{student['gpa']:.3f}",
                'Courses': student['courses_count'],
                'Credits': f"{student['total_credits']:.1f}"
            })
        
        leaderboard_df = pd.DataFrame(leaderboard_data)
        st.dataframe(leaderboard_df, use_container_width=True)
    
    # Subject performance
    st.subheader("Subject Performance")
    subject_stats_list = subject_stats(df, st.session_state.grade_scale)
    
    if subject_stats_list:
        subject_data = []
        for stat in subject_stats_list[:15]:  # Top 15 subjects
            subject_data.append({
                'Course Code': stat['course_code'],
                'Course Name': stat['course_name'],
                'Students': stat['total_students'],
                'Avg Marks': f"{stat['average_marks']:.1f}",
                'Pass Rate': f"{stat['pass_rate']:.1f}%",
                'Top Score': f"{stat['top_score']:.1f}" if stat['top_score'] else 'N/A'
            })
        
        subject_df = pd.DataFrame(subject_data)
        st.dataframe(subject_df, use_container_width=True)


def display_details_tab(df: pd.DataFrame):
    """Display the details tab with raw data and student information."""
    st.header("📋 Student Details")
    
    # Student selection
    st.subheader("Select Students")
    student_ids = df['StudentID'].unique()
    selected_students = st.multiselect(
        "Choose students to view details:",
        student_ids,
        default=student_ids[:5] if len(student_ids) > 5 else student_ids
    )
    
    if selected_students:
        # Filter data for selected students
        selected_df = df[df['StudentID'].isin(selected_students)]
        
        # Display student details
        st.subheader("Student Records")
        
        # Anonymize names if requested
        display_df = selected_df.copy()
        if st.session_state.get('anonymize_names', False):
            display_df['Name'] = display_df['StudentID'].apply(lambda x: f"Student {x}")
        
        st.dataframe(display_df, use_container_width=True)
        
        # Individual student analysis
        st.subheader("Individual Student Analysis")
        
        for student_id in selected_students:
            student_df = selected_df[selected_df['StudentID'] == student_id]
            student_name = student_df['Name'].iloc[0]
            
            if st.session_state.get('anonymize_names', False):
                student_name = f"Student {student_id}"
            
            with st.expander(f"📊 {student_name} - Analysis"):
                # Calculate student GPA
                student_gpa = _calculate_student_gpa(student_df, st.session_state.grade_scale)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    kpi_card("GPA", f"{student_gpa:.3f}")
                with col2:
                    kpi_card("Courses", len(student_df))
                with col3:
                    kpi_card("Total Credits", f"{student_df['CreditHours'].sum():.1f}")
                with col4:
                    kpi_card("Avg Marks", f"{student_df['Marks'].mean():.1f}")
                
                # Course breakdown
                st.write("**Course Breakdown:**")
                course_breakdown = student_df[['CourseCode', 'CourseName', 'Marks', 'CreditHours']].copy()
                course_breakdown['Grade'] = course_breakdown['Marks'].apply(
                    lambda x: st.session_state.grade_scale.marks_to_grade(x)
                )
                st.dataframe(course_breakdown, use_container_width=True)


def display_reports_tab(df: pd.DataFrame):
    """Display the reports tab with PDF generation options."""
    st.header("📄 Generate Reports")
    
    # Report configuration
    st.subheader("Report Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_title = st.text_input("Report Title", value="University Performance Report")
        institution = st.text_input("Institution Name", value="University")
        cohort_info = st.text_input("Cohort Information", value="")
    
    with col2:
        include_charts = st.checkbox("Include Charts", value=True)
        include_leaderboard = st.checkbox("Include Leaderboard", value=True)
        include_subject_stats = st.checkbox("Include Subject Statistics", value=True)
        anonymize_names = st.checkbox("Anonymize Student Names", value=st.session_state.get('anonymize_names', False))
    
    # Student selection for report
    st.subheader("Select Students for Report")
    student_ids = df['StudentID'].unique()
    selected_students = st.multiselect(
        "Choose students to include in report:",
        student_ids,
        default=student_ids[:10] if len(student_ids) > 10 else student_ids,
        help="Leave empty to include all students"
    )
    
    # Generate report button
    if st.button("📄 Generate PDF Report", type="primary"):
        try:
            with st.spinner("Generating PDF report..."):
                # Filter data for selected students
                if selected_students:
                    report_df = df[df['StudentID'].isin(selected_students)]
                else:
                    report_df = df
                
                # Create report configuration
                config = PDFReportConfig(
                    title=report_title,
                    institution=institution,
                    cohort_info=cohort_info,
                    include_charts=include_charts,
                    include_leaderboard=include_leaderboard,
                    include_subject_stats=include_subject_stats,
                    anonymize_names=anonymize_names,
                    selected_students=selected_students if selected_students else None
                )
                
                # Generate metadata
                metadata = {
                    "Generated on": pd.Timestamp.now().strftime("%B %d, %Y at %I:%M %p"),
                    "Total Students": len(report_df['StudentID'].unique()),
                    "Total Records": len(report_df),
                    "Grade Scale": st.session_state.grade_scale.scale_type
                }
                
                # Generate PDF
                pdf_bytes = generate_pdf_report(report_df, metadata, config, st.session_state.grade_scale)
                
                # Download button
                st.success("PDF report generated successfully!")
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"university_performance_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                
        except Exception as e:
            st.error(f"Error generating PDF report: {str(e)}")
    
    # Data export
    st.subheader("Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Filtered Data as CSV"):
            try:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"filtered_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error exporting data: {str(e)}")
    
    with col2:
        if st.button("📈 Export Analytics Summary"):
            try:
                summary = cohort_summary(df, st.session_state.grade_scale)
                summary_df = pd.DataFrame([summary])
                csv = summary_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Summary",
                    data=csv,
                    file_name=f"analytics_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error exporting summary: {str(e)}")


def _calculate_student_gpa(student_records: pd.DataFrame, scale: GradeScale) -> float:
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


if __name__ == "__main__":
    main()
