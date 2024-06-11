import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

def start_hospital_map_dashboard():
    def fetch_hospitals_data():
        engine = create_engine('postgresql+psycopg2://user:password@postgres:5432/mydatabase')
        query = text("SELECT ST_AsText(geom) AS geom_text, Name FROM hospitals;")
        with engine.connect() as conn:
            result = conn.execute(query)
            df = pd.DataFrame(result.fetchall(), columns=['geom_text', 'Name'])
        # Extract latitude and longitude from WKT format
        df[['lon', 'lat']] = df['geom_text'].str.extract(r'POINT\(([^ ]+) ([^ ]+)\)').astype(float)
        return df

    df = fetch_hospitals_data()
    # Create a Plotly figure
    fig = px.scatter_mapbox(df, lat="lat", lon="lon", hover_name="Name", zoom=3, height=600)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.H1("Hospitals in Australia"),
        dcc.Graph(id="map", figure=fig)
    ])

    # Run the app
    app.run_server(debug=True)

# Call the function to start the dashboard
if __name__ == '__main__':
    start_hospital_map_dashboard()
