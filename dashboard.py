import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional
from config import Config
from shot_analyzer import ShotAnalyzer
from visualizer import Visualizer
from data_manager import DataManager

class Dashboard:
    """Main dashboard class combining session and shot analysis"""

    def __init__(self):
        # Streamlit page configuration MUST be first
        st.set_page_config(layout="wide", page_title="Tennis Analysis Dashboard")

        # Initialize components
        self.config = Config()
        self.data_manager = DataManager(self.config)
        self.visualizer = Visualizer()
        self.shot_analyzer = ShotAnalyzer(self.config)

        # Load session data
        self.sessions_df = self.data_manager.load_sessions(self.config)

        # Initialize view
        self.initialize_view()

    def initialize_view(self):
        """Initialize the dashboard view"""
        st.title("Tennis Analysis Dashboard")

        # Main view selection
        self.view_mode = st.sidebar.radio(
            "Select View",
            ["Session Analysis", "Historical Analysis", "Shot Analysis"],
            key="view_mode_radio"
        )

        # Render selected view
        if self.view_mode == "Session Analysis":
            self.render_session_analysis()
        elif self.view_mode == "Historical Analysis":
            self.render_historical_analysis()
        else:
            self.render_shot_analysis()

    def get_session_selector(self) -> Optional[str]:
        """Get selected session ID"""
        return st.sidebar.selectbox(
            "Select Session",
            self.sessions_df['_id'].unique(),
            format_func=lambda x: f"ID: {x} - {self.sessions_df[self.sessions_df['_id'] == x]['formatted_time'].iloc[0]}",
            key="session_selector"
        )

    def render_session_analysis(self):
        """Render session analysis view"""
        session_id = self.get_session_selector()
        if session_id:
            session = self.sessions_df[self.sessions_df['_id'] == session_id].iloc[0]
            self.display_session_metrics(session)
            self.display_session_analysis(session)

    def render_shot_analysis(self):
        """Render shot analysis view"""
        session_id = self.get_session_selector()
        if session_id:
            session = self.sessions_df[self.sessions_df['_id'] == session_id].iloc[0]
            session_datetime = session['datetime']

            # Display session info
            st.subheader(f"Session: {session['formatted_time']}")
            st.markdown(f"Total Shots: {session['total_shot_count']}")

            # Render shot analysis
            self.shot_analyzer.render_shot_analysis(session_id, session_datetime)

    def display_session_metrics(self, session: pd.Series):
        metrics = [
            ("Best PIQ", session['max_piq_score'], None),
            ("Best Shot Speed", f"{session['max_serve_speed'] * self.config.SPEED_CONVERSION_FACTOR:.1f} mph", None),
            ("Best Rally", session['best_rally'], None),
            ("Activity Score", session['activity_level'], None),
            ("PIQ Score", session['piq_score'], None),
            ("Rate (shots/min)", f"{session['rate']:.1f}", None)
        ]

        cols = st.columns(3)
        for idx, (label, value, delta) in enumerate(metrics):
            cols[idx % 3].metric(label, value, delta)

    def display_session_analysis(self, session: pd.Series):
        # Shot distribution
        shot_counts = {
            'Forehand': session['forehand_count'],
            'Backhand': session['backhand_count'],
            'Serve': session['serves_count'],
            'Volley': session['volley_count'],
            'Smash': session['smash_count']
        }

        st.markdown(f"### Total Shots: {session['total_shot_count']}")
        st.plotly_chart(self.visualizer.create_shot_distribution_chart(shot_counts))

        # Spin analysis
        spin_data = self.data_manager.parse_json(session['activity_statistics_spin_json'])
        if spin_data:
            st.header("Spin Analysis")
            fig_spin, percentages = self.visualizer.create_spin_analysis_chart(spin_data)
            st.plotly_chart(fig_spin)
            st.markdown("### Spin Type Distribution (%)")
            st.dataframe(percentages.round(1))

    def render_historical_analysis(self):
        """Render historical analysis view"""
        self.setup_historical_controls()
        self.display_historical_trends()
        self.display_summary_statistics()

    def setup_historical_controls(self):
        st.sidebar.header("Visualization Options")
        self.viz_options = {
            'show_trendline': st.sidebar.checkbox("Show Trend Lines", value=True),
            'show_rolling_avg': st.sidebar.checkbox("Show Rolling Average", value=True),
            'rolling_window': st.sidebar.slider(
                "Rolling Average Window Size", 
                min_value=2, 
                max_value=20, 
                value=self.config.DEFAULT_ROLLING_WINDOW
            ),
            'show_forehand': st.sidebar.checkbox("Show Forehand", value=False),
            'show_backhand': st.sidebar.checkbox("Show Backhand", value=False)
        }

    def display_historical_trends(self):
        self.display_piq_history()
        self.display_speed_history()
        self.display_activity_history()

    def display_piq_history(self):
        st.subheader("PIQ Score History")
        fig = go.Figure()
        
        # Add main PIQ traces
        fig.add_trace(go.Scatter(
            x=self.sessions_df['datetime'],
            y=self.sessions_df['max_piq_score'],
            name='Best PIQ',
            line=dict(color=self.config.PLOT_COLORS['best_piq'])
        ))
        
        fig.add_trace(go.Scatter(
            x=self.sessions_df['datetime'],
            y=self.sessions_df['piq_score'],
            name='Average PIQ',
            line=dict(color=self.config.PLOT_COLORS['avg_piq'])
        ))
        
        # Add optional traces based on user selection
        if self.viz_options['show_forehand']:
            fig.add_trace(go.Scatter(
                x=self.sessions_df['datetime'],
                y=self.sessions_df['forehand_avg_score'],
                name='Forehand Avg Score',
                line=dict(color=self.config.PLOT_COLORS['forehand'])
            ))
            self.visualizer.add_trend_analysis(
                fig,
                self.sessions_df['datetime'],
                self.sessions_df['forehand_avg_score'],
                'Forehand Avg Score',
                window_size=self.viz_options['rolling_window'],
                show_trendline=self.viz_options['show_trendline'],
                show_rolling_avg=self.viz_options['show_rolling_avg']
            )
        
        if self.viz_options['show_backhand']:
            fig.add_trace(go.Scatter(
                x=self.sessions_df['datetime'],
                y=self.sessions_df['backhand_avg_score'],
                name='Backhand Avg Score',
                line=dict(color=self.config.PLOT_COLORS['backhand'])
            ))
            self.visualizer.add_trend_analysis(
                fig,
                self.sessions_df['datetime'],
                self.sessions_df['backhand_avg_score'],
                'Backhand Avg Score',
                window_size=self.viz_options['rolling_window'],
                show_trendline=self.viz_options['show_trendline'],
                show_rolling_avg=self.viz_options['show_rolling_avg']
            )
        
        # Add trend analysis for main metrics
        for metric_name, y_data in [
            ('Best PIQ', self.sessions_df['max_piq_score']),
            ('Average PIQ', self.sessions_df['piq_score'])
        ]:
            self.visualizer.add_trend_analysis(
                fig,
                self.sessions_df['datetime'],
                y_data,
                metric_name,
                window_size=self.viz_options['rolling_window'],
                show_trendline=self.viz_options['show_trendline'],
                show_rolling_avg=self.viz_options['show_rolling_avg']
            )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="PIQ Score",
            hovermode='x unified'
        )
        st.plotly_chart(fig)

    def display_speed_history(self):
        st.subheader("Best Shot Speed History")
        fig = go.Figure()
        
        # Convert speeds to mph
        speeds_dict = {
            'serve': self.sessions_df['max_serve_speed'] * self.config.SPEED_CONVERSION_FACTOR,
            'forehand': self.sessions_df['max_forehand_speed'] * self.config.SPEED_CONVERSION_FACTOR,
            'backhand': self.sessions_df['max_backhand_speed'] * self.config.SPEED_CONVERSION_FACTOR
        }
        
        # Add serve speed trace
        fig.add_trace(go.Scatter(
            x=self.sessions_df['datetime'],
            y=speeds_dict['serve'],
            name='Best Serve Speed',
            line=dict(color=self.config.PLOT_COLORS['serve'])
        ))
        
        # Add optional traces
        trace_config = [
            ('forehand', self.viz_options['show_forehand']),
            ('backhand', self.viz_options['show_backhand'])
        ]
        
        filtered_dfs = []
        for shot_type, show in trace_config:
            if show:
                fig.add_trace(go.Scatter(
                    x=self.sessions_df['datetime'],
                    y=speeds_dict[shot_type],
                    name=f'Best {shot_type.title()} Speed',
                    line=dict(color=self.config.PLOT_COLORS[shot_type])
                ))
                filtered_df = self.visualizer.add_trend_analysis(
                    fig,
                    self.sessions_df['datetime'],
                    speeds_dict[shot_type],
                    f'Best {shot_type.title()} Speed',
                    window_size=self.viz_options['rolling_window'],
                    remove_zeros=True,
                    y_min=self.config.MIN_SPEED_THRESHOLD,
                    show_trendline=self.viz_options['show_trendline'],
                    show_rolling_avg=self.viz_options['show_rolling_avg']
                )
                if filtered_df is not None:
                    filtered_dfs.append(filtered_df)
        
        # Add trend analysis for serve speed
        filtered_serve_df = self.visualizer.add_trend_analysis(
            fig,
            self.sessions_df['datetime'],
            speeds_dict['serve'],
            'Best Serve Speed',
            window_size=self.viz_options['rolling_window'],
            remove_zeros=True,
            y_min=self.config.MIN_SPEED_THRESHOLD,
            show_trendline=self.viz_options['show_trendline'],
            show_rolling_avg=self.viz_options['show_rolling_avg']
        )
        if filtered_serve_df is not None:
            filtered_dfs.append(filtered_serve_df)
        
        # Update y-axis range if we have valid data
        if filtered_dfs:
            all_speeds = pd.concat([df['y'] for df in filtered_dfs])
            y_min = max(self.config.MIN_SPEED_THRESHOLD, all_speeds.min() * 0.9)
            y_max = all_speeds.max() * 1.1
            fig.update_layout(yaxis=dict(range=[y_min, y_max], autorange=False))
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Speed (mph)",
            hovermode='x unified'
        )
        st.plotly_chart(fig)

    def display_activity_history(self):
        st.subheader("Activity Level History")
        fig = go.Figure()
        
        # Add activity level trace
        fig.add_trace(go.Scatter(
            x=self.sessions_df['datetime'],
            y=self.sessions_df['activity_level'],
            name='Activity Level',
            line=dict(color=self.config.PLOT_COLORS['backhand'])
        ))
        
        # Add trend analysis
        self.visualizer.add_trend_analysis(
            fig,
            self.sessions_df['datetime'],
            self.sessions_df['activity_level'],
            'Activity Level',
            window_size=self.viz_options['rolling_window'],
            show_trendline=self.viz_options['show_trendline'],
            show_rolling_avg=self.viz_options['show_rolling_avg']
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Activity Level",
            hovermode='x unified'
        )
        st.plotly_chart(fig)

    def display_summary_statistics(self):
        st.header("Summary Statistics")
        cols = st.columns(3)
        
        cols[0].metric(
            "PIQ Score",
            f"{self.sessions_df['piq_score'].mean():.1f}",
            f"Best: {self.sessions_df['max_piq_score'].max()}"
        )
        
        max_speeds = {
            'serve': self.sessions_df['max_serve_speed'].max() * self.config.SPEED_CONVERSION_FACTOR,
            'forehand': self.sessions_df['max_forehand_speed'].max() * self.config.SPEED_CONVERSION_FACTOR,
            'backhand': self.sessions_df['max_backhand_speed'].max() * self.config.SPEED_CONVERSION_FACTOR
        }
        
        cols[1].metric(
            "Best Speeds (mph)",
            f"Serve: {max_speeds['serve']:.1f}",
            f"FH: {max_speeds['forehand']:.1f} / BH: {max_speeds['backhand']:.1f}"
        )
        
        cols[2].metric(
            "Activity Level",
            f"{self.sessions_df['activity_level'].mean():.1f}",
            f"Best: {self.sessions_df['activity_level'].max()}"
        )

if __name__ == "__main__":
    dashboard = Dashboard()

