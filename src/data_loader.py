"""
Data loading and validation module for the University Performance Analyzer.

This module handles CSV file loading, validation, and data preprocessing.
"""

import io
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path

from .config import REQUIRED_COLUMNS, COLUMN_MAPPINGS, ERROR_MESSAGES
from .models import StudentRecord, ParsedStudent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoaderError(Exception):
    """Custom exception for data loading errors."""
    pass


class ValidationError(Exception):
    """Custom exception for data validation errors."""
    pass


def validate_csv_columns(df: pd.DataFrame) -> None:
    """
    Validate that the CSV contains all required columns.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValidationError: If required columns are missing
    """
    if df.empty:
        raise ValidationError(ERROR_MESSAGES["empty_file"])
    
    # Check for required columns (case-insensitive)
    df_columns = [col.strip().lower() for col in df.columns]
    required_columns_lower = [col.lower() for col in REQUIRED_COLUMNS]
    
    missing_columns = []
    for req_col in required_columns_lower:
        if req_col not in df_columns:
            missing_columns.append(req_col.upper())
    
    if missing_columns:
        raise ValidationError(
            ERROR_MESSAGES["missing_columns"].format(
                missing_columns=", ".join(missing_columns)
            )
        )
    
    logger.info(f"CSV validation passed. Found {len(df.columns)} columns.")


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to standard format.
    
    Args:
        df: DataFrame with potentially inconsistent column names
        
    Returns:
        DataFrame with normalized column names
    """
    # Create a mapping from current columns to normalized columns
    column_mapping = {}
    
    for col in df.columns:
        col_clean = col.strip().lower()
        
        # Check if this column matches any of our required columns
        for req_col in REQUIRED_COLUMNS:
            if col_clean == req_col.lower():
                column_mapping[col] = req_col
                break
        
        # Check against our flexible column mappings
        for flexible_name, standard_name in COLUMN_MAPPINGS.items():
            if col_clean == flexible_name.lower():
                column_mapping[col] = standard_name
                break
    
    # Rename columns
    df_normalized = df.rename(columns=column_mapping)
    
    logger.info(f"Normalized {len(column_mapping)} column names")
    return df_normalized


def coerce_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Coerce data types for proper processing.
    
    Args:
        df: DataFrame to process
        
    Returns:
        DataFrame with proper data types
    """
    df_processed = df.copy()
    
    try:
        # Convert numeric columns
        if 'CreditHours' in df_processed.columns:
            df_processed['CreditHours'] = pd.to_numeric(
                df_processed['CreditHours'], errors='coerce'
            )
        
        if 'Marks' in df_processed.columns:
            df_processed['Marks'] = pd.to_numeric(
                df_processed['Marks'], errors='coerce'
            )
        
        # Convert string columns and clean them
        string_columns = ['StudentID', 'Name', 'Department', 'Semester', 
                         'CourseCode', 'CourseName']
        
        for col in string_columns:
            if col in df_processed.columns:
                df_processed[col] = df_processed[col].astype(str).str.strip()
        
        # Remove rows with missing critical data
        critical_columns = ['StudentID', 'Name', 'Marks', 'CreditHours']
        initial_rows = len(df_processed)
        
        for col in critical_columns:
            if col in df_processed.columns:
                df_processed = df_processed.dropna(subset=[col])
        
        removed_rows = initial_rows - len(df_processed)
        if removed_rows > 0:
            logger.warning(f"Removed {removed_rows} rows with missing critical data")
        
        logger.info(f"Data type coercion completed. {len(df_processed)} rows remaining.")
        
    except Exception as e:
        raise ValidationError(f"Error processing data types: {str(e)}")
    
    return df_processed


