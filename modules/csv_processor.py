"""
CSV Processing Module

This module handles CSV file processing and data standardization for
the personal finance tool. It supports flexible CSV formats from different
banks and provides data cleaning and validation capabilities.

Designed for beginners with clear documentation and robust error handling.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVProcessor:
    """
    Handles CSV file processing and standardization for bank transaction data.
    
    This class provides:
    - Flexible CSV format detection
    - Data cleaning and standardization
    - Support for multiple date and amount formats
    - Column mapping and validation
    - Error handling and data validation
    """
    
    def __init__(self):
        """Initialize CSV processor with common date and amount formats."""
        
        # Common date formats used by banks
        self.date_formats = [
            '%Y-%m-%d',          # 2023-12-31
            '%d/%m/%Y',          # 31/12/2023
            '%m/%d/%Y',          # 12/31/2023
            '%d-%m-%Y',          # 31-12-2023
            '%m-%d-%Y',          # 12-31-2023
            '%Y/%m/%d',          # 2023/12/31
            '%d %b %Y',          # 31 Dec 2023
            '%d %B %Y',          # 31 December 2023
            '%b %d, %Y',         # Dec 31, 2023
            '%B %d, %Y',         # December 31, 2023
            '%d.%m.%Y',          # 31.12.2023
        ]
        
        # Patterns for detecting amount formats
        self.amount_patterns = {
            'decimal': r'^-?\d+\.?\d*$',           # 123.45 or -123.45
            'comma_decimal': r'^-?\d+,\d{2}$',     # 123,45
            'parentheses': r'^\(\d+\.?\d*\)$',     # (123.45) for negative
            'currency_symbol': r'^[$£€¥]?\d+\.?\d*$',  # $123.45
        }
        
        logger.info("CSV processor initialized")
    
    def detect_csv_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Automatically detect CSV format and suggest column mappings.
        
        Args:
            df (pd.DataFrame): Raw CSV data
            
        Returns:
            Dict[str, Any]: Detected format information including:
                - suggested_mappings: Suggested column mappings
                - date_format: Detected date format
                - amount_format: Detected amount format
                - confidence: Confidence score (0-1)
        """
        logger.info("Detecting CSV format...")
        
        suggestions = {
            'suggested_mappings': {},
            'date_format': None,
            'amount_format': None,
            'confidence': 0.0
        }
        
        # Get column names in lowercase for matching
        columns_lower = [col.lower().strip() for col in df.columns]
        
        # Common column name patterns
        date_patterns = [
            'date', 'transaction date', 'posting date', 'value date',
            'datum', 'fecha', 'tarih', 'ημερομηνία'
        ]
        
        amount_patterns = [
            'amount', 'value', 'transaction amount', 'debit', 'credit',
            'betrag', 'importe', 'miktar', 'ποσό'
        ]
        
        description_patterns = [
            'description', 'details', 'transaction details', 'memo',
            'reference', 'particulars', 'beschreibung', 'descripción',
            'açıklama', 'περιγραφή'
        ]
        
        balance_patterns = [
            'balance', 'running balance', 'account balance', 'saldo',
            'υπόλοιπο', 'bakiye'
        ]
        
        # Find best matching columns
        confidence_scores = []
        
        # Date column detection
        date_col = self._find_best_match(columns_lower, date_patterns)
        if date_col:
            suggestions['suggested_mappings']['date'] = df.columns[date_col]
            date_format = self._detect_date_format(df.iloc[:, date_col])
            suggestions['date_format'] = date_format
            confidence_scores.append(0.9 if date_format else 0.3)
        
        # Amount column detection
        amount_col = self._find_best_match(columns_lower, amount_patterns)
        if amount_col:
            suggestions['suggested_mappings']['amount'] = df.columns[amount_col]
            amount_format = self._detect_amount_format(df.iloc[:, amount_col])
            suggestions['amount_format'] = amount_format
            confidence_scores.append(0.8 if amount_format else 0.3)
        
        # Description column detection
        desc_col = self._find_best_match(columns_lower, description_patterns)
        if desc_col:
            suggestions['suggested_mappings']['description'] = df.columns[desc_col]
            confidence_scores.append(0.7)
        
        # Balance column detection (optional)
        balance_col = self._find_best_match(columns_lower, balance_patterns)
        if balance_col:
            suggestions['suggested_mappings']['balance'] = df.columns[balance_col]
            confidence_scores.append(0.5)
        
        # Calculate overall confidence
        suggestions['confidence'] = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        logger.info(f"Format detection completed with confidence: {suggestions['confidence']:.2f}")
        return suggestions
    
    def _find_best_match(self, columns_lower: List[str], patterns: List[str]) -> Optional[int]:
        """
        Find the best matching column for given patterns.
        
        Args:
            columns_lower (List[str]): Column names in lowercase
            patterns (List[str]): Patterns to match against
            
        Returns:
            Optional[int]: Index of best matching column, or None if no match
        """
        best_match = None
        best_score = 0
        
        for i, col in enumerate(columns_lower):
            for pattern in patterns:
                # Exact match gets highest score
                if col == pattern:
                    return i
                
                # Partial match gets lower score
                if pattern in col or col in pattern:
                    score = len(pattern) / max(len(col), len(pattern))
                    if score > best_score:
                        best_score = score
                        best_match = i
        
        return best_match if best_score > 0.5 else None
    
    def _detect_date_format(self, date_series: pd.Series) -> Optional[str]:
        """
        Detect date format from a series of date values.
        
        Args:
            date_series (pd.Series): Series containing date values
            
        Returns:
            Optional[str]: Detected date format string, or None if not detected
        """
        # Take a sample of non-null values
        sample_values = date_series.dropna().astype(str).head(10).tolist()
        
        if not sample_values:
            return None
        
        # Try each date format
        for date_format in self.date_formats:
            success_count = 0
            
            for value in sample_values:
                try:
                    datetime.strptime(value.strip(), date_format)
                    success_count += 1
                except ValueError:
                    continue
            
            # If more than 70% of samples match, consider it detected
            if success_count / len(sample_values) > 0.7:
                logger.info(f"Detected date format: {date_format}")
                return date_format
        
        # Try pandas auto-detection as fallback
        try:
            pd.to_datetime(sample_values)
            logger.info("Date format: pandas auto-detection")
            return 'auto'
        except:
            logger.warning("Could not detect date format")
            return None
    
    def _detect_amount_format(self, amount_series: pd.Series) -> Optional[str]:
        """
        Detect amount format from a series of amount values.
        
        Args:
            amount_series (pd.Series): Series containing amount values
            
        Returns:
            Optional[str]: Detected amount format type
        """
        # Take a sample of non-null values
        sample_values = amount_series.dropna().astype(str).head(10).tolist()
        
        if not sample_values:
            return None
        
        # Test each amount pattern
        for format_type, pattern in self.amount_patterns.items():
            match_count = 0
            
            for value in sample_values:
                value = value.strip()
                if re.match(pattern, value):
                    match_count += 1
            
            # If more than 70% of samples match, consider it detected
            if match_count / len(sample_values) > 0.7:
                logger.info(f"Detected amount format: {format_type}")
                return format_type
        
        logger.warning("Could not detect amount format")
        return 'decimal'  # Default fallback
    
    def process_csv(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Process CSV data with specified column mapping.
        
        Args:
            df (pd.DataFrame): Raw CSV data
            column_mapping (Dict[str, str]): Column mapping configuration
            
        Returns:
            pd.DataFrame: Processed and standardized transaction data
            
        Raises:
            ValueError: If required columns are missing or data is invalid
        """
        logger.info("Processing CSV data...")
        
        # Validate required mappings
        required_fields = ['date', 'amount', 'description']
        missing_fields = [field for field in required_fields if not column_mapping.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required column mappings: {missing_fields}")
        
        # Create processed dataframe
        processed_df = pd.DataFrame()
        
        try:
            # Process date column
            date_col = column_mapping['date']
            processed_df['date'] = self._process_date_column(df[date_col])
            
            # Process amount column
            amount_col = column_mapping['amount']
            processed_df['amount'] = self._process_amount_column(df[amount_col])
            
            # Process description column
            desc_col = column_mapping['description']
            processed_df['description'] = self._process_description_column(df[desc_col])
            
            # Process optional columns
            if column_mapping.get('balance'):
                balance_col = column_mapping['balance']
                processed_df['balance'] = self._process_amount_column(df[balance_col])
            
            if column_mapping.get('reference'):
                ref_col = column_mapping['reference']
                processed_df['reference'] = df[ref_col].astype(str)
            
            # Add metadata
            processed_df['import_date'] = datetime.now()
            processed_df['source_file'] = 'csv_upload'
            
            # Remove rows with invalid data
            initial_count = len(processed_df)
            processed_df = self._clean_data(processed_df)
            final_count = len(processed_df)
            
            if initial_count > final_count:
                logger.warning(f"Removed {initial_count - final_count} invalid rows during processing")
            
            logger.info(f"Successfully processed {final_count} transactions")
            return processed_df
            
        except Exception as e:
            logger.error(f"Error processing CSV data: {e}")
            raise ValueError(f"CSV processing failed: {str(e)}")
    
    def _process_date_column(self, date_series: pd.Series) -> pd.Series:
        """
        Process and standardize date column.
        
        Args:
            date_series (pd.Series): Raw date data
            
        Returns:
            pd.Series: Processed datetime series
        """
        logger.debug("Processing date column...")
        
        # Try pandas auto-detection first
        try:
            return pd.to_datetime(date_series, dayfirst=True, errors='coerce')
        except:
            pass
        
        # Try specific date formats
        for date_format in self.date_formats:
            try:
                return pd.to_datetime(date_series, format=date_format, errors='coerce')
            except:
                continue
        
        # If all else fails, try to parse manually
        logger.warning("Using manual date parsing as fallback")
        return pd.to_datetime(date_series, errors='coerce')
    
    def _process_amount_column(self, amount_series: pd.Series) -> pd.Series:
        """
        Process and standardize amount column.
        
        Args:
            amount_series (pd.Series): Raw amount data
            
        Returns:
            pd.Series: Processed numeric series
        """
        logger.debug("Processing amount column...")
        
        # Convert to string for processing
        amounts = amount_series.astype(str).str.strip()
        
        # Handle different amount formats
        processed_amounts = []
        
        for amount in amounts:
            try:
                # Remove currency symbols
                amount = re.sub(r'[£$€¥,\s]', '', amount)
                
                # Handle parentheses for negative amounts
                if amount.startswith('(') and amount.endswith(')'):
                    amount = '-' + amount[1:-1]
                
                # Handle comma as decimal separator
                if ',' in amount and amount.count(',') == 1 and len(amount.split(',')[1]) <= 2:
                    amount = amount.replace(',', '.')
                
                # Convert to float
                processed_amounts.append(float(amount))
                
            except (ValueError, TypeError):
                processed_amounts.append(np.nan)
        
        return pd.Series(processed_amounts)
    
    def _process_description_column(self, desc_series: pd.Series) -> pd.Series:
        """
        Process and clean description column.
        
        Args:
            desc_series (pd.Series): Raw description data
            
        Returns:
            pd.Series: Processed description series
        """
        logger.debug("Processing description column...")
        
        # Convert to string and clean
        descriptions = desc_series.astype(str).str.strip()
        
        # Remove excessive whitespace
        descriptions = descriptions.str.replace(r'\s+', ' ', regex=True)
        
        # Handle common encoding issues
        descriptions = descriptions.str.replace('Ã¢â‚¬â€', "'", regex=False)
        descriptions = descriptions.str.replace('Ã¢â‚¬Å"', '"', regex=False)
        
        return descriptions
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean processed data by removing invalid rows.
        
        Args:
            df (pd.DataFrame): Processed transaction data
            
        Returns:
            pd.DataFrame: Cleaned transaction data
        """
        logger.debug("Cleaning processed data...")
        
        initial_count = len(df)
        
        # Remove rows with invalid dates
        df = df.dropna(subset=['date'])
        
        # Remove rows with invalid amounts
        df = df.dropna(subset=['amount'])
        
        # Remove rows with empty descriptions
        df = df[df['description'].str.strip() != '']
        df = df[df['description'] != 'nan']
        
        # Remove duplicate transactions (same date, amount, description)
        df = df.drop_duplicates(subset=['date', 'amount', 'description'], keep='first')
        
        # Sort by date
        df = df.sort_values('date')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        final_count = len(df)
        logger.debug(f"Data cleaning: {initial_count} -> {final_count} rows")
        
        return df
    
    def validate_processed_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate processed transaction data and return validation report.
        
        Args:
            df (pd.DataFrame): Processed transaction data
            
        Returns:
            Dict[str, Any]: Validation report with statistics and issues
        """
        logger.info("Validating processed data...")
        
        report = {
            'total_transactions': len(df),
            'date_range': None,
            'amount_range': None,
            'issues': [],
            'warnings': [],
            'is_valid': True
        }
        
        if df.empty:
            report['is_valid'] = False
            report['issues'].append("No valid transactions found")
            return report
        
        # Date validation
        if 'date' in df.columns:
            report['date_range'] = {
                'min': df['date'].min(),
                'max': df['date'].max(),
                'span_days': (df['date'].max() - df['date'].min()).days
            }
            
            # Check for future dates
            future_dates = df['date'] > datetime.now()
            if future_dates.any():
                report['warnings'].append(f"{future_dates.sum()} transactions have future dates")
        
        # Amount validation
        if 'amount' in df.columns:
            report['amount_range'] = {
                'min': df['amount'].min(),
                'max': df['amount'].max(),
                'mean': df['amount'].mean(),
                'zero_amounts': (df['amount'] == 0).sum()
            }
            
            # Check for extremely large amounts (might indicate parsing errors)
            large_amounts = df['amount'].abs() > 10000
            if large_amounts.any():
                report['warnings'].append(f"{large_amounts.sum()} transactions have amounts > $10,000")
        
        # Description validation
        if 'description' in df.columns:
            empty_descriptions = df['description'].str.strip() == ''
            if empty_descriptions.any():
                report['warnings'].append(f"{empty_descriptions.sum()} transactions have empty descriptions")
        
        # Overall validation
        if len(report['issues']) > 0:
            report['is_valid'] = False
        
        logger.info(f"Validation completed: {report['total_transactions']} transactions, "
                   f"{len(report['issues'])} issues, {len(report['warnings'])} warnings")
        
        return report
    
    def get_sample_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Get sample column mappings for common bank formats.
        
        Returns:
            Dict[str, Dict[str, str]]: Sample mappings for different banks
        """
        return {
            'Standard Bank (UK)': {
                'date': 'Transaction Date',
                'amount': 'Amount',
                'description': 'Description',
                'balance': 'Balance',
                'reference': 'Reference'
            },
            'Chase Bank (US)': {
                'date': 'Posting Date',
                'amount': 'Amount',
                'description': 'Description',
                'balance': None,
                'reference': 'Check or Slip #'
            },
            'Deutsche Bank (DE)': {
                'date': 'Buchungstag',
                'amount': 'Betrag',
                'description': 'Verwendungszweck',
                'balance': 'Saldo',
                'reference': 'Referenz'
            },
            'Generic CSV': {
                'date': 'Date',
                'amount': 'Amount',
                'description': 'Description',
                'balance': 'Balance',
                'reference': 'Reference'
            }
        }