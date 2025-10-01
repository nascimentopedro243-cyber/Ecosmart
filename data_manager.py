import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class DataManager:
    def __init__(self):
        self.initialize_data()
    
    def initialize_data(self):
        """Initialize sample data for the system"""
        
        # Condominiums data
        self.condominiums = pd.DataFrame([
            {
                'name': 'Residencial Vila Verde',
                'address': 'Rua das Flores, 123 - Rio de Janeiro, RJ',
                'latitude': -22.9068,
                'longitude': -43.1729,
                'contact': '(21) 3456-7890',
                'units': 150
            },
            {
                'name': 'Condomínio Parque das Árvores',
                'address': 'Av. Copacabana, 456 - Rio de Janeiro, RJ',
                'latitude': -22.9215,
                'longitude': -43.1895,
                'contact': '(21) 9876-5432',
                'units': 200
            },
            {
                'name': 'Torres do Lago',
                'address': 'Rua dos Lagos, 789 - Rio de Janeiro, RJ',
                'latitude': -22.8925,
                'longitude': -43.1556,
                'contact': '(21) 1234-5678',
                'units': 120
            },
            {
                'name': 'Residencial Jardim Azul',
                'address': 'Rua Azul, 321 - Rio de Janeiro, RJ',
                'latitude': -22.9345,
                'longitude': -43.1823,
                'contact': '(21) 5555-6666',
                'units': 80
            },
            {
                'name': 'Condomínio Solar',
                'address': 'Av. do Sol, 654 - Rio de Janeiro, RJ',
                'latitude': -22.8789,
                'longitude': -43.1467,
                'contact': '(21) 7777-8888',
                'units': 180
            }
        ])
        
        # Trucks data
        self.trucks = pd.DataFrame([
            {
                'truck_id': 'ECO-001',
                'plate': 'ABC-1234',
                'driver': 'João Silva',
                'status': 'Ativo',
                'latitude': -22.9068,
                'longitude': -43.1729,
                'current_location': 'Residencial Vila Verde',
                'fuel_level': 75,
                'capacity': 5000,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            {
                'truck_id': 'ECO-002',
                'plate': 'DEF-5678',
                'driver': 'Maria Santos',
                'status': 'Ativo',
                'latitude': -22.9215,
                'longitude': -43.1895,
                'current_location': 'Parque das Árvores',
                'fuel_level': 60,
                'capacity': 4500,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            {
                'truck_id': 'ECO-003',
                'plate': 'GHI-9012',
                'driver': 'Carlos Oliveira',
                'status': 'Manutenção',
                'latitude': -22.8925,
                'longitude': -43.1556,
                'current_location': 'Oficina Central',
                'fuel_level': 90,
                'capacity': 5500,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        ])
        
        # Trash bins data
        self.generate_bins_data()
        
    def generate_bins_data(self):
        """Generate trash bins data for all condominiums"""
        bins_list = []
        
        for _, condo in self.condominiums.iterrows():
            # Generate 3-5 bins per condominium
            num_bins = random.randint(3, 5)
            
            for i in range(num_bins):
                # Generate position near condominium
                lat_offset = random.uniform(-0.002, 0.002)
                lng_offset = random.uniform(-0.002, 0.002)
                
                bin_data = {
                    'bin_id': f"{str(condo['name'])[:3].upper()}-{i+1:03d}",
                    'condominium': condo['name'],
                    'location': f"Bloco {chr(65+i)} - Térreo",
                    'latitude': condo['latitude'] + lat_offset,
                    'longitude': condo['longitude'] + lng_offset,
                    'fill_level': random.randint(15, 95),
                    'capacity': random.choice([100, 150, 200]),
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                bins_list.append(bin_data)
        
        self.bins = pd.DataFrame(bins_list)
    
    def get_condominiums_data(self):
        """Return condominiums data"""
        return self.condominiums.copy()
    
    def get_trucks_data(self):
        """Return trucks data"""
        return self.trucks.copy()
    
    def get_bins_data(self):
        """Return bins data"""
        return self.bins.copy()
    
    def update_truck_positions(self):
        """Simulate truck position updates"""
        for idx, truck in self.trucks.iterrows():
            if truck['status'] == 'Ativo':
                # Small random movement
                lat_change = random.uniform(-0.001, 0.001)
                lng_change = random.uniform(-0.001, 0.001)
                
                self.trucks.at[idx, 'latitude'] += lat_change
                self.trucks.at[idx, 'longitude'] += lng_change
                self.trucks.at[idx, 'last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                
                # Update fuel level (decrease slightly)
                if truck['fuel_level'] > 10:
                    self.trucks.at[idx, 'fuel_level'] = float(truck['fuel_level']) - random.uniform(0.5, 2.0)
    
    def update_bin_levels(self):
        """Simulate bin level updates"""
        for idx, bin_row in self.bins.iterrows():
            # Randomly increase fill level slightly
            current_level = bin_row['fill_level']
            if current_level < 95:
                increase = random.uniform(0.5, 3.0)
                new_level = min(float(current_level) + increase, 100.0)
                self.bins.at[idx, 'fill_level'] = new_level
                self.bins.at[idx, 'last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    def add_condominium(self, name, address, lat, lng, contact, units):
        """Add new condominium"""
        try:
            # Check if name already exists
            if name in self.condominiums['name'].values:
                return False
            
            new_condo = pd.DataFrame([{
                'name': name,
                'address': address,
                'latitude': lat,
                'longitude': lng,
                'contact': contact,
                'units': units
            }])
            
            self.condominiums = pd.concat([self.condominiums, new_condo], ignore_index=True)
            return True
        except:
            return False
    
    def add_bin(self, bin_id, condominium, location, lat, lng, capacity):
        """Add new trash bin"""
        try:
            # Check if bin_id already exists
            if bin_id in self.bins['bin_id'].values:
                return False
            
            new_bin = pd.DataFrame([{
                'bin_id': bin_id,
                'condominium': condominium,
                'location': location,
                'latitude': lat,
                'longitude': lng,
                'fill_level': random.randint(10, 30),
                'capacity': capacity,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            }])
            
            self.bins = pd.concat([self.bins, new_bin], ignore_index=True)
            return True
        except:
            return False
    
    def add_truck(self, truck_id, plate, driver, capacity, fuel_capacity, status):
        """Add new truck"""
        try:
            # Check if truck_id already exists
            if truck_id in self.trucks['truck_id'].values:
                return False
            
            new_truck = pd.DataFrame([{
                'truck_id': truck_id,
                'plate': plate,
                'driver': driver,
                'status': status,
                'latitude': -23.550520,  # Default position
                'longitude': -46.633308,
                'current_location': 'Base Central',
                'fuel_level': 100,
                'capacity': capacity,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            }])
            
            self.trucks = pd.concat([self.trucks, new_truck], ignore_index=True)
            return True
        except:
            return False
    
    def update_truck_status(self, truck_id, new_status):
        """Update truck status"""
        mask = self.trucks['truck_id'] == truck_id
        self.trucks.loc[mask, 'status'] = new_status
        self.trucks.loc[mask, 'last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    def get_recent_collections(self):
        """Get simulated recent collections"""
        collections = []
        for i in range(5):
            time_ago = datetime.now() - timedelta(hours=random.randint(1, 24))
            collections.append({
                'time': time_ago.strftime('%d/%m %H:%M'),
                'location': random.choice(self.condominiums['name'].tolist()),
                'amount': random.randint(50, 200)
            })
        return collections
    
    def get_scheduled_collections(self):
        """Get simulated scheduled collections"""
        schedules = []
        for i in range(3):
            time_future = datetime.now() + timedelta(hours=random.randint(1, 48))
            schedules.append({
                'time': time_future.strftime('%d/%m %H:%M'),
                'location': random.choice(self.condominiums['name'].tolist()),
                'estimated_amount': random.randint(80, 150)
            })
        return schedules
    
    def get_collections_count_today(self):
        """Get number of collections today"""
        return random.randint(8, 15)
    
    def get_efficiency_data(self):
        """Get efficiency data over time"""
        dates = []
        efficiencies = []
        
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
            efficiencies.append(random.randint(75, 95))
        
        return pd.DataFrame({
            'date': reversed(dates),
            'efficiency_percentage': reversed(efficiencies)
        })
    
    def get_collections_by_condominium(self):
        """Get collections by condominium"""
        collections = []
        for condo in self.condominiums['name']:
            collections.append({
                'condominium': condo,
                'collections': random.randint(5, 15)
            })
        
        return pd.DataFrame(collections)
    
    def get_recent_routes(self):
        """Get recent routes data"""
        routes = []
        for i in range(5):
            date = datetime.now() - timedelta(days=random.randint(0, 7))
            routes.append({
                'id': f"R{1000 + i}",
                'date': date.strftime('%d/%m/%Y'),
                'truck_id': random.choice(self.trucks['truck_id'].tolist()),
                'stops_count': random.randint(5, 12),
                'distance': round(random.uniform(15, 45), 1),
                'duration': random.randint(90, 180),
                'status': random.choice(['Concluída', 'Em Andamento', 'Cancelada'])
            })
        return routes
    
    def get_route_efficiency_metrics(self):
        """Get route efficiency metrics"""
        return {
            'avg_distance': random.uniform(25, 35),
            'avg_duration': random.uniform(120, 150),
            'avg_efficiency': random.uniform(82, 92),
            'completion_rate': random.uniform(88, 96)
        }
    
    def get_performance_by_condominium(self):
        """Get performance metrics by condominium"""
        performance = []
        for condo in self.condominiums['name']:
            performance.append({
                'Condomínio': condo,
                'Coletas Realizadas': random.randint(10, 25),
                'Lixo Coletado (kg)': random.randint(800, 1500),
                'Eficiência (%)': random.randint(75, 95),
                'Tempo Médio (min)': random.randint(15, 35)
            })
        
        return pd.DataFrame(performance)
