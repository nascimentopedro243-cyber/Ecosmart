import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import math

class RouteOptimizer:
    def __init__(self):
        pass
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        return distance
    
    def generate_route(self, truck_position, bins_data, max_stops, optimization_criteria):
        """Generate optimized route for waste collection"""
        
        if len(bins_data) == 0:
            return None
        
        # Limit to max_stops
        available_bins = bins_data.head(max_stops).copy()
        
        # Calculate distances from truck to all bins
        truck_lat, truck_lng = truck_position
        
        available_bins['distance_from_truck'] = available_bins.apply(
            lambda row: self.calculate_distance(truck_lat, truck_lng, row['latitude'], row['longitude']),
            axis=1
        )
        
        # Apply optimization criteria
        if optimization_criteria == "Distância Mínima":
            # Sort by distance first, then by fill level
            available_bins = available_bins.sort_values(['distance_from_truck', 'fill_level'], ascending=[True, False])
        elif optimization_criteria == "Tempo Mínimo":
            # Consider both distance and accessibility (simulated)
            available_bins['time_score'] = available_bins['distance_from_truck'] * random.uniform(0.8, 1.2)
            available_bins = available_bins.sort_values('time_score')
        elif optimization_criteria == "Lixeiras Mais Cheias":
            # Sort by fill level first, then by distance
            available_bins = available_bins.sort_values(['fill_level', 'distance_from_truck'], ascending=[False, True])
        
        # Generate route stops
        route_stops = []
        current_lat, current_lng = truck_position
        total_distance = 0
        estimated_time = 0
        estimated_collection = 0
        
        for idx, (_, bin_row) in enumerate(available_bins.iterrows()):
            # Calculate distance from previous point
            distance_from_previous = self.calculate_distance(
                current_lat, current_lng, bin_row['latitude'], bin_row['longitude']
            )
            
            total_distance += distance_from_previous
            
            # Estimate collection amount based on fill level and capacity
            estimated_bin_collection = (bin_row['fill_level'] / 100) * bin_row['capacity']
            estimated_collection += estimated_bin_collection
            
            # Estimate arrival time (including service time)
            travel_time = distance_from_previous * 2.5  # ~2.5 minutes per km in city
            service_time = 10  # 10 minutes service time per bin
            estimated_time += travel_time + service_time
            
            # Calculate estimated arrival time
            arrival_time = datetime.now() + timedelta(minutes=estimated_time)
            
            stop_data = {
                'bin_id': bin_row['bin_id'],
                'condominium': bin_row['condominium'],
                'location': bin_row['location'],
                'latitude': bin_row['latitude'],
                'longitude': bin_row['longitude'],
                'fill_level': bin_row['fill_level'],
                'capacity': bin_row['capacity'],
                'distance_from_previous': distance_from_previous,
                'estimated_arrival': arrival_time.strftime('%H:%M'),
                'estimated_collection': estimated_bin_collection,
                'stop_order': idx + 1
            }
            
            route_stops.append(stop_data)
            
            # Update current position
            current_lat, current_lng = bin_row['latitude'], bin_row['longitude']
        
        # Create route summary
        route_data = {
            'truck_position': truck_position,
            'stops': route_stops,
            'total_distance': total_distance,
            'estimated_time': int(estimated_time),
            'estimated_collection': estimated_collection,
            'optimization_criteria': optimization_criteria,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return route_data
    
    def calculate_route_efficiency(self, route_data):
        """Calculate efficiency metrics for a route"""
        
        if not route_data or len(route_data['stops']) == 0:
            return None
        
        # Basic efficiency calculations
        distance_per_stop = route_data['total_distance'] / len(route_data['stops'])
        collection_per_km = route_data['estimated_collection'] / route_data['total_distance']
        avg_fill_level = sum(stop['fill_level'] for stop in route_data['stops']) / len(route_data['stops'])
        
        # Calculate efficiency score (0-100)
        # Higher score for: more collection per km, higher avg fill level, fewer km per stop
        efficiency_score = (
            (collection_per_km * 2) +  # Weight collection efficiency
            (avg_fill_level * 0.5) +   # Weight fill level
            (max(0, 10 - distance_per_stop) * 5)  # Weight distance efficiency
        )
        
        efficiency_score = min(100, max(0, efficiency_score))
        
        return {
            'efficiency_score': round(efficiency_score, 1),
            'distance_per_stop': round(distance_per_stop, 2),
            'collection_per_km': round(collection_per_km, 1),
            'avg_fill_level': round(avg_fill_level, 1)
        }
    
    def optimize_multi_truck_routes(self, trucks_data, bins_data, max_stops_per_truck=10):
        """Optimize routes for multiple trucks"""
        
        active_trucks = trucks_data[trucks_data['status'] == 'Ativo'].copy()
        high_priority_bins = bins_data[bins_data['fill_level'] >= 70].copy()
        
        if len(active_trucks) == 0 or len(high_priority_bins) == 0:
            return []
        
        routes = []
        remaining_bins = high_priority_bins.copy()
        
        for _, truck in active_trucks.iterrows():
            if len(remaining_bins) == 0:
                break
                
            truck_position = (truck['latitude'], truck['longitude'])
            
            # Generate route for this truck
            truck_route = self.generate_route(
                truck_position, 
                remaining_bins, 
                max_stops_per_truck,
                "Lixeiras Mais Cheias"
            )
            
            if truck_route:
                truck_route['truck_id'] = truck['truck_id']
                routes.append(truck_route)
                
                # Remove assigned bins from remaining bins
                assigned_bin_ids = [stop['bin_id'] for stop in truck_route['stops']]
                remaining_bins = remaining_bins[~remaining_bins['bin_id'].isin(assigned_bin_ids)]
        
        return routes
    
    def suggest_route_improvements(self, route_data):
        """Suggest improvements for a route"""
        
        suggestions = []
        
        if not route_data or len(route_data['stops']) == 0:
            return suggestions
        
        # Check for long distances between stops
        for i, stop in enumerate(route_data['stops']):
            if stop['distance_from_previous'] > 5:  # More than 5km
                suggestions.append(f"⚠️ Parada {i+1}: Distância longa ({stop['distance_from_previous']:.1f}km) - considere reordenar")
        
        # Check for low fill levels
        low_fill_stops = [stop for stop in route_data['stops'] if stop['fill_level'] < 50]
        if len(low_fill_stops) > 0:
            suggestions.append(f"💡 {len(low_fill_stops)} lixeiras com <50% - considere adiar para próxima coleta")
        
        # Check route efficiency
        efficiency = self.calculate_route_efficiency(route_data)
        if efficiency and efficiency['efficiency_score'] < 70:
            suggestions.append("📊 Eficiência baixa - tente otimizar por 'Distância Mínima'")
        
        # Check total time
        if route_data['estimated_time'] > 240:  # More than 4 hours
            suggestions.append("⏰ Rota longa (>4h) - considere dividir em duas rotas")
        
        return suggestions
