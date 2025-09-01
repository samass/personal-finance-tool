"""
Personal Finance Tool - Main Application

A web-based tool that analyzes bank account transactions from CSV files,
categorizes spending, and provides summaries and projections.

This is the main entry point for the Streamlit application.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import sys

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import custom modules
try:
    from csv_processor import CSVProcessor
    from categorization import TransactionCategorizer
    from analysis import AnalysisEngine
    from projections import ProjectionEngine
    from visualization import VisualizationEngine
    from storage import DatabaseManager
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Personal Finance Tool",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better mobile responsiveness
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 30px;
    }
    .stButton > button {
        width: 100%;
        margin-top: 10px;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'transactions_df' not in st.session_state:
        st.session_state.transactions_df = None
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    if 'csv_processor' not in st.session_state:
        st.session_state.csv_processor = CSVProcessor()
    if 'categorizer' not in st.session_state:
        st.session_state.categorizer = TransactionCategorizer()
    if 'analysis_engine' not in st.session_state:
        st.session_state.analysis_engine = AnalysisEngine()
    if 'projection_engine' not in st.session_state:
        st.session_state.projection_engine = ProjectionEngine()
    if 'viz_engine' not in st.session_state:
        st.session_state.viz_engine = VisualizationEngine()

def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Main header
    st.markdown('<h1 class="main-header">💰 Personal Finance Tool</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Main navigation options
    page = st.sidebar.selectbox(
        "Choose a page:",
        [
            "🏠 Home",
            "📁 Upload Data", 
            "📊 Dashboard",
            "🏷️ Categorization",
            "📈 Analysis",
            "🔮 Projections",
            "⚙️ Settings"
        ]
    )
    
    # Route to appropriate page
    if page == "🏠 Home":
        show_home_page()
    elif page == "📁 Upload Data":
        show_upload_page()
    elif page == "📊 Dashboard":
        show_dashboard_page()
    elif page == "🏷️ Categorization":
        show_categorization_page()
    elif page == "📈 Analysis":
        show_analysis_page()
    elif page == "🔮 Projections":
        show_projections_page()
    elif page == "⚙️ Settings":
        show_settings_page()

def show_home_page():
    """Display home page with overview and getting started information"""
    
    st.markdown("## Welcome to Your Personal Finance Tool! 🎉")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### What can this tool do for you?
        
        📈 **Analyze Your Spending**: Upload your bank CSV files and get instant insights into your spending patterns
        
        🏷️ **Smart Categorization**: Automatically categorize transactions with machine learning, and teach it your preferences
        
        📊 **Visual Reports**: Beautiful interactive charts showing your financial trends over time
        
        🔮 **Future Projections**: Predict future spending based on your historical patterns
        
        💰 **Budget Tracking**: Monitor your spending against budgets and financial goals
        
        ### Getting Started
        1. **Upload your bank CSV files** using the "Upload Data" page
        2. **Review and categorize** your transactions
        3. **Explore insights** in the Dashboard and Analysis pages
        4. **Plan ahead** with projections and budget planning
        """)
        
        if st.button("🚀 Get Started - Upload Your First File"):
            st.session_state.page = "📁 Upload Data"
            st.rerun()
    
    with col2:
        st.markdown("### Quick Stats")
        
        # Get some basic stats if data exists
        db_manager = st.session_state.db_manager
        
        try:
            total_transactions = db_manager.get_transaction_count()
            total_categories = db_manager.get_category_count()
            date_range = db_manager.get_date_range()
            
            if total_transactions > 0:
                st.metric("Total Transactions", f"{total_transactions:,}")
                st.metric("Categories", total_categories)
                if date_range:
                    st.metric("Date Range", f"{date_range['days']} days")
            else:
                st.info("Upload your first CSV file to see statistics here!")
                
        except Exception as e:
            st.info("Upload your first CSV file to see statistics here!")
    
    # Sample data section
    st.markdown("---")
    st.markdown("### 📋 Try with Sample Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💳 Load Sample Bank Data"):
            load_sample_data("bank")
    
    with col2:
        if st.button("🏦 Load Sample Credit Card Data"):
            load_sample_data("credit_card")
    
    with col3:
        if st.button("📄 View CSV Format Guide"):
            show_csv_format_guide()

