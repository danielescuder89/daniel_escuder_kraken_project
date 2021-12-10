import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.utils import Utils
from load.load import Loader
from wrangler.wrangler import Wrangler
from compute.compute import Computer

# By default we show data from yesterday
date_end = Utils.date_formats(datetime.now().strftime("%Y-%m-%d 00:00:00"))
date_start = Utils.date_formats((date_end['datetime'] -
                                 relativedelta(days=1)).strftime("%Y-%m-%d 00:00:00"))

# We create and initialize our object of trades
load = Loader()

# We get all Cash-to-Crypto pairs, Crypto-to-Crypto pairs and Cash-to-Cash pairs for the selector
load.get_all_pairs()
pairs_total = load.pairs

# Font format Lato
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

# We initialize our visualization in Dash
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Cryptocurrency Analysis"
server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Img(
                    # Logo
                    src=app.get_asset_url('logo.png'), className="header-logo"
                ),
                html.H1(
                    # Title
                    children="Cryptocurrency Analysis", className="header-title"
                ),
                html.P(
                    # Description
                    children="Analysis of the behavior of cryptocurrency"
                             " prices and their corresponding VWAP",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            # Pair selector
                            children="Select pair",
                            className="menu-title"),
                        dcc.Dropdown(
                            id="filter-pair",
                            options=[
                                {"label": pair, "value": pair}
                                # Value of all pairs
                                for pair in sorted(pairs_total['wsname'].tolist())
                            ],
                            # By default we show this pair
                            value="XBT/USDT",
                            clearable=False,
                            className="dropdown",
                        ),
                        dcc.Loading(
                            # We show loading symbol
                            id="loading-1",
                            children=[
                                html.Div([html.Div(id="loading-output-1")])],
                            type="circle",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Select grouping frecuency",
                            className="menu-title"),
                        dcc.Dropdown(
                            # Interval selector
                            id="filter-frecuency",
                            options=[
                                {"label": interval_type, "value": interval_type}
                                for interval_type in ["1 minute", "5 minutes", "30 minutes",
                                                      "60 minutes", "Daily", "Weekly", "Monthly"]
                            ],
                            # By default we show this interval
                            value="30 minutes",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                        dcc.Loading(
                            # We show loading symbol
                            id="loading-2",
                            children=[
                                html.Div([html.Div(id="loading-output-2")])],
                            type="circle",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Select date range",
                            className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            # Dates selector
                            id="range-date",
                            max_date_allowed=date_end['datetime'],
                            start_date=date_start['datetime'],
                            end_date=date_end['datetime'],
                            display_format="MMM, D, YYYY",
                        ),
                        dcc.Loading(
                            # We show loading symbol
                            id="loading-3",
                            children=[
                                html.Div([html.Div(id="loading-output-3")])],
                            type="circle",
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    # Price chart and vwap (lines)
                    children=dcc.Graph(
                        id="price_chart_figure", config={"displayModeBar": False},
                    ),
                    className="card",

                ),
                html.Div(
                    # Volume chart (bar)
                    children=dcc.Graph(
                        id="volume_chart_figure", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    [
        # These elements are modified...
        Output("price_chart_figure", "figure"),
        Output("volume_chart_figure", "figure"),
        Output("loading-output-1", "children"),
        Output("loading-output-2", "children"),
        Output("loading-output-3", "children"),
    ],
    [
        # ...modifying the inputs of the following elements (selectors)
        Input("filter-pair", "value"),
        Input("filter-frecuency", "value"),
        Input("range-date", "start_date"),
        Input("range-date", "end_date"),
    ],
)
def update_charts(pair, interval_type, start_date, end_date):
    """
        We get a thousand ticks (max) of a currency pair by connecting to the KRAKEN API.

        Parameters:
        pair -- string with the name of crytocurrency pair
        date_initial -- date from which we will get our ticks
    """
    # We create a global variable to not connect to the API if it is not necessary
    global load

    # We save the pair selected by the user
    pair_alt = "".join(
        pairs_total[pairs_total['wsname'] == pair]['altname'].to_numpy().tolist())

    # We only load data from the API if the user has modified the pair or date picker
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'].split('.')[0] != 'filter-frecuency':
        dt_start = Utils.date_formats(start_date[:10] + " 00:00:00")
        dt_end = Utils.date_formats(end_date[:10] + " 00:00:00")
        load.load_historic(pair_alt, dt_start['unixtime'], dt_end['unixtime'])

    # We clean the data of the load
    w = Wrangler()
    filtered_data = w.clean_data(load.data)[pair_alt]

    # We calculate vwap and get the volumes from here
    c = Computer(filtered_data)
    c.compute_vwap(interval=interval_type)
    filtered_data_vwap = c.data['vwap']

    price_chart_figure = {
        # First graphic design - price and vwap
        "data": [
            {
                "x": filtered_data["dtime"],
                "y": filtered_data["price"],
                "type": "lines",
                "hovertemplate": "%{y:.2f}<extra></extra>",
                "name": "price",
            },
            {
                "x": filtered_data_vwap.index,
                "y": filtered_data_vwap["price"],
                "type": "lines",
                "hovertemplate": "%{y:.2f}<extra></extra>",
                "name": "vwap",
            },
        ],
        "layout": {
            "title": {
                "text": "Price (" + pair + ")",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#17B897", "#E12D39"],
        },
    }

    volume_chart_figure = {
        # Second graphic design - volume
        "data": [
            {
                "x": filtered_data_vwap.index,
                "y": filtered_data_vwap["volume"],
                "type": "bar",
            },
        ],
        "layout": {
            "title": {
                "text": "Volume (" + pair + ")",
                "x": 0.05,
                "xanchor": "left"
            },
            "height": 300,
            "colorway": ["#014461"],
        },
    }
    # All outputs
    return price_chart_figure, volume_chart_figure, None, None, None


if __name__ == "__main__":
    app.run_server(debug=True)
