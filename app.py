from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import json

# LOADING DATA
nyc_taxi = pd.read_pickle('nyc_taxi.pickle')
locations = pd.read_csv('data/taxi_zone_lookup.csv')
with open("data/taxi_zones/taxi_zones.geojson") as geofile:
    j_file = json.load(geofile)


external_script = ['https://cdn.tailwindcss.com']
#custom_css = ["/assets/styles.css"]


app = Dash(__name__, external_scripts=external_script)
# external_stylesheets=custom_css)

# Create server variable with Flask server object for use with gunicorn
server = app.server
app.title = 'NYC Taxi Trips 2021'


# app layout
app.layout = html.Div(children=[

    html.H1(children='NYC Taxi Trips',
            className='font-bold my-2 text-3xl underline decoration-yellow-400 decoration-dotted text-gray-700'),

    html.Div(
        children='An interactive visualisation of New York City Taxi Trips in the year 2011', className='mb-10 text-gray-900'),


    html.Div([
        dcc.Graph(id='create_map'),
        dcc.Graph(id='topzones', className='lg:mt-0 mt-10'),
    ], className='lg:flex justify-center'),



    html.Div(children=[
        html.H3(children='Select Months', className='font-bold'),
        dcc.RangeSlider(1, 11, 1, count=1, value=[
                        1, 12], className='my-2', id='select_months'),
        html.H3(children='Pickup or Dropoff', className='font-bold'),
        dcc.RadioItems([
            'Pickup', 'Dropoff',
        ], 'Pickup',
            inline=False, className='my-2 w-full', id='pudo_radio'),



    ], className='mt-10 p-2 bg-gray-100'),

    html.H1(children='Details',
            className='font-bold text-xl text-gray-700 mt-10 p-2'),

    html.Div([
        html.Div([
            html.H3('Number of Samples'),
            dcc.Slider(1000, 100000, value=1000, id='n_samples',
                       className='my-4 w-3/4'),
            html.H3('X-Axis Values'),
            dcc.Dropdown(['passenger_count', 'trip_distance',
                         'fare_amount', 'tip_amount'], value='passenger_count', id='x_axis', className='my-4 w-3/4 font-normal'),
            html.H3('Y-Axis Values'),
            dcc.Dropdown(['passenger_count', 'trip_distance',
                         'fare_amount', 'tip_amount'], value='trip_distance', id='y_axis', className='my-4 w-3/4 font-normal'),
        ], className='w-full font-bold'),
        html.Div([
            dcc.Graph(id='detailplot')
        ], className='w-full')

    ], className='lg:flex mt-5 p-2'),

    html.Div([

    ], className='h-40')

], className='container mx-auto')

# prepare data


def prepare_data(pudo, timerange):

    if pudo == 'Pickup':
        if timerange == [1, 12]:
            trips = nyc_taxi.groupby(['PULocationID']).size().reset_index()
        else:
            trips = nyc_taxi[(nyc_taxi.tpep_pickup_datetime.dt.month >= timerange[0]) & (
                nyc_taxi.tpep_pickup_datetime.dt.month <= timerange[1])].groupby(['PULocationID']).size().reset_index()
        trips.rename(
            columns={0: 'count', 'PULocationID': 'LocationID'}, inplace=True)
    else:
        if timerange == [1, 12]:
            trips = nyc_taxi.groupby(['DOLocationID']).size().reset_index()
        else:
            trips = nyc_taxi[(nyc_taxi.tpep_pickup_datetime.dt.month >= timerange[0]) & (
                nyc_taxi.tpep_pickup_datetime.dt.month <= timerange[1])].groupby(['DOLocationID']).size().reset_index()
        trips.rename(
            columns={0: 'count', 'DOLocationID': 'LocationID'}, inplace=True)

    trips_all = pd.merge(trips, locations, on='LocationID', how='inner')

    return trips_all


@app.callback(
    Output('create_map', 'figure'),
    Input('pudo_radio', 'value'),
    Input('select_months', 'value')
)
def create_map(pudo, timerange):

    trips = prepare_data(pudo, timerange)

    fig = px.choropleth_mapbox(trips, geojson=j_file,
                               locations='LocationID',
                               color='count',
                               featureidkey='properties.LocationID',
                               # color_continuous_scale="Viridis",
                               mapbox_style="carto-positron",
                               zoom=9, center={"lat": 40.719590, "lon": -73.990851},
                               opacity=0.5,
                               labels={'LocationID': 'LocationID',
                                       'count': 'Counts'},
                               hover_data=['Borough', 'Zone']
                               )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


# barchart
@app.callback(
    Output('topzones', 'figure'),
    Input('pudo_radio', 'value'),
    Input('select_months', 'value')
)
def create_topzones(pudo, timerange):

    trips = prepare_data(pudo, timerange)

    fig = px.bar(trips.sort_values('count', ascending=False).head(
        50), x='Zone', y='count', title='Top 50 Zones', labels={'count': '', 'Zone': ''}, color_discrete_sequence=['rgb(250,204,21)']*len(trips))
    fig.update_layout({'plot_bgcolor': 'rgb(255,255,255)'},
                      margin={"r": 40, "t": 40, "l": 40, "b": 0})

    return fig


# detail plot
@app.callback(
    Output('detailplot', 'figure'),
    Input('n_samples', 'value'),
    Input('x_axis', 'value'),
    Input('y_axis', 'value')
)
def create_detail_plot(n_samples, x_axis, y_axis):
    fig = px.scatter(nyc_taxi.sample(n_samples),
                     x=x_axis, y=y_axis, title=f'{x_axis} vs. {y_axis} on {n_samples} samples')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
