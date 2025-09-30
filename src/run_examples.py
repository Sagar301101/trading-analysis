"""
Usage Examples for Finnhub Stock Analysis APIs
"""

import os
import sys
sys.path.append('.')
from finnhub_api import FinnhubStockAPI

def main():
    """Run example usage of the stock analysis APIs"""
    
    # Get API key from environment
    api_key = os.getenv('FINNHUB_API_KEY')
    
    if not api_key or api_key == 'your_finnhub_api_key_here':
        print("❌ Error: Please set FINNHUB_API_KEY environment variable")
        print("1. Copy .env.example to .env")
        print("2. Edit .env and add your Finnhub API key")
        print("3. Run: source .env")
        return
    
    print("🚀 FINNHUB STOCK ANALYSIS API EXAMPLES")
    print("=" * 60)
    
    # Initialize API
    api = FinnhubStockAPI(api_key)
    
    # Example 1: List US stocks
    print("\n📈 EXAMPLE 1: LIST US STOCKS")
    print("-" * 40)
    stocks = api.list_all_stocks(exchange="US", limit=10)
    
    if not stocks.empty:
        print(f"Found {len(stocks)} stocks:")
        print(stocks[['symbol', 'description', 'type']].to_string(index=False))
    else:
        print("No stocks found")
    
    # Example 2: Search for stocks
    print("\n🔍 EXAMPLE 2: SEARCH STOCKS")
    print("-" * 40)
    search_results = api.search_stocks("Apple", limit=5)
    
    if not search_results.empty:
        print("Apple-related stocks:")
        print(search_results[['symbol', 'description']].to_string(index=False))
    else:
        print("No Apple stocks found")
    
    # Example 3: Comprehensive stock analysis
    print("\n📊 EXAMPLE 3: COMPREHENSIVE STOCK ANALYSIS")
    print("-" * 40)
    symbol = "AAPL"
    report = api.get_stock_report(symbol, period_years=2)
    
    if 'error' not in report:
        print(f"Analysis Report for {symbol}:")
        print(f"Generated: {report['generated_at']}")
        
        # Company Profile
        profile = report.get('company_profile', {})
        if profile:
            print(f"\n🏢 COMPANY PROFILE:")
            print(f"Name: {profile.get('name', 'N/A')}")
            print(f"Industry: {profile.get('finnhubIndustry', 'N/A')}")
            print(f"Market Cap: ${profile.get('marketCapitalization', 0):,.0f}M")
            print(f"Country: {profile.get('country', 'N/A')}")
        
        # Current Quote
        quote = report.get('current_quote', {})
        if quote:
            print(f"\n💰 CURRENT PRICE DATA:")
            print(f"Current Price: ${quote.get('c', 0):.2f}")
            print(f"Change: ${quote.get('d', 0):.2f} ({quote.get('dp', 0):.2f}%)")
            print(f"High: ${quote.get('h', 0):.2f}")
            print(f"Low: ${quote.get('l', 0):.2f}")
            print(f"Open: ${quote.get('o', 0):.2f}")
            print(f"Previous Close: ${quote.get('pc', 0):.2f}")
        
        # Technical Analysis
        technical = report.get('technical_analysis', {})
        if technical:
            print(f"\n📈 TECHNICAL INDICATORS:")
            print(f"RSI (14): {technical.get('rsi', 0):.2f}")
            print(f"MACD: {technical.get('macd', 0):.4f}")
            print(f"MACD Signal: {technical.get('macd_signal', 0):.4f}")
            print(f"20-day SMA: ${technical.get('sma_20', 0):.2f}")
            print(f"50-day SMA: ${technical.get('sma_50', 0):.2f}")
            print(f"200-day SMA: ${technical.get('sma_200', 0):.2f}")
            print(f"Support Level: ${technical.get('support', 0):.2f}")
            print(f"Resistance Level: ${technical.get('resistance', 0):.2f}")
        
        # Trading Recommendation
        rec = report.get('trading_recommendation')
        if rec:
            print(f"\n🎯 TRADING RECOMMENDATION:")
            print(f"Action: {rec.action}")
            print(f"Current Price: ${rec.current_price:.2f}")
            print(f"Target Price: ${rec.target_price:.2f}")
            print(f"Stop Loss: ${rec.stop_loss:.2f}")
            print(f"Confidence: {rec.confidence*100:.1f}%")
            print(f"Risk Level: {rec.risk_level}")
            print(f"Reasoning: {rec.reasoning}")
            
            # Calculate potential profit/loss
            if rec.action in ['BUY', 'STRONG_BUY']:
                potential_gain = ((rec.target_price - rec.current_price) / rec.current_price) * 100
                potential_loss = ((rec.stop_loss - rec.current_price) / rec.current_price) * 100
                print(f"Potential Gain: {potential_gain:.2f}%")
                print(f"Potential Loss: {potential_loss:.2f}%")
        
        # Risk Assessment
        risk = report.get('risk_assessment', {})
        if risk:
            print(f"\n⚠️ RISK ASSESSMENT:")
            print(f"Volatility (Annual): {risk.get('volatility', 0):.2%}")
            print(f"Max Drawdown: {risk.get('max_drawdown', 0):.2%}")
            print(f"Value at Risk (95%): {risk.get('var_95', 0):.2%}")
            print(f"Sharpe Ratio: {risk.get('sharpe_ratio', 0):.2f}")
            print(f"Risk Level: {risk.get('risk_level', 'N/A')}")
        
        print(f"\n💾 Report saved internally for {symbol}")
        
    else:
        print(f"❌ Error generating report for {symbol}: {report['error']}")
    
    # Example 4: Multiple stock comparison
    print("\n📊 EXAMPLE 4: MULTIPLE STOCK COMPARISON")
    print("-" * 40)
    
    comparison_symbols = ["AAPL", "MSFT", "GOOGL"]
    comparison_results = []
    
    for symbol in comparison_symbols:
        print(f"Analyzing {symbol}...")
        report = api.get_stock_report(symbol, period_years=1)
        
        if 'error' not in report:
            rec = report.get('trading_recommendation')
            risk = report.get('risk_assessment', {})
            
            if rec:
                comparison_results.append({
                    'Symbol': symbol,
                    'Action': rec.action,
                    'Current_Price': f"${rec.current_price:.2f}",
                    'Target_Price': f"${rec.target_price:.2f}",
                    'Confidence': f"{rec.confidence*100:.1f}%",
                    'Risk_Level': rec.risk_level,
                    'Volatility': f"{risk.get('volatility', 0):.1%}"
                })
    
    if comparison_results:
        print("\n🏆 PORTFOLIO RECOMMENDATIONS:")
        import pandas as pd
        df = pd.DataFrame(comparison_results)
        print(df.to_string(index=False))
    
    print("\n✅ All examples completed!")
    print("\n📝 Next Steps:")
    print("1. Start the Flask API server: python src/flask_app.py")
    print("2. Test API endpoints:")
    print("   - http://localhost:5000/api/health")
    print("   - http://localhost:5000/api/stocks/list?exchange=US&limit=10")
    print("   - http://localhost:5000/api/stocks/report/AAPL?years=2")

if __name__ == "__main__":
    main()
