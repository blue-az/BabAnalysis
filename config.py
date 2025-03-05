from dataclasses import dataclass
from typing import Dict
from pathlib import Path

@dataclass
class Config:
    """Configuration settings for the combined dashboard"""
    
    # Database paths
    DB_PATH: Path = Path('./playpop_.db')
    SHOT_DB_PATH: Path = Path('./BabPopExt.db')
    
    # Time settings
    TIMEZONE: str = 'America/Phoenix'
    
    # Analysis settings
    SPEED_CONVERSION_FACTOR: float = 2.25  # m/s to mph
    DEFAULT_ROLLING_WINDOW: int = 5
    MIN_SPEED_THRESHOLD: float = 50.0
    
    # Visualization settings
    PLOT_COLORS: Dict[str, str] = None
    
    def __post_init__(self):
        self.PLOT_COLORS = {
            'best_piq': '#2ecc71',
            'avg_piq': '#3498db',
            'forehand': '#e67e22',
            'backhand': '#9b59b6',
            'serve': '#e74c3c'
        }
