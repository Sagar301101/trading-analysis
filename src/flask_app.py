"""
NSE and BSE Stock Analysis Flask API
Pure Indian Stock Market Focus
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from nse_bse_api import NSEBSEStockAPI

app = Flask(__name__)
CORS(app)

# Initialize NSE/BSE API
stock_api = NSEBSEStockAPI()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'api_connected': True,
        'supported_exchanges': ['NSE', 'BSE'],
        'currency': 'INR',
        'country': 'India'
    })

@app.route('/api/stocks/list', methods=['GET'])
def list_stocks():
    """
    List NSE or BSE stocks only
    
    Usage:
    - /api/stocks/list?exchange=NSE&limit=100 (NSE stocks)
    - /api/stocks/list?exchange=BSE&limit=50 (BSE stocks)
    """
    try:
        exchange = request.args.get('exchange', 'NSE')
        limit = request.args.get('limit', type=int)
        
        # Only allow NSE or BSE
        if exchange.upper() not in ['NSE', 'BSE']:
            return jsonify({
                'error': 'Only NSE and BSE exchanges supported',
                'supported_exchanges': ['NSE', 'BSE']
            }), 400
        
        stocks_df = stock_api.list_all_stocks(exchange=exchange.upper(), limit=limit)
        
        if stocks_df.empty:
            return jsonify({
                'message': f'No {exchange} stocks available',
                'data': [],
                'count': 0
            })
        
        stocks_list = stocks_df.to_dict('records')
        
        return jsonify({
            'message': f'Successfully fetched {exchange} stocks',
            'exchange': exchange.upper(),
            'count': len(stocks_list),
            'currency': 'INR',
            'country': 'India',
            'data': stocks_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/search', methods=['GET'])
def search_stocks():
    """
    Search NSE/BSE stocks by company name
    
    Usage:
    - /api/stocks/search?q=Reliance&exchange=NSE
    - /api/stocks/search?q=Tata&exchange=BSE&limit=10
    """
    try:
        query = request.args.get('q')
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        exchange = request.args.get('exchange', 'NSE')
        limit = request.args.get('limit', 20, type=int)
        
        # Only allow NSE or BSE
        if exchange.upper() not in ['NSE', 'BSE']:
            return jsonify({
                'error': 'Only NSE and BSE exchanges supported',
                'supported_exchanges': ['NSE', 'BSE']
            }), 400
        
        results_df = stock_api.search_stocks(query=query, exchange=exchange.upper(), limit=limit)
        
        if results_df.empty:
            return jsonify({
                'message': f'No {exchange} stocks found matching: {query}',
                'query': query,
                'exchange': exchange.upper(),
                'data': [],
                'count': 0
            })
        
        results_list = results_df.to_dict('records')
        
        return jsonify({
            'message': f'Found {exchange} stocks matching: {query}',
            'query': query,
            'exchange': exchange.upper(),
            'count': len(results_list),
            'data': results_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/report/<symbol>', methods=['GET'])
def get_stock_report(symbol):
    """
    Get comprehensive NSE/BSE stock analysis report
    
    Usage:
    - /api/stocks/report/RELIANCE.NS?years=3
    - /api/stocks/report/TCS.BO?years=2
    """
    try:
        years = request.args.get('years', 2, type=int)
        
        if not symbol:
            return jsonify({'error': 'Stock symbol is required'}), 400
        
        if years < 1 or years > 10:
            return jsonify({'error': 'Years must be between 1 and 10'}), 400
        
        # Ensure it's an Indian stock
        if not symbol.upper().endswith(('.NS', '.BO')):
            return jsonify({
                'error': 'Only NSE (.NS) and BSE (.BO) stocks supported',
                'example': 'Use RELIANCE.NS or TCS.BO'
            }), 400
        
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
    """
    Quick trading recommendation for NSE/BSE stocks
    
    Usage:
    - /api/stocks/recommendation/HDFCBANK.NS
    - /api/stocks/recommendation/ICICIBANK.BO
    """
    try:
        # Ensure it's an Indian stock
        if not symbol.upper().endswith(('.NS', '.BO')):
            return jsonify({
                'error': 'Only NSE (.NS) and BSE (.BO) stocks supported',
                'example': 'Use HDFCBANK.NS or ICICIBANK.BO'
            }), 400
        
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
                'currency': 'INR',
                'exchange': 'NSE' if symbol.upper().endswith('.NS') else 'BSE',
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

@app.route('/api/stocks/sectors', methods=['GET'])
def get_sectors():
    """Get available sectors for Indian stock market"""
    sectors = stock_api.sectors
    
    sector_info = []
    for sector, stocks in sectors.items():
        sector_info.append({
            'name': sector,
            'stock_count': len(stocks),
            'sample_stocks': stocks[:3]  # First 3 stocks as examples
        })
    
    return jsonify({
        'message': 'Available sectors in Indian stock market',
        'sectors': sector_info,
        'total_sectors': len(sectors)
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /api/stocks/list?exchange=NSE',
            'GET /api/stocks/search?q=Reliance&exchange=NSE',
            'GET /api/stocks/report/RELIANCE.NS',
            'GET /api/stocks/recommendation/TCS.NS',
            'GET /api/stocks/sectors'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🇮🇳 Starting NSE/BSE Stock Analysis API Server...")
    print("=" * 60)
    print("📋 Available endpoints:")
    print("   GET  /api/health")
    print("   GET  /api/stocks/list?exchange=NSE&limit=50")
    print("   GET  /api/stocks/list?exchange=BSE&limit=50")
    print("   GET  /api/stocks/search?q=Reliance&exchange=NSE")
    print("   GET  /api/stocks/report/RELIANCE.NS?years=2")
    print("   GET  /api/stocks/recommendation/TCS.NS")
    print("   GET  /api/stocks/sectors")
    print()
    print("🎯 Example URLs:")
    print("   http://localhost:5000/api/stocks/list?exchange=NSE&limit=20")
    print("   http://localhost:5000/api/stocks/report/HDFCBANK.NS")
    print("   http://localhost:5000/api/stocks/recommendation/ICICIBANK.NS")
    print()
    print("💰 Currency: INR | 🇮🇳 Country: India")
    print("📊 Data Source: Yahoo Finance")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