def show_upload_page():
    """Display file upload page with CSV processing"""
    
    st.markdown("## 📁 Upload Your Transaction Data")
    
    # File upload section
    st.markdown("### Choose Your CSV File")
    
    uploaded_file = st.file_uploader(
        "Upload your bank statement CSV file",
        type=['csv', 'xlsx'],
        help="Supported formats: CSV, Excel (.xlsx). Your data is processed locally and never shared."
    )
    
    if uploaded_file is not None:
        try:
            # Process the uploaded file
            csv_processor = st.session_state.csv_processor
            
            with st.spinner("Processing your file..."):
                # Read the file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ File loaded successfully! Found {len(df)} rows.")
                
                # Show preview
                st.markdown("### Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Column mapping interface
                st.markdown("### Map Your CSV Columns")
                st.info("Tell us which columns contain your transaction data:")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    date_col = st.selectbox("Date Column", options=df.columns.tolist(), index=0)
                
                with col2:
                    amount_col = st.selectbox("Amount Column", options=df.columns.tolist(), index=1 if len(df.columns) > 1 else 0)
                
                with col3:
                    description_col = st.selectbox("Description Column", options=df.columns.tolist(), index=2 if len(df.columns) > 2 else 0)
                
                # Additional optional columns
                with st.expander("Advanced Column Mapping (Optional)"):
                    col1, col2 = st.columns(2)
                    with col1:
                        balance_col = st.selectbox("Balance Column (Optional)", options=["None"] + df.columns.tolist(), index=0)
                        balance_col = None if balance_col == "None" else balance_col
                    
                    with col2:
                        reference_col = st.selectbox("Reference/ID Column (Optional)", options=["None"] + df.columns.tolist(), index=0)
                        reference_col = None if reference_col == "None" else reference_col
                
                # Process and save data
                if st.button("💾 Process and Save Transactions", type="primary"):
                    with st.spinner("Processing transactions..."):
                        try:
                            # Create column mapping
                            column_mapping = {
                                'date': date_col,
                                'amount': amount_col,
                                'description': description_col,
                                'balance': balance_col,
                                'reference': reference_col
                            }
                            
                            # Process the transactions
                            processed_df = csv_processor.process_csv(df, column_mapping)
                            
                            # Store in session state
                            st.session_state.transactions_df = processed_df
                            
                            # Save to database
                            db_manager = st.session_state.db_manager
                            saved_count = db_manager.save_transactions(processed_df)
                            
                            st.success(f"✅ Successfully processed and saved {saved_count} transactions!")
                            st.info("🎉 You can now view your data in the Dashboard or categorize transactions.")
                            
                            # Show processed preview
                            st.markdown("### Processed Data Preview")
                            st.dataframe(processed_df.head(), use_container_width=True)
                            
                        except Exception as e:
                            st.error(f"❌ Error processing transactions: {str(e)}")
                            st.info("Please check your column mappings and try again.")
                
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.info("Please make sure your file is a valid CSV or Excel file.")

def show_dashboard_page():
    """Display main dashboard with overview metrics and charts"""
    
    st.markdown("## 📊 Financial Dashboard")
    
    # Check if we have data
    db_manager = st.session_state.db_manager
    
    try:
        transactions = db_manager.get_all_transactions()
        
        if transactions.empty:
            st.warning("No transaction data found. Please upload a CSV file first.")
            if st.button("📁 Go to Upload Page"):
                st.session_state.page = "📁 Upload Data"
                st.rerun()
            return
        
        # Date range selector
        st.markdown("### 📅 Select Date Range")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            start_date = st.date_input("Start Date", value=transactions['date'].min().date())
        
        with col2:
            end_date = st.date_input("End Date", value=transactions['date'].max().date())
        
        with col3:
            time_period = st.selectbox(
                "Quick Select",
                ["Custom", "Last 30 days", "Last 3 months", "Last 6 months", "Last year", "All time"]
            )
        
        # Apply date filters
        if time_period != "Custom":
            end_date = datetime.now().date()
            if time_period == "Last 30 days":
                start_date = end_date - timedelta(days=30)
            elif time_period == "Last 3 months":
                start_date = end_date - timedelta(days=90)
            elif time_period == "Last 6 months":
                start_date = end_date - timedelta(days=180)
            elif time_period == "Last year":
                start_date = end_date - timedelta(days=365)
            elif time_period == "All time":
                start_date = transactions['date'].min().date()
        
        # Filter transactions
        filtered_transactions = transactions[
            (transactions['date'].dt.date >= start_date) & 
            (transactions['date'].dt.date <= end_date)
        ]
        
        if filtered_transactions.empty:
            st.warning("No transactions found in the selected date range.")
            return
        
        # Key metrics
        st.markdown("### 💰 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_income = filtered_transactions[filtered_transactions['amount'] > 0]['amount'].sum()
        total_expenses = abs(filtered_transactions[filtered_transactions['amount'] < 0]['amount'].sum())
        net_change = total_income - total_expenses
        avg_transaction = filtered_transactions['amount'].mean()
        
        with col1:
            st.metric("Total Income", f"${total_income:,.2f}", delta=None)
        
        with col2:
            st.metric("Total Expenses", f"${total_expenses:,.2f}", delta=None)
        
        with col3:
            delta_color = "normal" if net_change >= 0 else "inverse"
            st.metric("Net Change", f"${net_change:,.2f}", delta=f"${net_change:,.2f}")
        
        with col4:
            st.metric("Avg Transaction", f"${avg_transaction:,.2f}", delta=None)
        
        # Visualization
        viz_engine = st.session_state.viz_engine
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Spending Over Time")
            time_chart = viz_engine.create_spending_timeline(filtered_transactions)
            if time_chart:
                st.plotly_chart(time_chart, use_container_width=True)
        
        with col2:
            st.markdown("### 🥧 Spending by Category")
            category_chart = viz_engine.create_category_breakdown(filtered_transactions)
            if category_chart:
                st.plotly_chart(category_chart, use_container_width=True)
        
        # Recent transactions
        st.markdown("### 📋 Recent Transactions")
        recent_transactions = filtered_transactions.head(20)
        st.dataframe(recent_transactions, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

def show_categorization_page():
    """Display transaction categorization interface"""
    st.markdown("## 🏷️ Transaction Categorization")
    st.info("Coming soon! This page will allow you to review and categorize your transactions.")

def show_analysis_page():
    """Display detailed analysis and reports"""
    st.markdown("## 📈 Financial Analysis")
    st.info("Coming soon! This page will provide detailed spending analysis and trends.")

def show_projections_page():
    """Display spending projections and forecasts"""
    st.markdown("## 🔮 Financial Projections")
    st.info("Coming soon! This page will show spending forecasts and budget projections.")

def show_settings_page():
    """Display settings and configuration options"""
    st.markdown("## ⚙️ Settings")
    st.info("Coming soon! This page will allow you to configure categories, budgets, and other preferences.")

def load_sample_data(data_type):
    """Load sample data for demonstration"""
    st.info(f"Loading sample {data_type} data... (This feature will be implemented soon)")

def show_csv_format_guide():
    """Show guide for CSV format requirements"""
    st.info("CSV Format Guide will be shown here (Coming soon)")

if __name__ == "__main__":
    main()