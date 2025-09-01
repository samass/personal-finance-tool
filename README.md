# Personal Finance Tool 💰

A comprehensive web-based tool that analyzes bank account transactions from CSV files, categorizes spending, and provides summaries and projections. This tool helps you understand your financial patterns and make informed budgeting decisions.

## Features 🚀

### 📊 **Transaction Analysis**
- Upload and process CSV files from different banks
- Automatic transaction categorization using machine learning
- Flexible CSV format detection and mapping
- Data cleaning and validation

### 📈 **Visual Analytics**
- Interactive charts and graphs powered by Plotly
- Spending timeline and trends analysis
- Category breakdown visualizations
- Monthly income vs expense comparisons
- Spending pattern heatmaps

### 🔮 **Financial Projections**
- Regular spending projections (mortgages, utilities, etc.)
- Seasonal spending pattern analysis
- Variable spending trend forecasting
- Multi-year financial planning
- Budget vs actual comparisons

### 🏷️ **Smart Categorization**
- Automatic transaction categorization
- Machine learning that improves with your corrections
- Regular payment detection
- Custom category management

### 📱 **User-Friendly Interface**
- Built with Streamlit for responsive web interface
- Mobile-friendly design
- Beginner-friendly with clear documentation
- Privacy-focused - all data processed locally

## Quick Start 🏃‍♂️

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/samass/personal-finance-tool.git
   cd personal-finance-tool
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   The application will automatically open at `http://localhost:8501`

### First Steps

1. **Try with Sample Data**
   - Click "Load Sample Bank Data" on the home page to explore features
   - Or use the sample CSV files in `data/samples/`

2. **Upload Your Data**
   - Go to the "Upload Data" page
   - Upload your bank CSV file
   - Map columns to match your bank's format
   - Review and process transactions

3. **Explore Insights**
   - View your Dashboard for overview metrics
   - Analyze spending patterns and trends
   - Set up budgets and projections

## Supported CSV Formats 📄

The tool supports flexible CSV formats from various banks:

### Required Columns
- **Date**: Transaction date (various formats supported)
- **Amount**: Transaction amount (positive for income, negative for expenses)
- **Description**: Transaction description or merchant name

### Optional Columns
- **Balance**: Running account balance
- **Reference**: Transaction reference or ID
- **Category**: Pre-categorized transactions

### Supported Date Formats
- `YYYY-MM-DD` (2024-01-15)
- `DD/MM/YYYY` (15/01/2024)
- `MM/DD/YYYY` (01/15/2024)
- `DD-MM-YYYY` (15-01-2024)
- And many more...

## Project Structure 📁

```
personal-finance-tool/
├── app.py                          # Main Streamlit application
├── modules/                        # Core functionality modules
│   ├── storage.py                  # Database management (SQLite)
│   ├── csv_processor.py           # CSV processing and data cleaning
│   ├── categorization.py          # Transaction categorization
│   ├── analysis.py                # Financial analysis and reporting
│   ├── projections.py             # Forecasting and projections
│   └── visualization.py           # Charts and graphs (Plotly)
├── config/                         # Configuration files
│   └── settings.yaml              # Default categories and settings
├── data/                          # Data storage
│   ├── samples/                   # Sample CSV files
│   └── templates/                 # CSV format templates
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## Key Technologies 🛠️

- **Python 3.8+**: Core programming language
- **Streamlit**: Web interface framework
- **Pandas**: Data processing and analysis
- **Plotly**: Interactive visualizations
- **SQLite**: Local data storage
- **NumPy**: Numerical computations
- **Scikit-learn**: Machine learning for categorization

## Privacy & Security 🔒

- **Local Processing**: All data is processed locally on your machine
- **No Cloud Storage**: Transactions are stored in local SQLite database
- **No Data Sharing**: Your financial data never leaves your computer
- **Open Source**: Full transparency of data handling

## Usage Examples 💡

### Uploading Bank Data
1. Export CSV from your bank (usually available in online banking)
2. Upload the file in the "Upload Data" section
3. Map columns to match the expected format
4. Review and import transactions

### Understanding Categories
The tool includes default categories like:
- **Income**: Salary, Freelance, Investment Returns
- **Housing**: Rent, Mortgage, Utilities
- **Transportation**: Gas, Public Transport, Car Maintenance
- **Food & Dining**: Groceries, Restaurants
- **And many more...**

### Creating Projections
1. Ensure you have at least 3 months of transaction history
2. Go to the "Projections" page
3. Review regular payment detection
4. Set budget goals for different categories
5. View projected spending for upcoming months

## Development 🔧

### Setting up Development Environment

1. **Clone and setup**
   ```bash
   git clone https://github.com/samass/personal-finance-tool.git
   cd personal-finance-tool
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run in development mode**
   ```bash
   streamlit run app.py --logger.level=debug
   ```

### Code Structure
- **Modular Design**: Each module handles specific functionality
- **Beginner Friendly**: Well-commented code with clear documentation
- **Extensible**: Easy to add new features and integrations

## Contributing 🤝

We welcome contributions! Please see our contributing guidelines and:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting 🔧

### Common Issues

**Issue**: CSV upload fails
- **Solution**: Check that your CSV has required columns (Date, Amount, Description)
- **Check**: Ensure date format is recognizable
- **Try**: Use the column mapping feature to match your bank's format

**Issue**: Categorization not working
- **Solution**: Review transaction descriptions for common patterns
- **Manual**: Manually categorize some transactions to train the system
- **Update**: Use the learning feature to improve categorization

**Issue**: Charts not displaying
- **Solution**: Ensure you have transaction data uploaded
- **Check**: Verify date ranges include your transactions
- **Refresh**: Try refreshing the page

### Getting Help

1. Check this README for common solutions
2. Review sample data format in `data/samples/`
3. Open an issue on GitHub with details about your problem

## License 📝

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- Built with [Streamlit](https://streamlit.io/) for the web interface
- Visualizations powered by [Plotly](https://plotly.com/)
- Data processing with [Pandas](https://pandas.pydata.org/)
- Machine learning with [Scikit-learn](https://scikit-learn.org/)

---

**Start taking control of your finances today!** 💪

For questions, suggestions, or support, please open an issue on GitHub.
