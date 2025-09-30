"""
Finnhub Stock API - Main API class for stock analysis
"""

import finnhub
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

@dataclass
class StockRecommendation:
    """Data class for stock recommendations"""
    action: str
    current_price: float
    target_price: float
    stop_loss: float
    confidence: float
    reasoning: str
    risk_level: str

class FinnhubStockAPI:
    """Complete Finnhub Stock API for listing stocks and generating reports"""
    
    def __init__(self, api_key: str):
        """Initialize Finnhub client with API key"""
        self.api_key = api_key
        self.client = finnhub.Client(api_key=api_key)
        
    def list_all_stocks(self, exchange: str = "US", limit: Optional[int] = None) -> pd.DataFrame:
        """API 1: List all available stocks from specified exchange"""
        try:
            print(f"📈 Fetching stock symbols from {exchange} exchange...")
            symbols_data = self.client.stock_symbols(exchange)
            
            if not symbols_data:
                print(f"❌ No data returned for exchange: {exchange}")
                return pd.DataFrame()
            
            stocks_df = pd.DataFrame(symbols_data)
            
            if limit and len(stocks_df) > limit:
                stocks_df = stocks_df.head(limit)
            
            stocks_df['exchange'] = exchange
            stocks_df['listed_date'] = pd.to_datetime('today').strftime('%Y-%m-%d')
            
            if 'description' in stocks_df.columns:
                stocks_df['company_name'] = stocks_df['description']
            if 'symbol' in stocks_df.columns:
                stocks_df['ticker'] = stocks_df['symbol']
            
            print(f"✅ Successfully fetched {len(stocks_df)} stocks from {exchange}")
            return stocks_df
            
        except Exception as e:
            print(f"❌ Error fetching stocks: {str(e)}")
            return pd.DataFrame()
    
    def search_stocks(self, query: str, limit: int = 20) -> pd.DataFrame:
        """Search for stocks by company name or symbol"""
        try:
            print(f"🔍 Searching for stocks matching: {query}")
            search_results = self.client.symbol_lookup(query)
            
            if 'result' not in search_results or not search_results['result']:
                print(f"❌ No stocks found matching: {query}")
                return pd.DataFrame()
            
            results_df = pd.DataFrame(search_results['result'])
            
            if len(results_df) > limit:
                results_df = results_df.head(limit)
            
            print(f"✅ Found {len(results_df)} matching stocks")
            return results_df
            
        except Exception as e:
            print(f"❌ Error searching stocks: {str(e)}")
            return pd.DataFrame()
    
    def get_stock_report(self, symbol: str, period_years: int = 2) -> Dict:
        """API 2: Generate comprehensive stock analysis report"""
        try:
            print(f"📊 Generating comprehensive report for {symbol}...")
            
            report = {
                'symbol': symbol,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'analysis_period_years': period_years
            }
            
            # Get all data components
            report['company_profile'] = self._get_company_profile(symbol)
            report['current_quote'] = self._get_current_quote(symbol)
            report['historical_data'] = self._get_historical_data(symbol, period_years)
            report['technical_analysis'] = self._calculate_technical_indicators(report['historical_data'])
            report['trading_recommendation'] = self._generate_trading_recommendation(report)
            report['risk_assessment'] = self._calculate_risk_metrics(report['historical_data'])
            
            print(f"✅ Successfully generated comprehensive report for {symbol}")
            return report
            
        except Exception as e:
            print(f"❌ Error generating report for {symbol}: {str(e)}")
            return {'error': str(e), 'symbol': symbol}
    
    def _get_company_profile(self, symbol: str) -> Dict:
        """Get company profile information"""
        try:
            profile = self.client.company_profile2(symbol=symbol)
            return profile if profile else {}
        except Exception as e:
            return {}
    
    def _get_current_quote(self, symbol: str) -> Dict:
        """Get current stock quote"""
        try:
            quote = self.client.quote(symbol)
            return quote if quote else {}
        except Exception as e:
            return {}
    
    def _get_historical_data(self, symbol: str, years: int) -> pd.DataFrame:
        """Get historical price data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years * 365)
            
            start_timestamp = int(start_date.timestamp())
            end_timestamp = int(end_date.timestamp())
            
            candles = self.client.stock_candles(symbol, 'D', start_timestamp, end_timestamp)
            
            if candles['s'] != 'ok':
                return pd.DataFrame()
            
            df = pd.DataFrame({
                'timestamp': candles['t'],
                'open': candles['o'],
                'high': candles['h'],
                'low': candles['l'],
                'close': candles['c'],
                'volume': candles['v']
            })
            
            df['date'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('date', inplace=True)
            df.drop('timestamp', axis=1, inplace=True)
            
            return df
            
        except Exception as e:
            return pd.DataFrame()
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators from price data"""
        if df.empty:
            return {}
        
        try:
            indicators = {}
            
            # Moving Averages
            indicators['sma_20'] = df['close'].rolling(20).mean().iloc[-1]
            indicators['sma_50'] = df['close'].rolling(50).mean().iloc[-1]
            indicators['sma_200'] = df['close'].rolling(200).mean().iloc[-1]
            indicators['ema_12'] = df['close'].ewm(span=12).mean().iloc[-1]
            indicators['ema_26'] = df['close'].ewm(span=26).mean().iloc[-1]
            
            # RSI
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            indicators['rsi'] = (100 - (100 / (1 + rs))).iloc[-1]
            
            # MACD
            ema_12 = df['close'].ewm(span=12).mean()
            ema_26 = df['close'].ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            macd_signal = macd_line.ewm(span=9).mean()
            indicators['macd'] = macd_line.iloc[-1]
            indicators['macd_signal'] = macd_signal.iloc[-1]
            indicators['macd_histogram'] = (macd_line - macd_signal).iloc[-1]
            
            # Bollinger Bands
            sma_20 = df['close'].rolling(20).mean()
            std_20 = df['close'].rolling(20).std()
            indicators['bb_upper'] = (sma_20 + (std_20 * 2)).iloc[-1]
            indicators['bb_lower'] = (sma_20 - (std_20 * 2)).iloc[-1]
            indicators['bb_position'] = ((df['close'].iloc[-1] - indicators['bb_lower']) / 
                                       (indicators['bb_upper'] - indicators['bb_lower']))
            
            # Support and Resistance
            recent_data = df.tail(50)
            indicators['support'] = recent_data['low'].min()
            indicators['resistance'] = recent_data['high'].max()
            
            return indicators
            
        except Exception as e:
            return {}
    
    def _generate_trading_recommendation(self, report: Dict) -> StockRecommendation:
        """Generate buy/sell recommendation based on analysis"""
        try:
            current_price = report.get('current_quote', {}).get('c', 0)
            if not current_price:
                return StockRecommendation(
                    action="HOLD", current_price=0, target_price=0, 
                    stop_loss=0, confidence=0, reasoning="Insufficient data",
                    risk_level="UNKNOWN"
                )
            
            technical = report.get('technical_analysis', {})
            
            score = 0
            reasons = []
            
            # Technical Analysis Scoring
            rsi = technical.get('rsi', 50)
            if rsi < 30:
                score += 2
                reasons.append("RSI oversold (bullish)")
            elif rsi > 70:
                score -= 2
                reasons.append("RSI overbought (bearish)")
            
            # Moving Average Analysis
            sma_20 = technical.get('sma_20', current_price)
            sma_50 = technical.get('sma_50', current_price)
            
            if current_price > sma_20 > sma_50:
                score += 1
                reasons.append("Price above key moving averages")
            elif current_price < sma_20 < sma_50:
                score -= 1
                reasons.append("Price below key moving averages")
            
            # MACD Analysis
            macd = technical.get('macd', 0)
            macd_signal = technical.get('macd_signal', 0)
            
            if macd > macd_signal:
                score += 1
                reasons.append("MACD bullish crossover")
            else:
                score -= 1
                reasons.append("MACD bearish trend")
            
            # Bollinger Bands Position
            bb_position = technical.get('bb_position', 0.5)
            if bb_position < 0.2:
                score += 1
                reasons.append("Near lower Bollinger Band (potential bounce)")
            elif bb_position > 0.8:
                score -= 1
                reasons.append("Near upper Bollinger Band (potential pullback)")
            
            # Generate recommendation
            if score >= 3:
                action = "STRONG_BUY"
                confidence = min(0.9, 0.6 + (score * 0.05))
                target_price = current_price * 1.15
                risk_level = "MEDIUM"
            elif score >= 1:
                action = "BUY"
                confidence = min(0.8, 0.6 + (score * 0.05))
                target_price = current_price * 1.08
                risk_level = "MEDIUM"
            elif score <= -3:
                action = "STRONG_SELL"
                confidence = min(0.9, 0.6 + (abs(score) * 0.05))
                target_price = current_price * 0.85
                risk_level = "HIGH"
            elif score <= -1:
                action = "SELL"
                confidence = min(0.8, 0.6 + (abs(score) * 0.05))
                target_price = current_price * 0.92
                risk_level = "MEDIUM_HIGH"
            else:
                action = "HOLD"
                confidence = 0.5
                target_price = current_price
                risk_level = "MEDIUM"
            
            # Calculate stop loss
            if action in ["BUY", "STRONG_BUY"]:
                stop_loss = current_price * 0.98
            else:
                stop_loss = current_price * 1.02
            
            reasoning = "; ".join(reasons) if reasons else "Mixed signals"
            
            return StockRecommendation(
                action=action,
                current_price=current_price,
                target_price=round(target_price, 2),
                stop_loss=round(stop_loss, 2),
                confidence=round(confidence, 2),
                reasoning=reasoning,
                risk_level=risk_level
            )
            
        except Exception as e:
            return StockRecommendation(
                action="HOLD", current_price=0, target_price=0,
                stop_loss=0, confidence=0, reasoning="Error in analysis",
                risk_level="UNKNOWN"
            )
    
    def _calculate_risk_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate risk assessment metrics"""
        if df.empty:
            return {}
        
        try:
            returns = df['close'].pct_change().dropna()
            
            volatility = returns.std() * np.sqrt(252)
            var_95 = returns.quantile(0.05)
            max_drawdown = ((df['close'] / df['close'].cummax()) - 1).min()
            
            excess_returns = returns.mean() * 252 - 0.02
            sharpe_ratio = excess_returns / volatility if volatility != 0 else 0
            
            beta = returns.cov(returns) / returns.var() if returns.var() != 0 else 1
            
            return {
                'volatility': round(volatility, 4),
                'var_95': round(var_95, 4),
                'max_drawdown': round(max_drawdown, 4),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'beta': round(beta, 2),
                'risk_level': 'HIGH' if volatility > 0.3 else 'MEDIUM' if volatility > 0.2 else 'LOW'
            }
            
        except Exception as e:
            return {}