def load_csv(file: io.BytesIO) -> pd.DataFrame:
    """
    Load and validate a CSV file.
    
    Args:
        file: BytesIO object containing CSV data
        
    Returns:
        Validated and processed DataFrame
        
    Raises:
        DataLoaderError: If file cannot be loaded
        ValidationError: If data validation fails
    """
    try:
        # Reset file pointer
        file.seek(0)
        
        # Try to detect encoding
        sample = file.read(1024)
        file.seek(0)
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                file.seek(0)
                df = pd.read_csv(file, encoding=encoding)
                logger.info(f"Successfully loaded CSV with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise DataLoaderError("Could not decode CSV file with any supported encoding")
        
        # Validate columns
        validate_csv_columns(df)
        
        # Normalize column names
        df = normalize_column_names(df)
        
        # Coerce data types
        df = coerce_data_types(df)
        
        logger.info(f"Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        return df
        
    except pd.errors.EmptyDataError:
        raise DataLoaderError(ERROR_MESSAGES["empty_file"])
    except pd.errors.ParserError as e:
        raise DataLoaderError(f"Error parsing CSV: {str(e)}")
    except Exception as e:
        raise DataLoaderError(f"Unexpected error loading CSV: {str(e)}")


def aggregate_student_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate student records by student for GPA calculation.
    
    Args:
        df: DataFrame with individual course records
        
    Returns:
        DataFrame with aggregated student data
    """
    try:
        # Group by student and aggregate
        aggregated = df.groupby(['StudentID', 'Name', 'Department', 'Semester']).agg({
            'CreditHours': 'sum',
            'Marks': 'mean',  # Average marks across courses
            'CourseCode': 'count',  # Number of courses
            'CourseName': lambda x: ', '.join(x.unique())  # All course names
        }).reset_index()
        
        # Rename columns for clarity
        aggregated.columns = [
            'StudentID', 'Name', 'Department', 'Semester',
            'TotalCredits', 'AverageMarks', 'CoursesCount', 'CoursesList'
        ]
        
        # Calculate pass/fail status (assuming 60% is passing)
        aggregated['PassFailStatus'] = aggregated['AverageMarks'].apply(
            lambda x: 'Pass' if x >= 60 else 'Fail'
        )
        
        logger.info(f"Aggregated {len(aggregated)} student records")
        return aggregated
        
    except Exception as e:
        raise DataLoaderError(f"Error aggregating student records: {str(e)}")


def load_sample_data() -> pd.DataFrame:
    """
    Load sample data for testing and demonstration.
    
    Returns:
        DataFrame with sample student data
    """
    try:
        sample_path = Path(SAMPLE_DATA_PATH)
        if not sample_path.exists():
            raise FileNotFoundError(f"Sample data file not found: {sample_path}")
        
        with open(sample_path, 'r', encoding='utf-8') as f:
            df = pd.read_csv(f)
        
        # Validate and process the sample data
        validate_csv_columns(df)
        df = normalize_column_names(df)
        df = coerce_data_types(df)
        
        logger.info(f"Loaded sample data with {len(df)} rows")
        return df
        
    except Exception as e:
        raise DataLoaderError(f"Error loading sample data: {str(e)}")


def validate_student_records(df: pd.DataFrame) -> List[StudentRecord]:
    """
    Validate and convert DataFrame rows to StudentRecord models.
    
    Args:
        df: DataFrame with student records
        
    Returns:
        List of validated StudentRecord objects
        
    Raises:
        ValidationError: If validation fails
    """
    records = []
    errors = []
    
    for index, row in df.iterrows():
        try:
            # Convert row to StudentRecord
            record = StudentRecord(
                student_id=str(row['StudentID']),
                name=str(row['Name']),
                department=str(row['Department']),
                semester=str(row['Semester']),
                course_code=str(row['CourseCode']),
                course_name=str(row['CourseName']),
                credit_hours=float(row['CreditHours']),
                marks=float(row['Marks'])
            )
            records.append(record)
            
        except Exception as e:
            errors.append(f"Row {index + 1}: {str(e)}")
    
    if errors:
        raise ValidationError(f"Validation errors found:\n" + "\n".join(errors))
    
    logger.info(f"Successfully validated {len(records)} student records")
    return records


def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get summary statistics for the loaded data.
    
    Args:
        df: DataFrame to summarize
        
    Returns:
        Dictionary with summary statistics
    """
    try:
        summary = {
            'total_records': len(df),
            'unique_students': df['StudentID'].nunique() if 'StudentID' in df.columns else 0,
            'unique_courses': df['CourseCode'].nunique() if 'CourseCode' in df.columns else 0,
            'departments': df['Department'].unique().tolist() if 'Department' in df.columns else [],
            'semesters': df['Semester'].unique().tolist() if 'Semester' in df.columns else [],
            'date_range': {
                'earliest': df['Semester'].min() if 'Semester' in df.columns else None,
                'latest': df['Semester'].max() if 'Semester' in df.columns else None
            },
            'marks_range': {
                'min': df['Marks'].min() if 'Marks' in df.columns else None,
                'max': df['Marks'].max() if 'Marks' in df.columns else None,
                'mean': df['Marks'].mean() if 'Marks' in df.columns else None
            },
            'credits_range': {
                'min': df['CreditHours'].min() if 'CreditHours' in df.columns else None,
                'max': df['CreditHours'].max() if 'CreditHours' in df.columns else None,
                'total': df['CreditHours'].sum() if 'CreditHours' in df.columns else None
            }
        }
        
        logger.info(f"Generated data summary for {summary['total_records']} records")
        return summary
        
    except Exception as e:
        logger.error(f"Error generating data summary: {str(e)}")
        return {'error': str(e)}


# Constants for sample data path
SAMPLE_DATA_PATH = "sample_data/sample_students.csv"
