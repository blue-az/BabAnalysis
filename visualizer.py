from typing import Dict, List, Tuple, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure
import numpy as np

class Visualizer:
    @staticmethod
    def create_shot_distribution_chart(shot_counts: Dict[str, int]) -> Figure:
        return px.pie(
            values=list(shot_counts.values()),
            names=list(shot_counts.keys()),
            title="Shot Distribution"
        )

    @staticmethod
    def create_spin_analysis_chart(spin_data: List[Dict]) -> Tuple[Figure, pd.DataFrame]:
        if not spin_data:
            return None, None
            
        spin_df = pd.DataFrame(spin_data)
        fig = px.bar(
            spin_df,
            x='motionType',
            y='count',
            color='spinType',
            barmode='group',
            title='Shot Distribution by Spin Type',
            labels={'motionType': 'Shot Type', 'count': 'Count', 'spinType': 'Spin Type'}
        )
        
        # Calculate percentages
        pivot = pd.pivot_table(
            spin_df,
            values='count',
            index='motionType',
            columns='spinType',
            aggfunc='sum'
        ).fillna(0)
        percentages = pivot.div(pivot.sum(axis=1), axis=0) * 100
        
        return fig, percentages

    @staticmethod
    def add_trend_analysis(
        fig: Figure,
        x: pd.Series,
        y: pd.Series,
        name: str,
        window_size: int = 5,
        remove_zeros: bool = False,
        y_min: Optional[float] = None,
        show_trendline: bool = True,
        show_rolling_avg: bool = True
    ) -> Optional[pd.DataFrame]:
        df = pd.DataFrame({'x': x, 'y': y})
        if remove_zeros:
            df = df[df['y'] > 0]
        if y_min is not None:
            df = df[df['y'] >= y_min]
        
        if df.empty:
            return None
            
        if show_rolling_avg:
            rolling_avg = df['y'].rolling(window=window_size, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=df['x'],
                y=rolling_avg,
                name=f'{name} ({window_size}-session Rolling Avg)',
                line=dict(color='rgba(0,0,0,0.5)', width=2),
                opacity=0.7
            ))
        
        if show_trendline:
            x_numeric = pd.to_numeric(pd.to_datetime(df['x']))
            z = np.polyfit(x_numeric, df['y'], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=df['x'],
                y=p(x_numeric),
                name=f'{name} Trend',
                line=dict(dash='dash'),
                opacity=0.5
            ))
        
        return df
