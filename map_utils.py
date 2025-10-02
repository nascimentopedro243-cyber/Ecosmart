import folium
from folium import plugins
import pandas as pd

class MapUtils:
    def __init__(self):
        # Rio de Janeiro coordinates as center
        self.default_center = [-22.9068, -43.1729]
        self.default_zoom = 12
    
    def create_main_map(self, trucks_data, bins_data, condominiums_data):
        """Create main monitoring map with all elements"""
        
        # Create base map
        m = folium.Map(
            location=self.default_center,
            zoom_start=self.default_zoom,
            tiles='OpenStreetMap'
        )
        
        # Add condominiums
        self.add_condominiums_to_map(m, condominiums_data, bins_data)
        
        # Add trucks
        self.add_trucks_to_map(m, trucks_data)
        
        # Add bins
        self.add_bins_to_map(m, bins_data)
        
        # Add legend
        self.add_legend_to_map(m)
        
        return m
    
    def add_condominiums_to_map(self, map_obj, condominiums_data, bins_data):
        """Add condominium markers to map"""
        
        for _, condo in condominiums_data.iterrows():
            # Count bins for this condominium
            condo_bins = bins_data[bins_data['condominium'] == condo['name']]
            full_bins = len(condo_bins[condo_bins['fill_level'] >= 80])
            total_bins = len(condo_bins)
            
            # Choose icon color based on urgent bins
            if full_bins > 0:
                icon_color = 'red'
                icon = 'exclamation-triangle'
            else:
                icon_color = 'blue'
                icon = 'building'
            
            # Create popup content
            popup_content = f"""
            <div style="width: 250px;">
                <h4>{condo['name']}</h4>
                <p><strong>Endereço:</strong> {condo['address']}</p>
                <p><strong>Contato:</strong> {condo['contact']}</p>
                <p><strong>Unidades:</strong> {condo['units']}</p>
                <p><strong>Lixeiras:</strong> {total_bins} (Cheias: {full_bins})</p>
            </div>
            """
            
            folium.Marker(
                location=[condo['latitude'], condo['longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{condo['name']} - {full_bins}/{total_bins} lixeiras cheias",
                icon=folium.Icon(color=icon_color, icon=icon, prefix='fa')
            ).add_to(map_obj)
    
    def add_trucks_to_map(self, map_obj, trucks_data):
        """Add truck markers to map"""
        
        for _, truck in trucks_data.iterrows():
            # Choose icon color based on status
            if truck['status'] == 'Ativo':
                icon_color = 'green'
                icon = 'truck'
            elif truck['status'] == 'Manutenção':
                icon_color = 'orange'
                icon = 'wrench'
            else:
                icon_color = 'gray'
                icon = 'truck'
            
            # Create popup content
            popup_content = f"""
            <div style="width: 200px;">
                <h4>🚛 {truck['truck_id']}</h4>
                <p><strong>Placa:</strong> {truck['plate']}</p>
                <p><strong>Motorista:</strong> {truck['driver']}</p>
                <p><strong>Status:</strong> {truck['status']}</p>
                <p><strong>Combustível:</strong> {truck['fuel_level']}%</p>
                <p><strong>Localização:</strong> {truck['current_location']}</p>
            </div>
            """
            
            folium.Marker(
                location=[truck['latitude'], truck['longitude']],
                popup=folium.Popup(popup_content, max_width=250),
                tooltip=f"{truck['truck_id']} - {truck['status']}",
                icon=folium.Icon(color=icon_color, icon=icon, prefix='fa')
            ).add_to(map_obj)
    
    def add_bins_to_map(self, map_obj, bins_data):
        """Add bin markers to map"""
        
        for _, bin_row in bins_data.iterrows():
            # Choose icon color based on fill level
            fill_level = bin_row['fill_level']
            if fill_level >= 90:
                icon_color = 'red'
                icon = 'trash'
            elif fill_level >= 70:
                icon_color = 'orange'
                icon = 'trash'
            else:
                icon_color = 'green'
                icon = 'trash'
            
            # Create popup content
            popup_content = f"""
            <div style="width: 200px;">
                <h4>🗑️ {bin_row['bin_id']}</h4>
                <p><strong>Condomínio:</strong> {bin_row['condominium']}</p>
                <p><strong>Localização:</strong> {bin_row['location']}</p>
                <p><strong>Nível:</strong> {fill_level}%</p>
                <p><strong>Capacidade:</strong> {bin_row['capacity']} kg</p>
                <p><strong>Atualizado:</strong> {bin_row['last_updated']}</p>
            </div>
            """
            
            # Create circle marker for bins
            folium.CircleMarker(
                location=[bin_row['latitude'], bin_row['longitude']],
                radius=8,
                popup=folium.Popup(popup_content, max_width=250),
                tooltip=f"{bin_row['bin_id']} - {fill_level}%",
                color='black',
                weight=2,
                fillColor=icon_color,
                fillOpacity=0.8
            ).add_to(map_obj)
    
    def create_route_map(self, route_data, trucks_data, bins_data):
        """Create map showing optimized route"""
        
        if not route_data or len(route_data['stops']) == 0:
            return folium.Map(location=self.default_center, zoom_start=self.default_zoom)
        
        # Get bounds for the route
        lats = [stop['latitude'] for stop in route_data['stops']]
        lngs = [stop['longitude'] for stop in route_data['stops']]
        lats.append(route_data['truck_position'][0])
        lngs.append(route_data['truck_position'][1])
        
        # Create map centered on route
        center_lat = sum(lats) / len(lats)
        center_lng = sum(lngs) / len(lngs)
        
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=13
        )
        
        # Add truck starting position
        folium.Marker(
            location=route_data['truck_position'],
            popup="🚛 Posição Inicial do Caminhão",
            tooltip="Início da Rota",
            icon=folium.Icon(color='blue', icon='play', prefix='fa')
        ).add_to(m)
        
        # Add route stops
        route_coordinates = [route_data['truck_position']]
        
        for i, stop in enumerate(route_data['stops']):
            stop_number = i + 1
            
            # Choose color based on fill level
            if stop['fill_level'] >= 90:
                color = 'red'
            elif stop['fill_level'] >= 70:
                color = 'orange'
            else:
                color = 'green'
            
            popup_content = f"""
            <div style="width: 250px;">
                <h4>Parada {stop_number}: {stop['bin_id']}</h4>
                <p><strong>Condomínio:</strong> {stop['condominium']}</p>
                <p><strong>Localização:</strong> {stop['location']}</p>
                <p><strong>Nível:</strong> {stop['fill_level']}%</p>
                <p><strong>Distância da parada anterior:</strong> {stop['distance_from_previous']:.1f} km</p>
                <p><strong>Chegada estimada:</strong> {stop['estimated_arrival']}</p>
                <p><strong>Coleta estimada:</strong> {stop['estimated_collection']:.0f} kg</p>
            </div>
            """
            
            folium.Marker(
                location=[stop['latitude'], stop['longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"Parada {stop_number} - {stop['fill_level']}%",
                icon=folium.Icon(
                    color=color, 
                    icon='flag', 
                    prefix='fa'
                )
            ).add_to(m)
            
            # Add stop number label
            folium.Marker(
                location=[stop['latitude'], stop['longitude']],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 12pt; font-weight: bold; color: white; background-color: {color}; border-radius: 50%; width: 25px; height: 25px; text-align: center; line-height: 25px;">{stop_number}</div>',
                    icon_size=(25, 25),
                    icon_anchor=(12, 12),
                )
            ).add_to(m)
            
            route_coordinates.append([stop['latitude'], stop['longitude']])
        
        # Draw route line
        folium.PolyLine(
            locations=route_coordinates,
            weight=4,
            color='blue',
            opacity=0.7,
            popup=f"Rota: {len(route_data['stops'])} paradas - {route_data['total_distance']:.1f} km"
        ).add_to(m)
        
        # Fit map to route bounds
        m.fit_bounds([[min(lats), min(lngs)], [max(lats), max(lngs)]])
        
        return m
    
    def create_bins_map(self, bins_data, condominiums_data):
        """Create map focused on trash bins"""
        
        if len(bins_data) == 0:
            return folium.Map(location=self.default_center, zoom_start=self.default_zoom)
        
        # Calculate center
        center_lat = bins_data['latitude'].mean()
        center_lng = bins_data['longitude'].mean()
        
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=13
        )
        
        # Add bins with clustering
        marker_cluster = plugins.MarkerCluster().add_to(m)
        
        for _, bin_row in bins_data.iterrows():
            fill_level = bin_row['fill_level']
            
            # Choose color
            if fill_level >= 90:
                color = 'red'
            elif fill_level >= 70:
                color = 'orange'
            else:
                color = 'green'
            
            popup_content = f"""
            <div style="width: 200px;">
                <h4>🗑️ {bin_row['bin_id']}</h4>
                <p><strong>Condomínio:</strong> {bin_row['condominium']}</p>
                <p><strong>Localização:</strong> {bin_row['location']}</p>
                <p><strong>Nível:</strong> {fill_level}%</p>
                <p><strong>Capacidade:</strong> {bin_row['capacity']} kg</p>
            </div>
            """
            
            folium.Marker(
                location=[bin_row['latitude'], bin_row['longitude']],
                popup=folium.Popup(popup_content, max_width=250),
                tooltip=f"{bin_row['bin_id']} - {fill_level}%",
                icon=folium.Icon(color=color, icon='trash', prefix='fa')
            ).add_to(marker_cluster)
        
        return m
    
    def add_legend_to_map(self, map_obj):
        """Add legend to map"""
        
        legend_html = """
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><strong>Legenda</strong></p>
        <p><i class="fa fa-building" style="color:blue"></i> Condomínios</p>
        <p><i class="fa fa-truck" style="color:green"></i> Caminhões Ativos</p>
        <p><i class="fa fa-circle" style="color:red"></i> Lixeiras Cheias (≥90%)</p>
        <p><i class="fa fa-circle" style="color:orange"></i> Lixeiras Atenção (70-89%)</p>
        <p><i class="fa fa-circle" style="color:green"></i> Lixeiras Normais (<70%)</p>
        </div>
        """
        
        map_obj.get_root().html.add_child(folium.Element(legend_html))
        
        return map_obj
