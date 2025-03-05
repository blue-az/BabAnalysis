# Tennis Analysis Dashboard

A comprehensive Streamlit dashboard for analyzing tennis sensor data, combining session-level analytics and shot-by-shot analysis.

## Features

### 1. Session Analysis
- Session metrics display (PIQ scores, speeds, activity levels)
- Shot distribution visualization
- Spin analysis with detailed breakdowns
- Shot type distribution charts

### 2. Historical Analysis
- PIQ score progression over time
- Speed development tracking
- Activity level trends
- Customizable visualizations with:
  - Configurable rolling averages
  - Optional trend lines
  - Selective shot type display
- Summary statistics

### 3. Shot Analysis
- Detailed shot-by-shot analysis for each session
- Interactive scatter plots
- Shot distribution histograms
- Shot progression analysis
- Correlation heatmaps
- Customizable filters for shot types and spin types

## Project Structure
```
tennis_dashboard/
├── config.py           # Configuration settings
├── dashboard.py        # Main dashboard implementation
├── data_manager.py     # Data loading and management
├── shot_analyzer.py    # Shot-by-shot analysis
├── visualizer.py       # Visualization utilities
├── wrangle.py         # Data preprocessing
└── main.py            # Application entry point
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tennis_dashboard
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Dependencies
- streamlit
- pandas
- numpy
- plotly
- seaborn
- matplotlib
- pytz

## Configuration

1. Database Settings:
   - Update database paths in `config.py`:
     - `DB_PATH`: Path to session summary database
     - `SHOT_DB_PATH`: Path to shot-by-shot database

2. Timezone Configuration:
   - Default timezone is 'America/Phoenix'
   - Modify in `config.py` if needed

3. Analysis Settings:
   - Speed conversion factor (m/s to mph): 2.25
   - Default rolling window size: 5
   - Minimum speed threshold: 50.0
   - Customizable plot colors

## Usage

1. Start the dashboard:
```bash
streamlit run main.py
```

2. Access the dashboard in your web browser (default: http://localhost:8501)

3. Navigate between views:
   - Session Analysis: View individual session details
   - Historical Analysis: Track progress over time
   - Shot Analysis: Analyze shot-by-shot data for specific sessions

4. Using Historical Analysis:
   - Toggle trend lines and rolling averages
   - Adjust rolling average window size
   - Select specific shot types to display
   - View summary statistics

5. Using Shot Analysis:
   - Select a specific session
   - Filter by shot types and spin types
   - Analyze shot distributions and metrics
   - View shot progression within the session

## Important Notes

1. Timezone Handling:
   - Session data uses timezone-aware timestamps
   - Shot data uses naive timestamps
   - All times are assumed to be in America/Phoenix timezone

2. Data Requirements:
   - Session database should contain summary metrics (PIQ scores, speeds, etc.)
   - Shot database should contain individual shot data
   - Ensure database paths are correctly configured

3. Performance Considerations:
   - Uses Streamlit caching for efficient data loading
   - Large datasets may require additional optimization

## Troubleshooting

1. Database Connection Issues:
   - Verify database paths in config.py
   - Check file permissions
   - Ensure SQLite is properly installed

2. Visualization Issues:
   - Check for missing data in required columns
   - Verify data types match expected formats
   - Confirm timezone settings if time-based issues occur

3. Shot Analysis Issues:
   - Ensure session timestamps align with shot data
   - Check filter combinations for empty result sets

## Future Improvements

Potential enhancements:
- Additional metrics and visualizations
- Export functionality
- Advanced filtering options
- Machine learning integration
- Custom date range selection
- Improved performance optimization
- Additional data validation

## License

[Insert License Information]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
