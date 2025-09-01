"""
Analysis and Reporting Module

This module provides comprehensive financial analysis capabilities including
spending trends, category analysis, budget tracking, and financial insights.

Designed for beginners with clear documentation and actionable insights.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisEngine:
    """
    Provides comprehensive financial analysis and reporting capabilities.
    
    This class offers:
    - Spending trend analysis
    - Category-wise breakdowns
    - Budget tracking and alerts
    - Financial health scoring
    - Comparative analysis
    - Seasonal spending patterns
    """
    
    def __init__(self):
        """Initialize the analysis engine."""
        logger.info("Analysis engine initialized")
    
    def generate_spending_summary(self, transactions_df: pd.DataFrame, 
                                period: str = 'month') -> Dict[str, Any]:
        """
        Generate a comprehensive spending summary for specified period.
        
        Args:
            transactions_df (pd.DataFrame): Transaction data
            period (str): Analysis period ('day', 'week', 'month', 'year')
            
        Returns:
            Dict[str, Any]: Comprehensive spending summary
        """
        logger.info(f"Generating {period}ly spending summary")
        
        if transactions_df.empty:
            return {'error': 'No transaction data available'}
        
        df = transactions_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Separate income and expenses
        income_df = df[df['amount'] > 0]
        expense_df = df[df['amount'] < 0].copy()
        expense_df['amount'] = expense_df['amount'].abs()
        
        summary = {
            'period': period,
            'date_range': {
                'start': df['date'].min(),
                'end': df['date'].max()
            },
            'totals': {
                'income': income_df['amount'].sum(),
                'expenses': expense_df['amount'].sum(),
                'net': income_df['amount'].sum() - expense_df['amount'].sum(),
                'transaction_count': len(df)
            },
            'averages': {},
            'category_breakdown': {},
            'trends': {},
            'insights': []
        }
        
        # Calculate averages based on period
        date_range_days = (df['date'].max() - df['date'].min()).days + 1
        
        if period == 'day':
            period_count = date_range_days
        elif period == 'week':
            period_count = max(1, date_range_days // 7)
        elif period == 'month':
            period_count = max(1, date_range_days // 30)
        elif period == 'year':
            period_count = max(1, date_range_days // 365)
        else:
            period_count = 1
        
        summary['averages'] = {
            'income_per_period': summary['totals']['income'] / period_count,
            'expenses_per_period': summary['totals']['expenses'] / period_count,
            'transactions_per_period': summary['totals']['transaction_count'] / period_count,
            'average_transaction': df['amount'].abs().mean()
        }
        
        # Category breakdown for expenses
        if 'category' in expense_df.columns:
            category_totals = expense_df.groupby('category')['amount'].sum().sort_values(ascending=False)
            category_percentages = (category_totals / category_totals.sum() * 100).round(2)
            
            summary['category_breakdown'] = {
                'totals': category_totals.to_dict(),
                'percentages': category_percentages.to_dict(),
                'top_category': category_totals.index[0] if len(category_totals) > 0 else None
            }
        
        # Generate insights
        summary['insights'] = self._generate_insights(summary, df)
        
        return summary
    
    def analyze_spending_trends(self, transactions_df: pd.DataFrame, 
                              periods: int = 6) -> Dict[str, Any]:
        """
        Analyze spending trends over multiple periods.
        
        Args:
            transactions_df (pd.DataFrame): Transaction data
            periods (int): Number of periods to analyze
            
        Returns:
            Dict[str, Any]: Trend analysis results
        """
        logger.info(f"Analyzing spending trends over {periods} periods")
        
        if transactions_df.empty:
            return {'error': 'No transaction data available'}
        
        df = transactions_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        
        # Get recent months
        latest_months = df['month'].unique()
        latest_months = sorted(latest_months, reverse=True)[:periods]
        
        trend_data = []
        
        for month in latest_months:
            month_data = df[df['month'] == month]
            income = month_data[month_data['amount'] > 0]['amount'].sum()
            expenses = month_data[month_data['amount'] < 0]['amount'].abs().sum()
            
            trend_data.append({
                'period': month,
                'income': income,
                'expenses': expenses,
                'net': income - expenses,
                'transaction_count': len(month_data)
            })
        
        # Calculate trends
        trends = {
            'periods_analyzed': len(trend_data),
            'data': trend_data,
            'trends': {},
            'patterns': []
        }
        
        if len(trend_data) >= 2:
            # Calculate percentage changes
            latest = trend_data[0]
            previous = trend_data[1]
            
            income_change = ((latest['income'] - previous['income']) / max(previous['income'], 1)) * 100
            expense_change = ((latest['expenses'] - previous['expenses']) / max(previous['expenses'], 1)) * 100
            
            trends['trends'] = {
                'income_change_pct': round(income_change, 2),
                'expense_change_pct': round(expense_change, 2),
                'direction': 'improving' if latest['net'] > previous['net'] else 'declining'
            }
            
            # Identify patterns
            if abs(income_change) > 20:
                trends['patterns'].append(f"Significant income change: {income_change:+.1f}%")
            
            if abs(expense_change) > 15:
                trends['patterns'].append(f"Notable expense change: {expense_change:+.1f}%")
        
        return trends
    
    def analyze_category_patterns(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze spending patterns by category.
        
        Args:
            transactions_df (pd.DataFrame): Transaction data with categories
            
        Returns:
            Dict[str, Any]: Category analysis results
        """
        logger.info("Analyzing category spending patterns")
        
        if transactions_df.empty or 'category' not in transactions_df.columns:
            return {'error': 'No categorized transaction data available'}
        
        # Filter expenses only
        expense_df = transactions_df[transactions_df['amount'] < 0].copy()
        expense_df['amount'] = expense_df['amount'].abs()
        expense_df['date'] = pd.to_datetime(expense_df['date'])
        
        analysis = {
            'category_totals': {},
            'category_averages': {},
            'category_trends': {},
            'seasonal_patterns': {},
            'recommendations': []
        }
        
        # Category totals and averages
        category_stats = expense_df.groupby('category')['amount'].agg(['sum', 'mean', 'count']).round(2)
        analysis['category_totals'] = category_stats['sum'].to_dict()
        analysis['category_averages'] = category_stats['mean'].to_dict()
        
        # Monthly trends by category
        expense_df['month'] = expense_df['date'].dt.to_period('M')
        monthly_category = expense_df.groupby(['month', 'category'])['amount'].sum().unstack(fill_value=0)
        
        # Calculate category trends (last 3 months if available)
        if len(monthly_category) >= 3:
            recent_months = monthly_category.tail(3)
            for category in recent_months.columns:
                values = recent_months[category].values
                if len(values) >= 2:
                    trend = 'increasing' if values[-1] > values[0] else 'decreasing'
                    change_pct = ((values[-1] - values[0]) / max(values[0], 1)) * 100
                    analysis['category_trends'][category] = {
                        'trend': trend,
                        'change_pct': round(change_pct, 2)
                    }
        
        # Generate recommendations
        total_expenses = expense_df['amount'].sum()
        for category, amount in analysis['category_totals'].items():
            percentage = (amount / total_expenses) * 100
            
            if percentage > 30:
                analysis['recommendations'].append(
                    f"{category} represents {percentage:.1f}% of spending - consider reviewing"
                )
            elif percentage > 20:
                analysis['recommendations'].append(
                    f"{category} is a major expense category ({percentage:.1f}%)"
                )
        
        return analysis
    
    def detect_anomalies(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect unusual transactions and spending patterns.
        
        Args:
            transactions_df (pd.DataFrame): Transaction data
            
        Returns:
            Dict[str, Any]: Anomaly detection results
        """
        logger.info("Detecting spending anomalies")
        
        if transactions_df.empty:
            return {'error': 'No transaction data available'}
        
        df = transactions_df.copy()
        df['amount_abs'] = df['amount'].abs()
        
        anomalies = {
            'large_transactions': [],
            'unusual_categories': [],
            'spending_spikes': [],
            'summary': {}
        }
        
        # Detect large transactions (>2 standard deviations from mean)
        mean_amount = df['amount_abs'].mean()
        std_amount = df['amount_abs'].std()
        threshold = mean_amount + (2 * std_amount)
        
        large_transactions = df[df['amount_abs'] > threshold]
        if not large_transactions.empty:
            anomalies['large_transactions'] = large_transactions.to_dict('records')
        
        # Detect unusual category spending (if categories available)
        if 'category' in df.columns:
            expense_df = df[df['amount'] < 0].copy()
            expense_df['amount_abs'] = expense_df['amount'].abs()
            
            category_stats = expense_df.groupby('category')['amount_abs'].agg(['mean', 'std'])
            
            for category in category_stats.index:
                cat_data = expense_df[expense_df['category'] == category]
                cat_mean = category_stats.loc[category, 'mean']
                cat_std = category_stats.loc[category, 'std']
                
                if cat_std > 0:  # Avoid division by zero
                    cat_threshold = cat_mean + (2 * cat_std)
                    unusual = cat_data[cat_data['amount_abs'] > cat_threshold]
                    
                    if not unusual.empty:
                        anomalies['unusual_categories'].append({
                            'category': category,
                            'unusual_transactions': len(unusual),
                            'threshold': cat_threshold
                        })
        
        # Summary statistics
        anomalies['summary'] = {
            'total_anomalies': len(anomalies['large_transactions']) + len(anomalies['unusual_categories']),
            'large_transaction_count': len(anomalies['large_transactions']),
            'unusual_category_count': len(anomalies['unusual_categories'])
        }
        
        return anomalies
    
    def calculate_financial_health_score(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate a financial health score based on spending patterns.
        
        Args:
            transactions_df (pd.DataFrame): Transaction data
            
        Returns:
            Dict[str, Any]: Financial health assessment
        """
        logger.info("Calculating financial health score")
        
        if transactions_df.empty:
            return {'error': 'No transaction data available', 'score': 0}
        
        df = transactions_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate recent period (last 3 months)
        recent_date = df['date'].max() - timedelta(days=90)
        recent_df = df[df['date'] >= recent_date]
        
        if recent_df.empty:
            recent_df = df  # Use all data if less than 3 months available
        
        income = recent_df[recent_df['amount'] > 0]['amount'].sum()
        expenses = recent_df[recent_df['amount'] < 0]['amount'].abs().sum()
        
        health_score = {
            'overall_score': 0,
            'components': {},
            'recommendations': [],
            'period_analyzed': 'last_3_months' if len(recent_df) < len(df) else 'all_available'
        }
        
        # Component 1: Income vs Expenses Ratio (40% weight)
        if income > 0:
            expense_ratio = expenses / income
            if expense_ratio <= 0.7:
                income_score = 100
            elif expense_ratio <= 0.85:
                income_score = 80
            elif expense_ratio <= 1.0:
                income_score = 60
            else:
                income_score = 30
        else:
            income_score = 0
            health_score['recommendations'].append("No income detected - consider tracking income sources")
        
        health_score['components']['income_expense_ratio'] = {
            'score': income_score,
            'weight': 40,
            'value': expense_ratio if income > 0 else 0
        }
        
        # Component 2: Spending Consistency (30% weight)
        if 'category' in recent_df.columns:
            # Check for balanced spending across categories
            expense_df = recent_df[recent_df['amount'] < 0]
            if not expense_df.empty:
                category_distribution = expense_df.groupby('category')['amount'].sum().abs()
                category_percentages = category_distribution / category_distribution.sum()
                
                # Good if no single category dominates (>50%)
                max_category_pct = category_percentages.max()
                if max_category_pct <= 0.3:
                    consistency_score = 100
                elif max_category_pct <= 0.5:
                    consistency_score = 80
                elif max_category_pct <= 0.7:
                    consistency_score = 60
                else:
                    consistency_score = 40
            else:
                consistency_score = 50
        else:
            consistency_score = 50
        
        health_score['components']['spending_consistency'] = {
            'score': consistency_score,
            'weight': 30,
            'value': max_category_pct if 'max_category_pct' in locals() else 0
        }
        
        # Component 3: Regular Savings (30% weight)
        net_income = income - expenses
        if income > 0:
            savings_rate = net_income / income
            if savings_rate >= 0.2:
                savings_score = 100
            elif savings_rate >= 0.1:
                savings_score = 80
            elif savings_rate >= 0.05:
                savings_score = 60
            elif savings_rate >= 0:
                savings_score = 40
            else:
                savings_score = 20
        else:
            savings_score = 0
        
        health_score['components']['savings_rate'] = {
            'score': savings_score,
            'weight': 30,
            'value': savings_rate if income > 0 else 0
        }
        
        # Calculate overall score
        total_weighted_score = sum(
            component['score'] * component['weight'] 
            for component in health_score['components'].values()
        )
        total_weight = sum(component['weight'] for component in health_score['components'].values())
        health_score['overall_score'] = round(total_weighted_score / total_weight, 1)
        
        # Generate recommendations based on scores
        if income_score < 70:
            health_score['recommendations'].append("Consider reducing expenses or increasing income")
        
        if consistency_score < 70:
            health_score['recommendations'].append("Review spending distribution across categories")
        
        if savings_score < 60:
            health_score['recommendations'].append("Try to save at least 10% of income each month")
        
        return health_score
    
    def _generate_insights(self, summary: Dict[str, Any], df: pd.DataFrame) -> List[str]:
        """
        Generate actionable insights based on spending analysis.
        
        Args:
            summary (Dict[str, Any]): Spending summary data
            df (pd.DataFrame): Transaction data
            
        Returns:
            List[str]: List of insights and recommendations
        """
        insights = []
        
        # Net income insights
        net_income = summary['totals']['net']
        if net_income > 0:
            insights.append(f"💰 Positive cash flow: ${net_income:,.2f}")
        else:
            insights.append(f"⚠️ Negative cash flow: ${net_income:,.2f}")
        
        # Category insights
        if 'category_breakdown' in summary and summary['category_breakdown'].get('totals'):
            top_category = summary['category_breakdown']['top_category']
            if top_category:
                top_amount = summary['category_breakdown']['totals'][top_category]
                top_pct = summary['category_breakdown']['percentages'][top_category]
                insights.append(f"📊 Top spending category: {top_category} (${top_amount:,.2f}, {top_pct}%)")
        
        # Transaction frequency insights
        avg_transactions = summary['averages']['transactions_per_period']
        if avg_transactions > 10:
            insights.append(f"📱 High transaction frequency: {avg_transactions:.1f} per {summary['period']}")
        
        # Average transaction size
        avg_transaction = summary['averages']['average_transaction']
        if avg_transaction > 100:
            insights.append(f"💳 Average transaction: ${avg_transaction:.2f}")
        
        return insights