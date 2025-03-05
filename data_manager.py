import sqlite3
import json
import pandas as pd
import streamlit as st
from typing import Dict
from config import Config

class DataManager:
    def __init__(self, config: Config):
        self.config = config

    @staticmethod
    @st.cache_resource
    def get_connection(_config: Config) -> sqlite3.Connection:
        return sqlite3.connect(str(_config.DB_PATH))

    @staticmethod
    @st.cache_data
    def load_sessions(_config: Config) -> pd.DataFrame:
        conn = DataManager.get_connection(_config)
        df = pd.read_sql_query("SELECT * FROM tb_activities", conn)
        df['datetime'] = pd.to_datetime(df['start_time'].astype(float)/1000, unit='s')
        df['datetime'] = df['datetime'].dt.tz_localize('UTC').dt.tz_convert(_config.TIMEZONE)
        df['formatted_time'] = df['datetime'].dt.strftime('%m-%d-%Y %I:%M:%S %p')
        return df.sort_values('datetime', ascending=False)

    @staticmethod
    def parse_json(json_str: str) -> Dict:
        try:
            return json.loads(json_str) if pd.notna(json_str) and json_str else {}
        except json.JSONDecodeError as e:
            st.error(f"JSON parsing error: {e}")
            return {}
