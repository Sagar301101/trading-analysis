"""
Fixed Flask REST API with correct NSE/BSE handling
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from finnhub_api import FinnhubStockAPI
import pandas as pd

app = Flask(__name__)
CORS(app)

# Initialize API
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', 'your_api_key_here')
stock_api = FinnhubStockAPI(FINNHUB_API_KEY) if FINNHUB_API_KEY != 'your_api_key_here' else None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'api_connected': stock_api is not None
    })

@app.route('/api/stocks/list', methods=['GET'])
def list_stocks():
    """
    List stocks from exchange
    
    CORRECTED USAGE:
    - /api/stocks/list?exchange=US&limit=100 (US stocks)
    - /api/stocks/list?exchange=NSE&limit=100 (NSE India stocks)  
    - /api/stocks/list?exchange=BSE&limit=100 (BSE India stocks)
    """
    if not stock_api:
        return jsonify({'error': 'API not initialized. Check FINNHUB_API_KEY'}), 500
    
    try:
        exchange = request.args.get('exchange', 'US')
        limit = request.args.get('limit', type=int)
        
        print(f"📊 Received request for exchange: {exchange}")
        
        # Handle Indian exchanges correctly
        if exchange in ['IN', 'NSE', 'BSE']:
            return get_indian_stocks(exchange, limit)
        else:
            # Handle other exchanges normally
            stocks_df = stock_api.list_all_stocks(exchange=exchange, limit=limit)
        
        if stocks_df.empty:
            return jsonify({
                'message': f'No stocks found for exchange: {exchange}',
                'data': [],
                'count': 0,
                'suggestion': 'Try: US, NSE, BSE, LSE, TSE'
            })
        
        stocks_list = stocks_df.to_dict('records')
        
        return jsonify({
            'message': f'Successfully fetched stocks from {exchange}',
            'exchange': exchange,
            'count': len(stocks_list),
            'data': stocks_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_indian_stocks(exchange, limit):
    """
    Special handler for Indian stocks (NSE/BSE)
    """
    try:
        print(f"🇮🇳 Fetching Indian stocks for {exchange}")
        
        # Method 1: Try to get all symbols from US exchange and filter Indian ones
        all_symbols = stock_api.client.stock_symbols('US')
        
        if not all_symbols:
            # Method 2: Try popular Indian stocks if API fails
            return get_popular_indian_stocks_response(exchange, limit)
        
        # Filter for Indian stocks
        indian_stocks = []
        for stock in all_symbols:
            symbol = stock.get('symbol', '')
            if exchange == 'NSE' and symbol.endswith('.NS'):
                indian_stocks.append(stock)
            elif exchange == 'BSE' and symbol.endswith('.BO'):
                indian_stocks.append(stock)
            elif exchange == 'IN' and (symbol.endswith('.NS') or symbol.endswith('.BO')):
                indian_stocks.append(stock)
        
        # If no results, try alternative method
        if not indian_stocks:
            return get_popular_indian_stocks_response(exchange, limit)
        
        # Apply limit
        if limit and len(indian_stocks) > limit:
            indian_stocks = indian_stocks[:limit]
        
        # Add metadata
        for stock in indian_stocks:
            stock['exchange'] = exchange
            stock['listed_date'] = datetime.now().strftime('%Y-%m-%d')
            if 'description' in stock:
                stock['company_name'] = stock['description']
            if 'symbol' in stock:
                stock['ticker'] = stock['symbol']
        
        return jsonify({
            'message': f'Successfully fetched {len(indian_stocks)} stocks from {exchange}',
            'exchange': exchange,
            'count': len(indian_stocks),
            'data': indian_stocks,
            'note': 'Filtered from global stock list'
        })
        
    except Exception as e:
        print(f"❌ Error fetching Indian stocks: {e}")
        return get_popular_indian_stocks_response(exchange, limit)

def get_popular_indian_stocks_response(exchange, limit):
    """
    Fallback: Return popular Indian stocks when API filtering fails
    """
    popular_stocks = {
        'NSE': [
            {'symbol': 'RELIANCE.NS', 'description': 'Reliance Industries Limited', 'type': 'Common Stock'},
            {'symbol': 'TCS.NS', 'description': 'Tata Consultancy Services Limited', 'type': 'Common Stock'},
            {'symbol': 'INFY.NS', 'description': 'Infosys Limited', 'type': 'Common Stock'},
            {'symbol': 'HDFCBANK.NS', 'description': 'HDFC Bank Limited', 'type': 'Common Stock'},
            {'symbol': 'ICICIBANK.NS', 'description': 'ICICI Bank Limited', 'type': 'Common Stock'},
            {'symbol': 'HINDUNILVR.NS', 'description': 'Hindustan Unilever Limited', 'type': 'Common Stock'},
            {'symbol': 'BHARTIARTL.NS', 'description': 'Bharti Airtel Limited', 'type': 'Common Stock'},
            {'symbol': 'ITC.NS', 'description': 'ITC Limited', 'type': 'Common Stock'},
            {'symbol': 'KOTAKBANK.NS', 'description': 'Kotak Mahindra Bank Limited', 'type': 'Common Stock'},
            {'symbol': 'LT.NS', 'description': 'Larsen & Toubro Limited', 'type': 'Common Stock'},
            {'symbol': 'SBIN.NS', 'description': 'State Bank of India', 'type': 'Common Stock'},
            {'symbol': 'ASIANPAINT.NS', 'description': 'Asian Paints Limited', 'type': 'Common Stock'},
            {'symbol': 'MARUTI.NS', 'description': 'Maruti Suzuki India Limited', 'type': 'Common Stock'},
            {'symbol': 'BAJFINANCE.NS', 'description': 'Bajaj Finance Limited', 'type': 'Common Stock'},
            {'symbol': 'HCLTECH.NS', 'description': 'HCL Technologies Limited', 'type': 'Common Stock'},
            {'symbol': 'WIPRO.NS', 'description': 'Wipro Limited', 'type': 'Common Stock'},
            {'symbol': 'ULTRACEMCO.NS', 'description': 'UltraTech Cement Limited', 'type': 'Common Stock'},
            {'symbol': 'TITAN.NS', 'description': 'Titan Company Limited', 'type': 'Common Stock'},
            {'symbol': 'NESTLEIND.NS', 'description': 'Nestle India Limited', 'type': 'Common Stock'},
            {'symbol': 'POWERGRID.NS', 'description': 'Power Grid Corporation of India Limited', 'type': 'Common Stock'}
        ],
        'BSE': [
            {'symbol': 'RELIANCE.BO', 'description': 'Reliance Industries Limited', 'type': 'Common Stock'},
            {'symbol': 'TCS.BO', 'description': 'Tata Consultancy Services Limited', 'type': 'Common Stock'},
            {'symbol': 'INFY.BO', 'description': 'Infosys Limited', 'type': 'Common Stock'},
            {'symbol': 'HDFCBANK.BO', 'description': 'HDFC Bank Limited', 'type': 'Common Stock'},
            {'symbol': 'ICICIBANK.BO', 'description': 'ICICI Bank Limited', 'type': 'Common Stock'},
            {'symbol': 'HINDUNILVR.BO', 'description': 'Hindustan Unilever Limited', 'type': 'Common Stock'},
            {'symbol': 'BHARTIARTL.BO', 'description': 'Bharti Airtel Limited', 'type': 'Common Stock'},
            {'symbol': 'ITC.BO', 'description': 'ITC Limited', 'type': 'Common Stock'},
            {'symbol': 'KOTAKBANK.BO', 'description': 'Kotak Mahindra Bank Limited', 'type': 'Common Stock'},
            {'symbol': 'LT.BO', 'description': 'Larsen & Toubro Limited', 'type': 'Common Stock'}
        ]
    }
    
    # Get stocks based on exchange
    stocks = popular_stocks.get(exchange, popular_stocks.get('NSE', []))
    
    # Apply limit
    if limit and len(stocks) > limit:
        stocks = stocks[:limit]
    
    # Add metadata
    for stock in stocks:
        stock['exchange'] = exchange
        stock['currency'] = 'INR'
        stock['country'] = 'India'
        stock['listed_date'] = datetime.now().strftime('%Y-%m-%d')
        stock['company_name'] = stock['description']
        stock['ticker'] = stock['symbol']
    
    return jsonify({
        'message': f'Popular {exchange} stocks (fallback data)',
        'exchange': exchange,
        'count': len(stocks),
        'data': stocks,
        'note': 'Using curated list of popular Indian stocks'
    })

@app.route('/api/stocks/search', methods=['GET'])
def search_stocks():
    """Search stocks by name or symbol"""
    if not stock_api:
        return jsonify({'error': 'API not initialized'}), 500
    
    try:
        query = request.args.get('q')
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        limit = request.args.get('limit', 20, type=int)
        
        results_df = stock_api.search_stocks(query=query, limit=limit)
        
        if results_df.empty:
            return jsonify({
                'message': f'No stocks found matching: {query}',
                'query': query,
                'data': [],
                'count': 0
            })
        
        results_list = results_df.to_dict('records')
        
        return jsonify({
            'message': f'Found stocks matching: {query}',
            'query': query,
            'count': len(results_list),
            'data': results_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/report/<symbol>', methods=['GET'])
def get_stock_report(symbol):
    """Get comprehensive stock analysis report"""
    if not stock_api:
        return jsonify({'error': 'API not initialized'}), 500
    
    try:
        years = request.args.get('years', 2, type=int)
        
        if not symbol or len(symbol) > 15:
            return jsonify({'error': 'Invalid stock symbol'}), 400
        
        if years < 1 or years > 10:
            return jsonify({'error': 'Years must be between 1 and 10'}), 400
        
        report = stock_api.get_stock_report(symbol.upper(), period_years=years)
        
        if 'error' in report:
            return jsonify({
                'error': f'Unable to generate report for {symbol}',
                'details': report['error']
            }), 404
        
        # Convert StockRecommendation dataclass to dict
        if 'trading_recommendation' in report:
            rec = report['trading_recommendation']
            report['trading_recommendation'] = {
                'action': rec.action,
                'current_price': rec.current_price,
                'target_price': rec.target_price,
                'stop_loss': rec.stop_loss,
                'confidence': rec.confidence,
                'reasoning': rec.reasoning,
                'risk_level': rec.risk_level
            }
        
        return jsonify({
            'message': f'Successfully generated report for {symbol}',
            'report': report
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/recommendation/<symbol>', methods=['GET'])
def get_quick_recommendation(symbol):
    """Quick trading recommendation"""
    if not stock_api:
        return jsonify({'error': 'API not initialized'}), 500
    
    try:
        report = stock_api.get_stock_report(symbol.upper(), period_years=1)
        
        if 'error' in report:
            return jsonify({'error': f'Unable to get recommendation for {symbol}'}), 404
        
        if 'trading_recommendation' in report:
            rec = report['trading_recommendation']
            recommendation = {
                'symbol': symbol.upper(),
                'action': rec.action,
                'current_price': rec.current_price,
                'target_price': rec.target_price,
                'stop_loss': rec.stop_loss,
                'confidence': rec.confidence,
                'reasoning': rec.reasoning,
                'risk_level': rec.risk_level,
                'generated_at': datetime.now().isoformat()
            }
            
            return jsonify({
                'message': f'Trading recommendation for {symbol}',
                'recommendation': recommendation
            })
        else:
            return jsonify({'error': 'Unable to generate recommendation'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Fixed Finnhub Stock Analysis API Server...")
    print("📋 Available endpoints:")
    print("   GET  /api/health")
    print("   GET  /api/stocks/list?exchange=NSE&limit=100  (NSE India)")
    print("   GET  /api/stocks/list?exchange=BSE&limit=100  (BSE India)")
    print("   GET  /api/stocks/list?exchange=US&limit=100   (US stocks)")
    print("   GET  /api/stocks/search?q=Reliance")
    print("   GET  /api/stocks/report/RELIANCE.NS?years=2")
    print("   GET  /api/stocks/recommendation/TCS.NS")
    print("\n🇮🇳 Correct URLs for Indian stocks:")
    print("   http://localhost:5000/api/stocks/list?exchange=NSE&limit=50")
    print("   http://localhost:5000/api/stocks/list?exchange=BSE&limit=50")  
    print("   http://localhost:5000/api/stocks/report/RELIANCE.NS")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
