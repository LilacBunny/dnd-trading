import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from market_simulator import MarketSimulator
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dd_commodity_trading_secret_key_2024")

# Initialize market simulator
market_sim = MarketSimulator()

@app.route('/')
def dashboard():
    """Main dashboard showing current market overview"""
    market_data = market_sim.get_market_data()
    regions = market_sim.get_regions()
    commodities = market_sim.get_commodities()
    last_events = market_sim.get_last_events()
    
    return render_template('dashboard.html', 
                         market_data=market_data,
                         regions=regions,
                         commodities=commodities,
                         last_events=last_events)

@app.route('/regions')
def regions():
    """Regional comparison view"""
    export_region = request.args.get('export', 'Red Expanse')
    import_region = request.args.get('import', 'Solara')
    
    market_data = market_sim.get_market_data()
    regions = market_sim.get_regions()
    commodities = market_sim.get_commodities()
    
    # Calculate profit opportunities
    profit_analysis = market_sim.calculate_profit_opportunities(export_region, import_region)
    
    return render_template('regions.html',
                         market_data=market_data,
                         regions=regions,
                         commodities=commodities,
                         export_region=export_region,
                         import_region=import_region,
                         profit_analysis=profit_analysis)

@app.route('/charts')
def charts():
    """Historical price charts view"""
    selected_commodity = request.args.get('commodity', 'wheat')
    selected_region = request.args.get('region', 'Red Expanse')
    
    market_data = market_sim.get_market_data()
    regions = market_sim.get_regions()
    commodities = market_sim.get_commodities()
    
    return render_template('charts.html',
                         market_data=market_data,
                         regions=regions,
                         commodities=commodities,
                         selected_commodity=selected_commodity,
                         selected_region=selected_region)

@app.route('/events')
def events():
    """Event simulation view"""
    regions = market_sim.get_regions()
    available_events = market_sim.get_events_by_region()
    event_history = market_sim.get_event_history()
    
    return render_template('events.html',
                         regions=regions,
                         available_events=available_events,
                         event_history=event_history)

@app.route('/analytics')
def analytics():
    """Market analytics and insights"""
    market_data = market_sim.get_market_data()
    regions = market_sim.get_regions()
    commodities = market_sim.get_commodities()
    
    # Calculate market analytics
    volatility_analysis = market_sim.calculate_volatility_analysis()
    trend_analysis = market_sim.calculate_trend_analysis()
    regional_performance = market_sim.calculate_regional_performance()
    
    return render_template('analytics.html',
                         market_data=market_data,
                         regions=regions,
                         commodities=commodities,
                         volatility_analysis=volatility_analysis,
                         trend_analysis=trend_analysis,
                         regional_performance=regional_performance)

@app.route('/api/advance_day', methods=['POST'])
def advance_day():
    """Advance market by one day"""
    market_sim.update_prices()
    flash('Market advanced by one day', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/trigger_event', methods=['POST'])
def trigger_event():
    """Trigger a specific event in a region"""
    region = request.form.get('region')
    event_index = int(request.form.get('event_index'))
    
    if region and event_index is not None:
        success, message = market_sim.trigger_event(region, event_index)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
    else:
        flash('Invalid event parameters', 'error')
    
    return redirect(url_for('events'))

@app.route('/api/market_data/<region>')
def get_market_data(region):
    """API endpoint for real-time market data"""
    if region == 'all':
        data = market_sim.get_market_data()
    else:
        data = market_sim.get_region_data(region)
    return jsonify(data)

@app.route('/api/price_history/<region>/<commodity>')
def get_price_history(region, commodity):
    """API endpoint for price history data"""
    history = market_sim.get_price_history(region, commodity)
    return jsonify(history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)