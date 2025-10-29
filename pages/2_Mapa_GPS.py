ValueError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/ecosmart/pages/2_Mapa_GPS.py", line 143, in <module>
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='OpenStreetMap' if map_style == 'OpenStreetMap' else 'Esri World Imagery' if map_style == 'Esri World Imagery (Satellite)' else 'Stamen Terrain'
    )
File "/home/adminuser/venv/lib/python3.13/site-packages/folium/folium.py", line 345, in __init__
    tile_layer = TileLayer(
        tiles=tiles, attr=attr, min_zoom=min_zoom, max_zoom=max_zoom
    )
File "/home/adminuser/venv/lib/python3.13/site-packages/folium/raster_layers.py", line 142, in __init__
    raise ValueError("Custom tiles must have an attribution.")
