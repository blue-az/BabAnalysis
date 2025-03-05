from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import wrangle
from datetime import datetime, timedelta
import pytz

class ShotAnalyzer:
    """Handles shot-by-shot analysis for a specific session"""
    
    def __init__(self, config):
        self.config = config
        
    @staticmethod
    @st.cache_resource
    def _setup_cache():
        """Initialize any cached resources"""
        pass
    
    @staticmethod
    @st.cache_data
    def load_shot_data(_config, session_id: str, session_datetime: datetime) -> pd.DataFrame:
        """Load shot data for a specific session"""
        df = wrangle.wrangle(_config.SHOT_DB_PATH)
        
        # Convert string time back to datetime and make timezone-naive
        df['time'] = pd.to_datetime(df['time'])
        
        # Convert session_datetime to naive datetime by removing timezone info
        naive_session_datetime = session_datetime.replace(tzinfo=None)
        
        # Add stroke categorization
        def categorize_stroke(row):
            stroke_lower = str(row).lower()
            if 'serve' in stroke_lower:
                return 'Serve'
            elif 'forehand' in stroke_lower:
                return 'Forehand'
            elif 'backhand' in stroke_lower:
                return 'Backhand'
            else:
                return 'Other'
        
        df['stroke_category'] = df['type'].apply(categorize_stroke)
        
        # Filter for the specific session (within a 2-hour window of the session start time)
        session_start = naive_session_datetime - pd.Timedelta(hours=1)
        session_end = naive_session_datetime + pd.Timedelta(hours=1)
        
        # Apply the filter
        df = df[
            (df['time'] >= session_start) &
            (df['time'] <= session_end)
        ]
        
        return df

    def render_shot_analysis(self, session_id: str, session_datetime: datetime):
        """Main entry point for shot analysis visualization"""
        # Load data for this session
        df = self.load_shot_data(self.config, session_id, session_datetime)
        
        if df.empty:
            st.warning("No shot data found for this session.")
            return
            
        # Setup filters in sidebar
        self._setup_filters(df)
        
        # Apply filters
        filtered_df = self._apply_filters(df)
        
        if filtered_df.empty:
            st.warning("No shots match the selected filters.")
            return
            
        # Render visualizations
        self._render_scatter_plot(filtered_df)
        self._render_histogram(filtered_df)
        self._render_line_plot(filtered_df)
        self._render_correlation_heatmap(filtered_df)
        self._render_summary_stats(filtered_df)

    def _setup_filters(self, df: pd.DataFrame):
        """Setup sidebar filters"""
        st.sidebar.header("Shot Analysis Controls")
        
        # Type selection
        self.selected_types = st.sidebar.multiselect(
            "Select Types",
            df['type'].unique(),
            default=df['type'].unique()
        )
        
        # Stroke category selection
        self.stroke_categories = st.sidebar.multiselect(
            "Select Stroke Categories",
            ['Serve', 'Forehand', 'Backhand', 'Other'],
            default=['Serve', 'Forehand', 'Backhand', 'Other']
        )
        
        # Spin selection
        self.selected_spins = st.sidebar.multiselect(
            "Select Spins",
            df['spin'].unique(),
            default=df['spin'].unique()
        )

    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply selected filters to the dataframe"""
        return df[
            (df['type'].isin(self.selected_types)) &
            (df['spin'].isin(self.selected_spins)) &
            (df['stroke_category'].isin(self.stroke_categories))
        ]

    def _render_scatter_plot(self, df: pd.DataFrame):
        """Render scatter plot visualization"""
        st.header("Shot Distribution")
        
        # Available metrics for axes
        metrics = ['PIQ', 'StyleScore', 'StyleValue', 'EffectScore', 
                  'EffectValue', 'SpeedScore', 'SpeedValue']
        
        # Axis selection
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("X-axis metric", metrics, index=0)
        with col2:
            y_axis = st.selectbox("Y-axis metric", metrics, index=1)
        
        # Jitter controls
        col3, col4 = st.columns(2)
        with col3:
            add_jitter = st.checkbox("Add Jitter", value=False)
        with col4:
            jitter_amount = st.slider(
                "Jitter Amount",
                0.0, 1.0, 0.5,
                disabled=not add_jitter
            )
        
        # Apply jitter if selected
        plot_df = df.copy()
        if add_jitter:
            for axis in [x_axis, y_axis]:
                if not isinstance(plot_df[axis], pd.Timestamp):
                    std = plot_df[axis].std() * jitter_amount * 0.1
                    plot_df[axis] += np.random.normal(0, std, len(plot_df))
        
        # Create scatter plot
        fig = px.scatter(
            plot_df,
            x=x_axis,
            y=y_axis,
            color="stroke_category",
            title=f"{x_axis} vs {y_axis}"
        )
        st.plotly_chart(fig)

    def _render_histogram(self, df: pd.DataFrame):
        """Render histogram visualization"""
        st.header("Shot Distribution Histogram")
        
        metrics = ['PIQ', 'StyleScore', 'StyleValue', 'EffectScore', 
                  'EffectValue', 'SpeedScore', 'SpeedValue']
        
        col1, col2 = st.columns(2)
        with col1:
            metric = st.selectbox("Select metric", metrics, index=0)
        with col2:
            num_bins = st.slider("Number of bins", 5, 100, 20)
        
        fig = px.histogram(
            df,
            x=metric,
            nbins=num_bins,
            color="stroke_category",
            title=f"Distribution of {metric}"
        )
        st.plotly_chart(fig)

    def _render_line_plot(self, df: pd.DataFrame):
        """Render line plot visualization"""
        st.header("Shot Progression")
        
        metrics = ['PIQ', 'StyleScore', 'StyleValue', 'EffectScore', 
                  'EffectValue', 'SpeedScore', 'SpeedValue']
        
        col1, col2 = st.columns(2)
        with col1:
            metric = st.selectbox(
                "Select metric for progression",
                metrics,
                index=0,
                key='line_metric'
            )
        with col2:
            add_average = st.checkbox("Show Moving Average")
        
        fig = go.Figure()
        
        # Add individual shots
        for category in df['stroke_category'].unique():
            category_data = df[df['stroke_category'] == category]
            fig.add_trace(go.Scatter(
                x=category_data['time'],
                y=category_data[metric],
                mode='markers',
                name=category,
                opacity=0.7
            ))
        
        # Add moving average if selected
        if add_average:
            window_size = st.slider("Moving Average Window", 5, 50, 20)
            df_sorted = df.sort_values('time')
            fig.add_trace(go.Scatter(
                x=df_sorted['time'],
                y=df_sorted[metric].rolling(window=window_size).mean(),
                mode='lines',
                name=f'{window_size}-shot Moving Average',
                line=dict(color='black', width=2)
            ))
        
        fig.update_layout(
            title=f"{metric} Progression",
            xaxis_title="Time",
            yaxis_title=metric
        )
        st.plotly_chart(fig)

    def _render_correlation_heatmap(self, df: pd.DataFrame):
        """Render correlation heatmap"""
        st.header("Metric Correlations")
        
        # Select only numeric columns
        numeric_df = df.select_dtypes(include=['number'])
        
        # Calculate correlation matrix
        corr = numeric_df.corr()
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            corr,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            ax=ax
        )
        st.pyplot(fig)

    def _render_summary_stats(self, df: pd.DataFrame):
        """Render summary statistics"""
        st.header("Summary Statistics")
        
        # Calculate summary statistics
        summary = df.describe()
        
        # Display in a more readable format
        st.dataframe(summary.style.format("{:.2f}"))

