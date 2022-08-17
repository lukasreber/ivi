from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import json


nyc_taxi = pd.read_pickle('nyc_taxi.pickle')


with open("data/taxi_zones/taxi_zones.geojson") as geofile:
    j_file = json.load(geofile)


external_script = ['https://cdn.tailwindcss.com']


app = Dash(__name__, external_scripts=external_script)

# Create server variable with Flask server object for use with gunicorn
server = app.server


# app layout
app.layout = html.Div(children=[

    html.H1(children='NYC Taxi Trips',
            className='font-bold my-2 text-3xl underline decoration-yellow-400 decoration-dotted text-gray-700'),

    html.Div(
        children='An interactive visualisation of New York City Taxi Trips in the year 2011', className='mb-10 text-gray-900'),

    dcc.Graph(id='create_map'),

    html.Div(children=[
        html.H3(children='Select Months', className='font-bold'),
        dcc.RangeSlider(1, 11, 1, count=1, value=[1, 12], className='my-2'),
        html.H3(children='Pickup or Dropoff', className='font-bold'),
        dcc.RadioItems([
            'Pickup', 'Dropoff',
        ], 'Pickup',
            inline=False, className='my-2 w-full', id='pudo_radio'),



    ], className='mt-10 p-2 bg-gray-100')

], className='container mx-auto my-5')

app.title = 'NYC Taxi Trips 2021'


@app.callback(
    Output('create_map', 'figure'),
    Input('pudo_radio', 'value')
)
def create_map(pudo):

    if pudo == 'Pickup':
        trips = nyc_taxi.groupby(['PULocationID']).size().reset_index()
        trips.rename(
            columns={0: 'count', 'PULocationID': 'LocationID'}, inplace=True)
    else:
        trips = nyc_taxi.groupby(['DOLocationID']).size().reset_index()
        trips.rename(
            columns={0: 'count', 'DOLocationID': 'LocationID'}, inplace=True)

    fig = px.choropleth_mapbox(trips, geojson=j_file,
                               locations='LocationID',
                               color='count',
                               featureidkey='properties.LocationID',
                               color_continuous_scale="Viridis",
                               mapbox_style="carto-positron",
                               zoom=9, center={"lat": 40.719590, "lon": -73.990851},
                               opacity=0.5,
                               labels={'LocationID': 'LocationID',
                                       'count': 'Counts'}
                               )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
