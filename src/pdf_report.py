"""
PDF report generation module for the University Performance Analyzer.

This module handles the generation of comprehensive PDF reports with charts,
tables, and analytics.
"""

import io
import tempfile
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.utils import ImageReader

from .config import get_settings
from .models import PDFReportConfig
from .analytics import cohort_summary, subject_stats, top_n_students, department_analysis
from .grading import GradeScale

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """PDF report generator with comprehensive analytics and charts."""
    
    def __init__(self, config: PDFReportConfig):
        """
        Initialize PDF report generator.
        
        Args:
            config: PDFReportConfig instance with report settings
        """
        self.config = config
        self.settings = get_settings()
        self.temp_files = []  # Track temporary files for cleanup
    
    def generate_report(
        self, 
        df: pd.DataFrame, 
        scale: Optional[GradeScale] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Generate comprehensive PDF report.
        
        Args:
            df: DataFrame with student records
            scale: GradeScale instance for GPA calculation
            metadata: Additional metadata for the report
            
        Returns:
            PDF content as bytes
        """
        try:
            # Create temporary file for PDF
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.close()
            self.temp_files.append(temp_file.name)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                temp_file.name,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build story (content)
            story = []
            
            # Title page
            story.extend(self._create_title_page(metadata))
            story.append(PageBreak())
            
            # Executive summary
            story.extend(self._create_executive_summary(df, scale))
            story.append(PageBreak())
            
            # Cohort analytics
            story.extend(self._create_cohort_analytics(df, scale))
            story.append(PageBreak())
            
            # Subject performance
            if self.config.include_subject_stats:
                story.extend(self._create_subject_performance(df, scale))
                story.append(PageBreak())
            
            # Top performers
            if self.config.include_leaderboard:
                story.extend(self._create_leaderboard(df, scale))
                story.append(PageBreak())
            
            # Department analysis
            story.extend(self._create_department_analysis(df, scale))
            story.append(PageBreak())
            
            # Student details (if specific students selected)
            if self.config.selected_students:
                story.extend(self._create_student_details(df, scale))
                story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            
            # Read PDF content
            with open(temp_file.name, 'rb') as f:
                pdf_content = f.read()
            
            logger.info(f"Generated PDF report with {len(story)} elements")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise ValueError(f"Error generating PDF report: {str(e)}")
        finally:
            # Clean up temporary files
            self._cleanup_temp_files()
    
    def _create_title_page(self, metadata: Optional[Dict[str, Any]]) -> List:
        """Create title page for the report."""
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=getSampleStyleSheet()['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        story.append(Paragraph(self.config.title, title_style))
        story.append(Spacer(1, 20))
        
        # Institution info
        institution_style = ParagraphStyle(
            'Institution',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        story.append(Paragraph(f"Institution: {self.config.institution}", institution_style))
        story.append(Spacer(1, 20))
        
        # Report metadata
        if metadata:
            metadata_style = ParagraphStyle(
                'Metadata',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=12,
                alignment=TA_CENTER
            )
            
            for key, value in metadata.items():
                story.append(Paragraph(f"<b>{key}:</b> {value}", metadata_style))
                story.append(Spacer(1, 5))
        
        # Generation date
        date_style = ParagraphStyle(
            'Date',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", date_style))
        
        return story
    
    def _create_executive_summary(self, df: pd.DataFrame, scale: Optional[GradeScale]) -> List:
        """Create executive summary section."""
        story = []
        
        # Section title
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        story.append(Paragraph("Executive Summary", title_style))
        
        # Get cohort summary
        summary = cohort_summary(df, scale)
        
        # Create summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Students', str(summary['total_students'])],
            ['Total Courses', str(summary['total_courses'])],
            ['Average GPA', f"{summary['average_gpa']:.3f}"],
            ['Median GPA', f"{summary['median_gpa']:.3f}"],
            ['Pass Rate', f"{summary['pass_rate']:.1f}%"],
            ['Total Credits', f"{summary['total_credits']:.1f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Key insights
        insights_style = ParagraphStyle(
            'Insights',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=12,
            spaceAfter=6
        )
        
        insights = [
            f"• The cohort consists of {summary['total_students']} students across {summary['total_courses']} courses.",
            f"• Overall pass rate is {summary['pass_rate']:.1f}%, with {summary['fail_count']} students failing.",
            f"• Average GPA of {summary['average_gpa']:.3f} indicates {'strong' if summary['average_gpa'] >= 3.0 else 'moderate' if summary['average_gpa'] >= 2.5 else 'weak'} performance.",
            f"• Total credit hours: {summary['total_credits']:.1f} across all students."
        ]
        
        for insight in insights:
            story.append(Paragraph(insight, insights_style))
        
        return story
    
    def _create_cohort_analytics(self, df: pd.DataFrame, scale: Optional[GradeScale]) -> List:
        """Create cohort analytics section."""
        story = []
        
        # Section title
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        story.append(Paragraph("Cohort Analytics", title_style))
        
        # GPA distribution
        if scale and 'Marks' in df.columns and 'CreditHours' in df.columns:
            gpa_data = []
            for student_id in df['StudentID'].unique():
                student_records = df[df['StudentID'] == student_id]
                gpa = self._calculate_student_gpa(student_records, scale)
                gpa_data.append(gpa)
            
            if gpa_data:
                gpa_stats = {
                    'mean': np.mean(gpa_data),
                    'median': np.median(gpa_data),
                    'std': np.std(gpa_data),
                    'min': np.min(gpa_data),
                    'max': np.max(gpa_data)
                }
                
                # GPA distribution table
                gpa_data_table = [
                    ['GPA Statistics', 'Value'],
                    ['Mean GPA', f"{gpa_stats['mean']:.3f}"],
                    ['Median GPA', f"{gpa_stats['median']:.3f}"],
                    ['Standard Deviation', f"{gpa_stats['std']:.3f}"],
                    ['Minimum GPA', f"{gpa_stats['min']:.3f}"],
                    ['Maximum GPA', f"{gpa_stats['max']:.3f}"]
                ]
                
                gpa_table = Table(gpa_data_table, colWidths=[2*inch, 1.5*inch])
                gpa_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(gpa_table)
                story.append(Spacer(1, 20))
        
        return story
    
    def _create_subject_performance(self, df: pd.DataFrame, scale: Optional[GradeScale]) -> List:
        """Create subject performance section."""
        story = []
        
        # Section title
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        story.append(Paragraph("Subject Performance", title_style))
        
        # Get subject statistics
        subject_stats_list = subject_stats(df, scale)
        
        if subject_stats_list:
            # Create subject performance table
            subject_data = [['Course Code', 'Course Name', 'Students', 'Avg Marks', 'Pass Rate', 'Top Score']]
            
            for stat in subject_stats_list[:10]:  # Top 10 subjects
                subject_data.append([
                    stat['course_code'],
                    stat['course_name'][:30] + '...' if len(stat['course_name']) > 30 else stat['course_name'],
                    str(stat['total_students']),
                    f"{stat['average_marks']:.1f}",
                    f"{stat['pass_rate']:.1f}%",
                    f"{stat['top_score']:.1f}" if stat['top_score'] else 'N/A'
                ])
            
            subject_table = Table(subject_data, colWidths=[1*inch, 2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            subject_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            
            story.append(subject_table)
        
        return story
    
    def _create_leaderboard(self, df: pd.DataFrame, scale: Optional[GradeScale]) -> List:
        """Create top performers leaderboard."""
        story = []
        
        # Section title
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        story.append(Paragraph("Top Performers", title_style))
        
        # Get top students
        top_students = top_n_students(df, n=10, scale=scale)
        
        if top_students:
            # Create leaderboard table
            leaderboard_data = [['Rank', 'Student Name', 'Department', 'GPA', 'Courses', 'Credits']]
            
            for i, student in enumerate(top_students, 1):
                name = student['name']
                if self.config.anonymize_names:
                    name = f"Student {student['student_id']}"
                
                leaderboard_data.append([
                    str(i),
                    name,
                    student['department'],
                    f"{student['gpa']:.3f}",
                    str(student['courses_count']),
                    f"{student['total_credits']:.1f}"
                ])
            
            leaderboard_table = Table(leaderboard_data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            leaderboard_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            story.append(leaderboard_table)
        
        return story
    
    def _create_department_analysis(self, df: pd.DataFrame, scale: Optional[GradeScale]) -> List:
        """Create department analysis section."""
        story = []
        
        # Section title
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        story.append(Paragraph("Department Analysis", title_style))
        
        # Get department analysis
        dept_analysis = department_analysis(df, scale)
        
        if dept_analysis:
            # Create department analysis table
            dept_data = [['Department', 'Students', 'Avg GPA', 'Pass Rate', 'Courses']]
            
            for dept, stats in dept_analysis.items():
                dept_data.append([
                    dept,
                    str(stats['total_students']),
                    f"{stats['average_gpa']:.3f}",
                    f"{stats['pass_rate']:.1f}%",
                    str(stats['total_courses'])
                ])
            
            dept_table = Table(dept_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            dept_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            story.append(dept_table)
        
        return story
    
    def _create_student_details(self, df: pd.DataFrame, scale: Optional[GradeScale]) -> List:
        """Create detailed student information section."""
        story = []
        
        # Section title
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        story.append(Paragraph("Student Details", title_style))
        
        # Filter for selected students
        if self.config.selected_students:
            selected_df = df[df['StudentID'].isin(self.config.selected_students)]
        else:
            selected_df = df
        
        # Create student details table
        student_data = [['Student ID', 'Name', 'Department', 'Semester', 'Course', 'Marks', 'Credits']]
        
        for _, row in selected_df.iterrows():
            name = row['Name']
            if self.config.anonymize_names:
                name = f"Student {row['StudentID']}"
            
            student_data.append([
                row['StudentID'],
                name,
                row['Department'],
                row['Semester'],
                row['CourseCode'],
                f"{row['Marks']:.1f}",
                f"{row['CreditHours']:.1f}"
            ])
        
        student_table = Table(student_data, colWidths=[1*inch, 1.5*inch, 1*inch, 0.8*inch, 1*inch, 0.8*inch, 0.8*inch])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        
        story.append(student_table)
        
        return story
    
    def _calculate_student_gpa(self, student_records: pd.DataFrame, scale: GradeScale) -> float:
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
    
    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Could not delete temporary file {temp_file}: {str(e)}")


def generate_pdf_report(
    df: pd.DataFrame, 
    metadata: Optional[Dict[str, Any]] = None,
    config: Optional[PDFReportConfig] = None,
    scale: Optional[GradeScale] = None
) -> bytes:
    """
    Generate PDF report for student performance data.
    
    Args:
        df: DataFrame with student records
        metadata: Additional metadata for the report
        config: PDFReportConfig instance
        scale: GradeScale instance for GPA calculation
        
    Returns:
        PDF content as bytes
    """
    if config is None:
        config = PDFReportConfig()
    
    generator = PDFReportGenerator(config)
    return generator.generate_report(df, scale, metadata)
