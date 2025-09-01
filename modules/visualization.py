"""
Visualization Module

This module creates interactive charts and visualizations for the personal
finance tool using Plotly. It provides various chart types for analyzing
spending patterns, trends, and financial data.

Designed for beginners with clear documentation and mobile-responsive charts.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualizationEngine:
    """
    Creates interactive visualizations for financial data analysis.
    
    This class provides:
    - Spending timeline charts
    - Category breakdown charts
    - Income vs expense comparisons
    - Trend analysis visualizations
    - Budget tracking charts
    - Mobile-responsive design
    """
    
    def __init__(self):
        """Initialize visualization engine with default styling."""
        
        # Color palette for charts (colorblind-friendly)
        self.color_palette = [
            '#1f77b4',  # Blue
            '#ff7f0e',  # Orange
            '#2ca02c',  # Green
            '#d62728',  # Red
            '#9467bd',  # Purple
            '#8c564b',  # Brown
            '#e377c2',  # Pink
            '#7f7f7f',  # Gray
            '#bcbd22',  # Olive
            '#17becf'   # Cyan
        ]
        
        # Default chart layout for mobile responsiveness
        self.default_layout = {
            'font': {'size': 12},
            'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50},
            'autosize': True,
            'hovermode': 'closest',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
        }
        
        logger.info("Visualization engine initialized")
    
    def create_spending_timeline(self, transactions_df: pd.DataFrame, 
                               group_by: str = 'month') -> Optional[go.Figure]:
        """
        Create a timeline chart showing spending over time.
        
        Args:
            transactions_df (pd.DataFrame): Transaction data
            group_by (str): Grouping period ('day', 'week', 'month', 'year')
            
        Returns:
            Optional[go.Figure]: Plotly figure or None if error
        """
        logger.debug(f"Creating spending timeline chart grouped by {group_by}")
        
        if transactions_df.empty:
            logger.warning("No data provided for spending timeline")
            return None
        
        try:
            # Ensure date column is datetime
            df = transactions_df.copy()
            df['date'] = pd.to_datetime(df['date'])
            
            # Separate income and expenses
            income_df = df[df['amount'] > 0].copy()
            expense_df = df[df['amount'] < 0].copy()
            expense_df['amount'] = expense_df['amount'].abs()  # Make positive for display
            
            # Group data by specified period
            if group_by == 'day':
                date_col = df['date'].dt.date
                income_df['period'] = income_df['date'].dt.date
                expense_df['period'] = expense_df['date'].dt.date
                title_suffix = "Daily"
            elif group_by == 'week':
                income_df['period'] = income_df['date'].dt.to_period('W').dt.start_time
                expense_df['period'] = expense_df['date'].dt.to_period('W').dt.start_time
                title_suffix = "Weekly"
            elif group_by == 'month':
                income_df['period'] = income_df['date'].dt.to_period('M').dt.start_time
                expense_df['period'] = expense_df['date'].dt.to_period('M').dt.start_time
                title_suffix = "Monthly"
            elif group_by == 'year':
                income_df['period'] = income_df['date'].dt.to_period('Y').dt.start_time
                expense_df['period'] = expense_df['date'].dt.to_period('Y').dt.start_time
                title_suffix = "Yearly"
            else:
                raise ValueError(f"Invalid group_by parameter: {group_by}")
            
            # Aggregate data
            income_summary = income_df.groupby('period')['amount'].sum().reset_index()
            expense_summary = expense_df.groupby('period')['amount'].sum().reset_index()
            
            # Create figure
            fig = go.Figure()
            
            # Add income trace
            if not income_summary.empty:
                fig.add_trace(go.Scatter(
                    x=income_summary['period'],
                    y=income_summary['amount'],
                    mode='lines+markers',
                    name='Income',
                    line=dict(color='#2ca02c', width=3),
                    marker=dict(size=6),
                    hovertemplate='<b>Income</b><br>' +
                                 'Period: %{x}<br>' +
                                 'Amount: $%{y:,.2f}<br>' +
                                 '<extra></extra>'
                ))
            
            # Add expense trace
            if not expense_summary.empty:
                fig.add_trace(go.Scatter(
                    x=expense_summary['period'],
                    y=expense_summary['amount'],
                    mode='lines+markers',
                    name='Expenses',
                    line=dict(color='#d62728', width=3),
                    marker=dict(size=6),
                    hovertemplate='<b>Expenses</b><br>' +
                                 'Period: %{x}<br>' +
                                 'Amount: $%{y:,.2f}<br>' +
                                 '<extra></extra>'
                ))
            
            # Update layout
            fig.update_layout(
                title=f'{title_suffix} Income vs Expenses',
                xaxis_title='Date',
                yaxis_title='Amount ($)',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                **self.default_layout
            )
            
            # Format y-axis as currency
            fig.update_yaxis(tickformat='$,.0f')
            
            logger.debug("Spending timeline chart created successfully")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating spending timeline: {e}")
            return None
    
    def create_category_breakdown(self, transactions_df: pd.DataFrame, 
                                chart_type: str = 'pie') -> Optional[go.Figure]:
        """
        Create a chart showing spending breakdown by category.
        
        Args:
            transactions_df (pd.DataFrame): Transaction data
            chart_type (str): Chart type ('pie', 'bar', 'treemap')
            
        Returns:
            Optional[go.Figure]: Plotly figure or None if error
        """
        logger.debug(f"Creating category breakdown chart ({chart_type})")
        
        if transactions_df.empty:
            logger.warning("No data provided for category breakdown")
            return None
        
        try:
            # Filter expenses only (negative amounts)
            expense_df = transactions_df[transactions_df['amount'] < 0].copy()
            
            if expense_df.empty:
                logger.warning("No expense data found for category breakdown")
                return None
            
            # Make amounts positive for display
            expense_df['amount'] = expense_df['amount'].abs()
            
            # Group by category
            if 'category' not in expense_df.columns:
                expense_df['category'] = 'Uncategorized'
            
            category_summary = expense_df.groupby('category')['amount'].sum().reset_index()
            category_summary = category_summary.sort_values('amount', ascending=False)
            
            # Create appropriate chart type
            if chart_type == 'pie':
                fig = go.Figure(data=[go.Pie(
                    labels=category_summary['category'],
                    values=category_summary['amount'],
                    hole=0.3,  # Donut chart
                    textinfo='label+percent',
                    textposition='outside',
                    hovertemplate='<b>%{label}</b><br>' +
                                 'Amount: $%{value:,.2f}<br>' +
                                 'Percentage: %{percent}<br>' +
                                 '<extra></extra>',
                    marker=dict(colors=self.color_palette)
                )])
                
                fig.update_layout(
                    title='Spending by Category',
                    showlegend=True,
                    legend=dict(orientation="v", x=1.05, y=0.5),
                    **self.default_layout
                )
            
            elif chart_type == 'bar':
                fig = go.Figure(data=[go.Bar(
                    x=category_summary['category'],
                    y=category_summary['amount'],
                    marker_color=self.color_palette[:len(category_summary)],
                    hovertemplate='<b>%{x}</b><br>' +
                                 'Amount: $%{y:,.2f}<br>' +
                                 '<extra></extra>'
                )])
                
                fig.update_layout(
                    title='Spending by Category',
                    xaxis_title='Category',
                    yaxis_title='Amount ($)',
                    xaxis={'tickangle': 45},
                    **self.default_layout
                )
                
                fig.update_yaxis(tickformat='$,.0f')
            
            elif chart_type == 'treemap':
                fig = go.Figure(go.Treemap(
                    labels=category_summary['category'],
                    values=category_summary['amount'],
                    parents=[''] * len(category_summary),
                    textinfo='label+value+percent parent',
                    hovertemplate='<b>%{label}</b><br>' +
                                 'Amount: $%{value:,.2f}<br>' +
                                 'Percentage: %{percentParent}<br>' +
                                 '<extra></extra>',
                    marker=dict(colorscale='Viridis')
                ))
                
                fig.update_layout(
                    title='Spending by Category (Treemap)',
                    **self.default_layout
                )
            
            else:
                raise ValueError(f"Invalid chart_type: {chart_type}")
            
            logger.debug("Category breakdown chart created successfully")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating category breakdown: {e}")
            return None
    
    def create_monthly_comparison(self, transactions_df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create a chart comparing monthly income vs expenses.
        
        Args:
            transactions_df (pd.DataFrame): Transaction data
            
        Returns:
            Optional[go.Figure]: Plotly figure or None if error
        """
        logger.debug("Creating monthly comparison chart")
        
        if transactions_df.empty:
            logger.warning("No data provided for monthly comparison")
            return None
        
        try:
            df = transactions_df.copy()
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.to_period('M')
            
            # Separate income and expenses
            income_df = df[df['amount'] > 0]
            expense_df = df[df['amount'] < 0]
            
            # Group by month
            monthly_income = income_df.groupby('month')['amount'].sum()
            monthly_expenses = expense_df.groupby('month')['amount'].abs().sum()
            
            # Create date range for all months
            if not monthly_income.empty and not monthly_expenses.empty:
                all_months = pd.period_range(
                    start=min(monthly_income.index.min(), monthly_expenses.index.min()),
                    end=max(monthly_income.index.max(), monthly_expenses.index.max()),
                    freq='M'
                )
            elif not monthly_income.empty:
                all_months = pd.period_range(
                    start=monthly_income.index.min(),
                    end=monthly_income.index.max(),
                    freq='M'
                )
            elif not monthly_expenses.empty:
                all_months = pd.period_range(
                    start=monthly_expenses.index.min(),
                    end=monthly_expenses.index.max(),
                    freq='M'
                )
            else:
                return None
            
            # Reindex to include all months (fill missing with 0)
            monthly_income = monthly_income.reindex(all_months, fill_value=0)
            monthly_expenses = monthly_expenses.reindex(all_months, fill_value=0)
            
            # Convert periods to datetime for plotting
            month_dates = [period.start_time for period in all_months]
            
            # Create figure
            fig = go.Figure()
            
            # Add income bars
            fig.add_trace(go.Bar(
                x=month_dates,
                y=monthly_income.values,
                name='Income',
                marker_color='#2ca02c',
                hovertemplate='<b>Income</b><br>' +
                             'Month: %{x|%B %Y}<br>' +
                             'Amount: $%{y:,.2f}<br>' +
                             '<extra></extra>'
            ))
            
            # Add expense bars
            fig.add_trace(go.Bar(
                x=month_dates,
                y=monthly_expenses.values,
                name='Expenses',
                marker_color='#d62728',
                hovertemplate='<b>Expenses</b><br>' +
                             'Month: %{x|%B %Y}<br>' +
                             'Amount: $%{y:,.2f}<br>' +
                             '<extra></extra>'
            ))
            
            # Add net income line
            net_income = monthly_income.values - monthly_expenses.values
            fig.add_trace(go.Scatter(
                x=month_dates,
                y=net_income,
                mode='lines+markers',
                name='Net Income',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=6),
                yaxis='y2',
                hovertemplate='<b>Net Income</b><br>' +
                             'Month: %{x|%B %Y}<br>' +
                             'Amount: $%{y:,.2f}<br>' +
                             '<extra></extra>'
            ))
            
            # Update layout with secondary y-axis
            fig.update_layout(
                title='Monthly Income vs Expenses',
                xaxis_title='Month',
                yaxis_title='Amount ($)',
                yaxis2=dict(
                    title='Net Income ($)',
                    overlaying='y',
                    side='right',
                    tickformat='$,.0f'
                ),
                barmode='group',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                **self.default_layout
            )
            
            # Format y-axis as currency
            fig.update_yaxis(tickformat='$,.0f')
            
            logger.debug("Monthly comparison chart created successfully")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating monthly comparison: {e}")
            return None
    
    def create_spending_heatmap(self, transactions_df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create a heatmap showing spending patterns by day of week and month.
        
        Args:
            transactions_df (pd.DataFrame): Transaction data
            
        Returns:
            Optional[go.Figure]: Plotly figure or None if error
        """
        logger.debug("Creating spending heatmap")
        
        if transactions_df.empty:
            logger.warning("No data provided for spending heatmap")
            return None
        
        try:
            # Filter expenses only
            expense_df = transactions_df[transactions_df['amount'] < 0].copy()
            
            if expense_df.empty:
                logger.warning("No expense data found for heatmap")
                return None
            
            expense_df['amount'] = expense_df['amount'].abs()
            expense_df['date'] = pd.to_datetime(expense_df['date'])
            
            # Extract day of week and month
            expense_df['day_of_week'] = expense_df['date'].dt.day_name()
            expense_df['month'] = expense_df['date'].dt.month_name()
            
            # Create pivot table for heatmap
            heatmap_data = expense_df.groupby(['month', 'day_of_week'])['amount'].sum().unstack(fill_value=0)
            
            # Reorder columns and rows
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            
            # Reindex to ensure proper order
            heatmap_data = heatmap_data.reindex(columns=day_order, fill_value=0)
            heatmap_data = heatmap_data.reindex(month_order, fill_value=0)
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Reds',
                hovertemplate='<b>%{y}, %{x}</b><br>' +
                             'Total Spending: $%{z:,.2f}<br>' +
                             '<extra></extra>',
                colorbar=dict(title="Amount ($)")
            ))
            
            fig.update_layout(
                title='Spending Patterns by Day and Month',
                xaxis_title='Day of Week',
                yaxis_title='Month',
                **self.default_layout
            )
            
            logger.debug("Spending heatmap created successfully")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating spending heatmap: {e}")
            return None
    
    def create_transaction_volume_chart(self, transactions_df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create a chart showing transaction volume over time.
        
        Args:
            transactions_df (pd.DataFrame): Transaction data
            
        Returns:
            Optional[go.Figure]: Plotly figure or None if error
        """
        logger.debug("Creating transaction volume chart")
        
        if transactions_df.empty:
            logger.warning("No data provided for transaction volume chart")
            return None
        
        try:
            df = transactions_df.copy()
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.to_period('M')
            
            # Count transactions per month
            monthly_counts = df.groupby('month').size().reset_index(name='count')
            monthly_counts['month_date'] = monthly_counts['month'].dt.start_time
            
            # Create bar chart
            fig = go.Figure(data=[go.Bar(
                x=monthly_counts['month_date'],
                y=monthly_counts['count'],
                marker_color='#1f77b4',
                hovertemplate='<b>Transaction Volume</b><br>' +
                             'Month: %{x|%B %Y}<br>' +
                             'Count: %{y} transactions<br>' +
                             '<extra></extra>'
            )])
            
            fig.update_layout(
                title='Monthly Transaction Volume',
                xaxis_title='Month',
                yaxis_title='Number of Transactions',
                **self.default_layout
            )
            
            logger.debug("Transaction volume chart created successfully")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating transaction volume chart: {e}")
            return None
    
    def create_balance_timeline(self, transactions_df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create a timeline showing account balance over time.
        
        Args:
            transactions_df (pd.DataFrame): Transaction data with balance column
            
        Returns:
            Optional[go.Figure]: Plotly figure or None if error
        """
        logger.debug("Creating balance timeline")
        
        if transactions_df.empty or 'balance' not in transactions_df.columns:
            logger.warning("No balance data available for timeline")
            return None
        
        try:
            df = transactions_df.copy()
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Remove rows with missing balance data
            df = df.dropna(subset=['balance'])
            
            if df.empty:
                logger.warning("No valid balance data found")
                return None
            
            # Create line chart
            fig = go.Figure(data=[go.Scatter(
                x=df['date'],
                y=df['balance'],
                mode='lines',
                line=dict(color='#2ca02c', width=2),
                fill='tonexty',
                hovertemplate='<b>Account Balance</b><br>' +
                             'Date: %{x}<br>' +
                             'Balance: $%{y:,.2f}<br>' +
                             '<extra></extra>'
            )])
            
            fig.update_layout(
                title='Account Balance Over Time',
                xaxis_title='Date',
                yaxis_title='Balance ($)',
                **self.default_layout
            )
            
            # Format y-axis as currency
            fig.update_yaxis(tickformat='$,.0f')
            
            logger.debug("Balance timeline created successfully")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating balance timeline: {e}")
            return None