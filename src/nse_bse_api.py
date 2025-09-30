"""
NSE and BSE Stock API - Complete Indian Stock Analysis System
Using Yahoo Finance for reliable NSE/BSE data
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
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

class NSEBSEStockAPI:
    """
    Dedicated NSE and BSE Stock Analysis API
    Using Yahoo Finance for reliable Indian stock data
    """
    
    def __init__(self):
        """Initialize NSE/BSE API"""
        print("🇮🇳 Initializing NSE/BSE Stock Analysis API...")
        
        # Popular NSE stocks (top 100+)
        self.nse_stocks = [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS", "LT.NS",
            "SBIN.NS", "ASIANPAINT.NS", "MARUTI.NS", "BAJFINANCE.NS", "HCLTECH.NS",
            "WIPRO.NS", "ULTRACEMCO.NS", "TITAN.NS", "NESTLEIND.NS", "POWERGRID.NS",
            "NTPC.NS", "ONGC.NS", "TECHM.NS", "TATASTEEL.NS", "AXISBANK.NS",
            "SUNPHARMA.NS", "BAJAJFINSV.NS", "DRREDDY.NS", "JSWSTEEL.NS", "GRASIM.NS",
            "M&M.NS", "INDUSINDBK.NS", "CIPLA.NS", "EICHERMOT.NS", "COALINDIA.NS",
            "HEROMOTOCO.NS", "BPCL.NS", "BRITANNIA.NS", "DIVISLAB.NS", "ADANIPORTS.NS",
            "TATACONSUM.NS", "HINDALCO.NS", "SHREECEM.NS", "IOC.NS", "BAJAJ-AUTO.NS",
            "TATAMOTORS.NS", "HDFCLIFE.NS", "SBILIFE.NS", "APOLLOHOSP.NS", "PIDILITIND.NS",
            "ADANIENT.NS", "GODREJCP.NS", "VEDL.NS", "DABUR.NS", "MARICO.NS",
            "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "UNIONBANK.NS", "INDIANB.NS",
            "IDEA.NS", "SAIL.NS", "NMDC.NS", "GAIL.NS", "PETRONET.NS",
            "UBL.NS", "PAGEIND.NS", "COLPAL.NS", "MCDOWELL-N.NS", "BERGEPAINT.NS",
            "HAVELLS.NS", "BAJAJHLDNG.NS", "TORNTPHARM.NS", "LUPIN.NS", "CADILAHC.NS",
            "RBLBANK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "BANDHANBNK.NS", "PFC.NS",
            "RECLTD.NS", "LICHSGFIN.NS", "MUTHOOTFIN.NS", "CHOLAFIN.NS", "L&TFH.NS",
            "NAUKRI.NS", "ZOMATO.NS", "PAYTM.NS", "DMART.NS", "MOTHERSUMI.NS",
            "BOSCHLTD.NS", "ESCORTS.NS", "BATAINDIA.NS", "RELAXO.NS", "DIXON.NS",
            "CROMPTON.NS", "WHIRLPOOL.NS", "VOLTAS.NS", "DEEPAKNTR.NS", "SRF.NS"
        ]
        
        # Popular BSE stocks  
        self.bse_stocks = [
            "RELIANCE.BO", "TCS.BO", "INFY.BO", "HDFCBANK.BO", "ICICIBANK.BO",
            "HINDUNILVR.BO", "BHARTIARTL.BO", "ITC.BO", "KOTAKBANK.BO", "LT.BO",
            "SBIN.BO", "ASIANPAINT.BO", "MARUTI.BO", "BAJFINANCE.BO", "HCLTECH.BO",
            "WIPRO.BO", "ULTRACEMCO.BO", "TITAN.BO", "NESTLEIND.BO", "POWERGRID.BO",
            "NTPC.BO", "ONGC.BO", "TECHM.BO", "TATASTEEL.BO", "AXISBANK.BO",
            "SUNPHARMA.BO", "BAJAJFINSV.BO", "DRREDDY.BO", "JSWSTEEL.BO", "GRASIM.BO",
            "M&M.BO", "INDUSINDBK.BO", "CIPLA.BO", "EICHERMOT.BO", "COALINDIA.BO",
            "HEROMOTOCO.BO", "BPCL.BO", "BRITANNIA.BO", "DIVISLAB.BO", "ADANIPORTS.BO",
            "TATACONSUM.BO", "HINDALCO.BO", "SHREECEM.BO", "IOC.BO", "BAJAJ-AUTO.BO"
        ]
        
        # Sector mapping
        self.sectors = {
            "Banking": ["HDFCBANK", "ICICIBANK", "KOTAKBANK", "SBIN", "AXISBANK", "INDUSINDBK"],
            "IT": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM", "COFORGE", "LTTS", "MPHASIS"],
            "Oil & Gas": ["RELIANCE", "ONGC", "IOC", "BPCL", "GAIL", "PETRONET"],
            "FMCG": ["HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR", "MARICO"],
            "Auto": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO"],
            "Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "LUPIN", "TORNTPHARM"],
            "Metals": ["TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "SAIL", "NMDC"]
        }
        
        print("✅ NSE/BSE API initialized with 100+ Indian stocks")
    
    def list_all_stocks(self, exchange: str = "NSE", limit: Optional[int] = None) -> pd.DataFrame:
        """
        List all NSE or BSE stocks
        
        Args:
            exchange: "NSE" or "BSE" 
            limit: Max number of stocks to return
        """
        try:
            print(f"📈 Fetching {exchange} stocks...")
            
            if exchange.upper() == "NSE":
                stocks = self.nse_stocks
            elif exchange.upper() == "BSE":
                stocks = self.bse_stocks
            else:
                print(f"❌ Unsupported exchange: {exchange}. Use NSE or BSE")
                return pd.DataFrame()
            
            if limit and len(stocks) > limit:
                stocks = stocks[:limit]
            
            # Create DataFrame with stock info
            stock_data = []
            for symbol in stocks:
                base_symbol = symbol.split('.')[0]
                
                # Determine sector
                sector = "Others"
                for sec, companies in self.sectors.items():
                    if base_symbol in companies:
                        sector = sec
                        break
                
                stock_data.append({
                    'symbol': symbol,
                    'ticker': symbol,
                    'company_name': self._get_company_name(base_symbol),
                    'exchange': exchange,
                    'sector': sector,
                    'currency': 'INR',
                    'country': 'India',
                    'type': 'Common Stock',
                    'listed_date': datetime.now().strftime('%Y-%m-%d')
                })
            
            stocks_df = pd.DataFrame(stock_data)
            print(f"✅ Successfully loaded {len(stocks_df)} {exchange} stocks")
            
            return stocks_df
            
        except Exception as e:
            print(f"❌ Error loading {exchange} stocks: {str(e)}")
            return pd.DataFrame()
    
    def search_stocks(self, query: str, exchange: str = "NSE", limit: int = 20) -> pd.DataFrame:
        """
        Search NSE/BSE stocks by company name
        
        Args:
            query: Search term (company name)
            exchange: NSE or BSE
            limit: Max results
        """
        try:
            print(f"🔍 Searching {exchange} stocks for: {query}")
            
            # Get all stocks for the exchange
            all_stocks = self.list_all_stocks(exchange, limit=None)
            
            if all_stocks.empty:
                return pd.DataFrame()
            
            # Search in company names and symbols
            query_lower = query.lower()
            matches = all_stocks[
                all_stocks['company_name'].str.lower().str.contains(query_lower, na=False) |
                all_stocks['symbol'].str.lower().str.contains(query_lower, na=False)
            ]
            
            if len(matches) > limit:
                matches = matches.head(limit)
            
            print(f"✅ Found {len(matches)} matching stocks")
            return matches
            
        except Exception as e:
            print(f"❌ Error searching stocks: {str(e)}")
            return pd.DataFrame()
    
    def get_stock_report(self, symbol: str, period_years: int = 2) -> Dict:
        """
        Generate comprehensive stock analysis report for NSE/BSE stocks
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS', 'TCS.BO')
            period_years: Years of historical data
        """
        try:
            print(f"�� Generating comprehensive report for {symbol}...")
            
            # Ensure symbol has proper suffix
            if not symbol.endswith(('.NS', '.BO')):
                print(f"⚠️ Adding .NS suffix to {symbol}")
                symbol = f"{symbol}.NS"
            
            report = {
                'symbol': symbol,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'analysis_period_years': period_years,
                'exchange': 'NSE' if symbol.endswith('.NS') else 'BSE',
                'currency': 'INR'
            }
            
            # Get all data components using Yahoo Finance
            ticker = yf.Ticker(symbol)
            
            report['company_info'] = self._get_company_info(ticker, symbol)
            report['current_quote'] = self._get_current_quote(ticker)
            report['historical_data'] = self._get_historical_data(ticker, period_years)
            report['technical_analysis'] = self._calculate_technical_indicators(report['historical_data'])
            report['trading_recommendation'] = self._generate_trading_recommendation(report)
            report['risk_assessment'] = self._calculate_risk_metrics(report['historical_data'])
            
            print(f"✅ Successfully generated report for {symbol}")
            return report
            
        except Exception as e:
            print(f"❌ Error generating report for {symbol}: {str(e)}")
            return {'error': str(e), 'symbol': symbol}
    
    def _get_company_name(self, base_symbol: str) -> str:
        """Get company name from base symbol"""
        company_names = {
            'RELIANCE': 'Reliance Industries Limited',
            'TCS': 'Tata Consultancy Services Limited',
            'INFY': 'Infosys Limited',
            'HDFCBANK': 'HDFC Bank Limited',
            'ICICIBANK': 'ICICI Bank Limited',
            'HINDUNILVR': 'Hindustan Unilever Limited',
            'BHARTIARTL': 'Bharti Airtel Limited',
            'ITC': 'ITC Limited',
            'KOTAKBANK': 'Kotak Mahindra Bank Limited',
            'LT': 'Larsen & Toubro Limited',
            'SBIN': 'State Bank of India',
            'ASIANPAINT': 'Asian Paints Limited',
            'MARUTI': 'Maruti Suzuki India Limited',
            'BAJFINANCE': 'Bajaj Finance Limited',
            'HCLTECH': 'HCL Technologies Limited',
            'WIPRO': 'Wipro Limited',
            'ULTRACEMCO': 'UltraTech Cement Limited',
            'TITAN': 'Titan Company Limited',
            'NESTLEIND': 'Nestle India Limited',
            'POWERGRID': 'Power Grid Corporation of India Limited'
        }
        
        return company_names.get(base_symbol, f"{base_symbol} Limited")
    
    def _get_company_info(self, ticker, symbol: str) -> Dict:
        """Get company information"""
        try:
            info = ticker.info
            return {
                'name': info.get('longName', symbol.split('.')[0]),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'employees': info.get('fullTimeEmployees', 0),
                'website': info.get('website', ''),
                'business_summary': info.get('businessSummary', '')[:500] + '...' if info.get('businessSummary') else ''
            }
        except:
            return {'name': symbol.split('.')[0], 'sector': 'Unknown'}
    
    def _get_current_quote(self, ticker) -> Dict:
        """Get current stock quote"""
        try:
            hist = ticker.history(period="2d")
            if hist.empty:
                return {}
            
            current = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else current
            
            return {
                'c': round(current['Close'], 2),
                'o': round(current['Open'], 2),
                'h': round(current['High'], 2),
                'l': round(current['Low'], 2),
                'pc': round(previous['Close'], 2),
                'd': round(current['Close'] - previous['Close'], 2),
                'dp': round(((current['Close'] - previous['Close']) / previous['Close']) * 100, 2),
                'v': int(current['Volume'])
            }
        except:
            return {}
    
    def _get_historical_data(self, ticker, years: int) -> pd.DataFrame:
        """Get historical price data"""
        try:
            period = f"{years}y"
            hist = ticker.history(period=period)
            
            if hist.empty:
                return pd.DataFrame()
            
            # Rename columns to match expected format
            hist = hist.rename(columns={
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            return hist[['open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            print(f"⚠️ Error fetching historical data: {e}")
            return pd.DataFrame()
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators from price data"""
        if df.empty:
            return {}
        
        try:
            indicators = {}
            
            # Moving Averages
            indicators['sma_20'] = df['close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else None
            indicators['sma_50'] = df['close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else None
            indicators['sma_200'] = df['close'].rolling(200).mean().iloc[-1] if len(df) >= 200 else None
            indicators['ema_12'] = df['close'].ewm(span=12).mean().iloc[-1]
            indicators['ema_26'] = df['close'].ewm(span=26).mean().iloc[-1]
            
            # RSI
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            indicators['rsi'] = (100 - (100 / (1 + rs))).iloc[-1] if len(df) >= 14 else None
            
            # MACD
            ema_12 = df['close'].ewm(span=12).mean()
            ema_26 = df['close'].ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            macd_signal = macd_line.ewm(span=9).mean()
            indicators['macd'] = macd_line.iloc[-1]
            indicators['macd_signal'] = macd_signal.iloc[-1]
            indicators['macd_histogram'] = (macd_line - macd_signal).iloc[-1]
            
            # Bollinger Bands
            if len(df) >= 20:
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
            
            # Clean None values
            indicators = {k: v for k, v in indicators.items() if v is not None}
            
            return indicators
            
        except Exception as e:
            print(f"⚠️ Error calculating technical indicators: {e}")
            return {}
    
    def _generate_trading_recommendation(self, report: Dict) -> StockRecommendation:
        """Generate buy/sell recommendation for Indian stocks"""
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
            if rsi and rsi < 30:
                score += 2
                reasons.append("RSI oversold (bullish signal)")
            elif rsi and rsi > 70:
                score -= 2
                reasons.append("RSI overbought (bearish signal)")
            
            # Moving Average Analysis
            sma_20 = technical.get('sma_20')
            sma_50 = technical.get('sma_50')
            
            if sma_20 and sma_50:
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
            bb_position = technical.get('bb_position')
            if bb_position:
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
                target_price = current_price * 1.15  # 15% upside
                risk_level = "MEDIUM"
            elif score >= 1:
                action = "BUY"
                confidence = min(0.8, 0.6 + (score * 0.05))
                target_price = current_price * 1.08  # 8% upside
                risk_level = "MEDIUM"
            elif score <= -3:
                action = "STRONG_SELL"
                confidence = min(0.9, 0.6 + (abs(score) * 0.05))
                target_price = current_price * 0.85  # 15% downside
                risk_level = "HIGH"
            elif score <= -1:
                action = "SELL"
                confidence = min(0.8, 0.6 + (abs(score) * 0.05))
                target_price = current_price * 0.92  # 8% downside
                risk_level = "MEDIUM_HIGH"
            else:
                action = "HOLD"
                confidence = 0.5
                target_price = current_price
                risk_level = "MEDIUM"
            
            # Calculate stop loss (2% below current price for long positions)
            if action in ["BUY", "STRONG_BUY"]:
                stop_loss = current_price * 0.98
            else:
                stop_loss = current_price * 1.02
            
            reasoning = "; ".join(reasons) if reasons else "Mixed technical signals"
            
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
            
            volatility = returns.std() * np.sqrt(252)  # Annualized volatility
            var_95 = returns.quantile(0.05)  # 95% Value at Risk
            max_drawdown = ((df['close'] / df['close'].cummax()) - 1).min()
            
            # Sharpe ratio (assuming risk-free rate of 6% for India)
            excess_returns = returns.mean() * 252 - 0.06  # Annualized excess return
            sharpe_ratio = excess_returns / volatility if volatility != 0 else 0
            
            # Beta calculation (simplified)
            beta = returns.var() / returns.var() if returns.var() != 0 else 1
            
            return {
                'volatility': round(volatility, 4),
                'var_95': round(var_95, 4),
                'max_drawdown': round(max_drawdown, 4),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'beta': round(beta, 2),
                'risk_level': 'HIGH' if volatility > 0.4 else 'MEDIUM' if volatility > 0.25 else 'LOW'
            }
            
        except Exception as e:
            return {'risk_level': 'MEDIUM'}
