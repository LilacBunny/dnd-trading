import random
import json
import os
from datetime import datetime, timedelta

class MarketSimulator:
    def __init__(self):
        # Base commodity data from 1340 CE, in D&D 5e currency (gp, sp, cp)
        self.commodities = {
            "wheat": {"base_price": 0.01, "unit": "cp/lb", "volatility": 0.1},
            "wool": {"base_price": 5.0, "unit": "sp/lb", "volatility": 0.15},
            "salt": {"base_price": 0.05, "unit": "cp/lb", "volatility": 0.1},
            "pepper": {"base_price": 1.5, "unit": "gp/lb", "volatility": 0.3},
            "saffron": {"base_price": 15.0, "unit": "gp/lb", "volatility": 0.4},
            "wine": {"base_price": 4.0, "unit": "sp/gallon", "volatility": 0.15},
            "olive_oil": {"base_price": 7.0, "unit": "sp/gallon", "volatility": 0.2},
            "herring": {"base_price": 0.04, "unit": "cp/lb", "volatility": 0.1},
            "iron": {"base_price": 0.1, "unit": "sp/lb", "volatility": 0.1},
            "copper": {"base_price": 0.5, "unit": "sp/lb", "volatility": 0.15},
            "silver": {"base_price": 5.0, "unit": "gp/lb", "volatility": 0.2},
            "timber": {"base_price": 1.5, "unit": "sp/cubic foot", "volatility": 0.2},
            "furs": {"base_price": 1.5, "unit": "gp/lb", "volatility": 0.3},
            "woad": {"base_price": 3.0, "unit": "sp/lb", "volatility": 0.15},
            "madder": {"base_price": 2.0, "unit": "sp/lb", "volatility": 0.15}
        }

        # Region-specific price modifiers (percentage increase/decrease)
        self.region_modifiers = {
            "Red Expanse": {
                "timber": 0.2, "wine": 0.15, "olive_oil": 0.15, "pepper": 0.1, "saffron": 0.1, "iron": -0.1, "copper": -0.1, "silver": -0.05
            },
            "Verdania": {
                "timber": -0.1, "iron": 0.1, "silver": 0.1
            },
            "Solara": {
                "pepper": -0.05, "saffron": -0.05, "silver": 0.1
            },
            "Frostveil": {
                "pepper": 0.2, "saffron": 0.2, "furs": -0.1
            },
            "Eldergraze": {
                "wheat": -0.1, "wool": -0.05, "madder": -0.05
            },
            "Ironcrag": {
                "iron": -0.1, "copper": -0.1, "furs": -0.05
            },
            "Saffronveil": {
                "pepper": -0.1, "saffron": -0.1, "timber": 0.1
            },
            "Mirehold": {
                "herring": -0.1, "woad": -0.05
            }
        }

        # Events by region
        self.events_by_region = {
            "Red Expanse": [
                {"description": "Sandstorm halts rail transport", "effects": {"timber": 0.2, "olive_oil": 0.15, "wine": 0.1}},
                {"description": "Mine collapse", "effects": {"iron": 0.2, "copper": 0.2, "silver": 0.25}},
                {"description": "Bandit raid on railway", "effects": {"pepper": 0.2, "furs": 0.2, "silver": 0.15}}
            ],
            "Verdania": [
                {"description": "Forest fire", "effects": {"timber": 0.2, "woad": 0.15, "furs": 0.1}},
                {"description": "Poor harvest", "effects": {"wheat": 0.15, "wool": 0.1}},
                {"description": "Druidic blessing", "effects": {"timber": -0.1, "woad": -0.1}}
            ],
            "Solara": [
                {"description": "Disease outbreak", "effects": {"wine": 0.2, "olive_oil": 0.2, "herring": 0.15}},
                {"description": "Pirate attack", "effects": {"pepper": 0.25, "saffron": 0.25, "wine": 0.1}},
                {"description": "Trade boom", "effects": {"pepper": -0.1, "saffron": -0.1}}
            ],
            "Frostveil": [
                {"description": "Flood", "effects": {"furs": 0.2, "herring": 0.2, "timber": 0.15}},
                {"description": "Blizzard", "effects": {"furs": 0.25, "herring": 0.1}},
                {"description": "Tribal truce", "effects": {"furs": -0.1, "herring": -0.05}}
            ],
            "Eldergraze": [
                {"description": "Drought", "effects": {"wheat": 0.2, "wool": 0.15, "madder": 0.1}},
                {"description": "Grassland fire", "effects": {"wheat": 0.15, "wool": 0.1}},
                {"description": "Bumper crop", "effects": {"wheat": -0.1, "madder": -0.1}}
            ],
            "Ironcrag": [
                {"description": "Avalanche", "effects": {"iron": 0.2, "copper": 0.2, "silver": 0.25}},
                {"description": "Mine strike", "effects": {"iron": 0.15, "copper": 0.15}},
                {"description": "New vein discovery", "effects": {"iron": -0.1, "copper": -0.1}}
            ],
            "Saffronveil": [
                {"description": "Monsoon", "effects": {"pepper": 0.2, "saffron": 0.2, "timber": 0.15}},
                {"description": "War with rivals", "effects": {"pepper": 0.25, "saffron": 0.25}},
                {"description": "Spice harvest", "effects": {"pepper": -0.1, "saffron": -0.1}}
            ],
            "Mirehold": [
                {"description": "Swamp flood", "effects": {"herring": 0.2, "woad": 0.15}},
                {"description": "Pest infestation", "effects": {"herring": 0.15, "woad": 0.1}},
                {"description": "Fishing boom", "effects": {"herring": -0.1, "woad": -0.05}}
            ]
        }

        self.market_file = "market_state.json"
        self.market, self.last_events, self.event_history = self.load_market()

    def load_market(self):
        """Load market state from file or initialize with base prices for each region"""
        if os.path.exists(self.market_file):
            with open(self.market_file, 'r') as f:
                data = json.load(f)
                return (data.get("market", {}), 
                       data.get("last_events", {}), 
                       data.get("event_history", []))
        
        # Initialize market with separate price history for each region
        market = {region: {comm: {"current_price": data["base_price"], "history": [data["base_price"]]} 
                          for comm, data in self.commodities.items()} 
                 for region in self.region_modifiers.keys()}
        
        last_events = {region: None for region in self.region_modifiers.keys()}
        event_history = []
        
        return market, last_events, event_history

    def save_market(self):
        """Save market state and last events to file"""
        with open(self.market_file, 'w') as f:
            json.dump({
                "market": self.market, 
                "last_events": self.last_events,
                "event_history": self.event_history
            }, f, indent=4)

    def format_price(self, price, unit):
        """Format price in D&D currency (gp, sp, cp)"""
        if "gp" in unit:
            return f"{price:.2f} gp"
        elif "sp" in unit:
            return f"{price:.2f} sp"
        else:  # cp
            return f"{price:.2f} cp"

    def update_prices(self):
        """Simulate one day's price changes for all regions"""
        for region in self.market.keys():
            for commodity, data in self.commodities.items():
                current_price = self.market[region][commodity]["current_price"]
                volatility = data["volatility"]
                
                # Random fluctuation
                change = random.gauss(0, volatility) * current_price
                new_price = max(0.1 * data["base_price"], current_price + change)
                
                # Apply region-specific modifier
                if region in self.region_modifiers and commodity in self.region_modifiers[region]:
                    new_price *= (1 + self.region_modifiers[region][commodity])
                
                self.market[region][commodity]["current_price"] = new_price
                self.market[region][commodity]["history"].append(new_price)
                
                # Keep only last 30 days
                if len(self.market[region][commodity]["history"]) > 30:
                    self.market[region][commodity]["history"].pop(0)
        
        self.save_market()

    def trigger_event(self, region, event_index):
        """Apply event-based price changes"""
        try:
            if region not in self.events_by_region:
                return False, "Invalid region"
            
            if event_index >= len(self.events_by_region[region]):
                return False, "Invalid event index"
            
            event = self.events_by_region[region][event_index]
            
            # Record event in history
            event_record = {
                "timestamp": datetime.now().isoformat(),
                "region": region,
                "description": event["description"],
                "effects": event["effects"]
            }
            self.event_history.append(event_record)
            
            # Keep only last 50 events
            if len(self.event_history) > 50:
                self.event_history.pop(0)
            
            self.last_events[region] = event['description']
            
            for commodity, change in event["effects"].items():
                if commodity in self.market[region]:
                    self.market[region][commodity]["current_price"] *= (1 + change)
                    self.market[region][commodity]["current_price"] = max(
                        0.1 * self.commodities[commodity]["base_price"], 
                        self.market[region][commodity]["current_price"]
                    )
                    self.market[region][commodity]["history"].append(
                        self.market[region][commodity]["current_price"]
                    )
                    if len(self.market[region][commodity]["history"]) > 30:
                        self.market[region][commodity]["history"].pop(0)
            
            self.save_market()
            return True, f"Event '{event['description']}' triggered in {region}"
        
        except Exception as e:
            return False, f"Error triggering event: {str(e)}"

    def calculate_profit_opportunities(self, export_region, import_region):
        """Calculate profit opportunities between two regions"""
        opportunities = []
        
        for commodity in self.commodities.keys():
            export_price = self.market[export_region][commodity]["current_price"]
            import_price = self.market[import_region][commodity]["current_price"]
            
            profit_margin = import_price - export_price
            profit_percentage = (profit_margin / export_price) * 100 if export_price > 0 else 0
            
            opportunities.append({
                "commodity": commodity,
                "export_price": export_price,
                "import_price": import_price,
                "profit_margin": profit_margin,
                "profit_percentage": profit_percentage,
                "unit": self.commodities[commodity]["unit"]
            })
        
        # Sort by profit percentage descending
        opportunities.sort(key=lambda x: x["profit_percentage"], reverse=True)
        return opportunities

    def calculate_volatility_analysis(self):
        """Calculate volatility analysis for all commodities"""
        analysis = {}
        
        for commodity in self.commodities.keys():
            regional_volatilities = []
            
            for region in self.region_modifiers.keys():
                history = self.market[region][commodity]["history"]
                if len(history) > 1:
                    changes = []
                    for i in range(1, len(history)):
                        change = abs((history[i] - history[i-1]) / history[i-1])
                        changes.append(change)
                    volatility = sum(changes) / len(changes) if changes else 0
                    regional_volatilities.append(volatility)
            
            avg_volatility = sum(regional_volatilities) / len(regional_volatilities) if regional_volatilities else 0
            analysis[commodity] = {
                "average_volatility": avg_volatility,
                "base_volatility": self.commodities[commodity]["volatility"],
                "volatility_rating": "High" if avg_volatility > 0.15 else "Medium" if avg_volatility > 0.05 else "Low"
            }
        
        return analysis

    def calculate_trend_analysis(self):
        """Calculate trend analysis for all commodities and regions"""
        analysis = {}
        
        for region in self.region_modifiers.keys():
            analysis[region] = {}
            for commodity in self.commodities.keys():
                history = self.market[region][commodity]["history"]
                if len(history) >= 2:
                    recent_change = (history[-1] - history[-2]) / history[-2] * 100
                    
                    if len(history) >= 7:
                        week_change = (history[-1] - history[-7]) / history[-7] * 100
                    else:
                        week_change = recent_change
                    
                    trend = "Rising" if recent_change > 2 else "Falling" if recent_change < -2 else "Stable"
                    
                    analysis[region][commodity] = {
                        "recent_change": recent_change,
                        "week_change": week_change,
                        "trend": trend
                    }
                else:
                    analysis[region][commodity] = {
                        "recent_change": 0,
                        "week_change": 0,
                        "trend": "Stable"
                    }
        
        return analysis

    def calculate_regional_performance(self):
        """Calculate regional market performance"""
        performance = {}
        
        for region in self.region_modifiers.keys():
            total_value = 0
            price_changes = []
            
            for commodity in self.commodities.keys():
                current_price = self.market[region][commodity]["current_price"]
                base_price = self.commodities[commodity]["base_price"]
                total_value += current_price
                
                if len(self.market[region][commodity]["history"]) >= 2:
                    recent_change = ((self.market[region][commodity]["history"][-1] - 
                                    self.market[region][commodity]["history"][-2]) / 
                                   self.market[region][commodity]["history"][-2])
                    price_changes.append(recent_change)
            
            avg_change = sum(price_changes) / len(price_changes) if price_changes else 0
            
            performance[region] = {
                "total_market_value": total_value,
                "average_change": avg_change * 100,
                "stability": "Stable" if abs(avg_change) < 0.02 else "Volatile",
                "last_event": self.last_events.get(region, "None")
            }
        
        return performance

    # Getter methods for the web interface
    def get_market_data(self):
        return self.market

    def get_regions(self):
        return list(self.region_modifiers.keys())

    def get_commodities(self):
        return self.commodities

    def get_last_events(self):
        return self.last_events

    def get_events_by_region(self):
        return self.events_by_region

    def get_event_history(self):
        return self.event_history[-20:]  # Return last 20 events

    def get_region_data(self, region):
        if region in self.market:
            return {region: self.market[region]}
        return {}

    def get_price_history(self, region, commodity):
        if region in self.market and commodity in self.market[region]:
            return {
                "commodity": commodity,
                "region": region,
                "history": self.market[region][commodity]["history"],
                "unit": self.commodities[commodity]["unit"]
            }
        return {}