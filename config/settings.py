"""
Configuration Settings for Stock Analysis Project
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    
    # API Keys
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
    
    # Flask Settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Data Settings
    DATA_PATH = os.getenv('DATA_PATH', './data')
    DEFAULT_EXCHANGE = os.getenv('DEFAULT_EXCHANGE', 'US')
    DEFAULT_ANALYSIS_YEARS = int(os.getenv('DEFAULT_ANALYSIS_YEARS', 2))
    
    # Technical Analysis Settings
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BB_PERIOD = 20
    BB_STD = 2
    
    # Trading Settings
    STOP_LOSS_PERCENT = 0.02  # 2%
    TARGET_PROFIT_CONSERVATIVE = 0.08  # 8%
    TARGET_PROFIT_AGGRESSIVE = 0.15   # 15%
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.FINNHUB_API_KEY:
            raise ValueError("FINNHUB_API_KEY is required")
        
        # Create data directories if they don't exist
        os.makedirs(f"{cls.DATA_PATH}/raw", exist_ok=True)
        os.makedirs(f"{cls.DATA_PATH}/processed", exist_ok=True)
        
        return True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    FLASK_ENV = 'production'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
