from dash import Dash
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import flask
from flask import Flask
from flask import render_template
from dash import html
import pandas as pd
import plotly
import plotly.express as px
import json
import molplotly4flask

server = Flask(__name__)

df_esol = pd.read_csv(
    'https://raw.githubusercontent.com/deepchem/deepchem/master/datasets/delaney-processed.csv')
df_esol['y_pred'] = df_esol['ESOL predicted log solubility in mols per litre']
df_esol['y_true'] = df_esol['measured log solubility in mols per litre']
df_esol['delY'] = df_esol["y_pred"] - df_esol["y_true"]

dash_app1 = Dash(__name__, server = server, url_base_pathname='/dashboard/' )
dash_app2 = Dash(__name__, server = server, url_base_pathname='/reports/')
dash_app1.layout = html.Div([html.H1('Hi there, I am app1 for dashboards')])
dash_app2.layout = html.Div([html.H1('Hi there, I am app2 for reports')])

fig_scatter = px.scatter(df_esol,
                         x="y_true",
                         y="y_pred",
                         color='delY',
                         title='ESOL Regression (default plotly)',
                         labels={'y_pred': 'Predicted Solubility',
                                 'y_true': 'Measured Solubility',
                                 'delY': 'dY'},
                         width=1200,
                         height=800)

molapp = Dash(__name__, server=server, url_base_pathname='/molplotly_test/')
molapp = app_scatter_with_captions = molplotly4flask.add_molecules(fig=fig_scatter,
                                                    df=df_esol,
                                                    app=molapp,
                                                    smiles_col='smiles',
                                                    title_col='Compound ID',
                                                    caption_cols=['Molecular Weight', 'Number of Rings'],
                                                    caption_transform={'Predicted Solubility': lambda x: f"{x:.2f}",
                                                                       'Measured Solubility': lambda x: f"{x:.2f}",
                                                                       'Molecular Weight': lambda x: f"{x:.2f}"
                                                                       },
                                                    show_coords=True)


@server.route('/plot1/')
def plot1():
    graphJSON = json.dumps(fig_scatter, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('plot1.html', graphJSON=graphJSON)

@server.route('/molplotly_test/')
def render_molplotly_test():
    print(type(molapp))
    #return 'hello'
    return flask.redirect('/testmol')

@server.route('/dashboard/')
def render_dashboard():
    return flask.redirect('/dash1')


@server.route('/reports/')
def render_reports():
    return flask.redirect('/dash2')

app = DispatcherMiddleware(server, {
    '/dash1': dash_app1.server,
    '/dash2': dash_app2.server,
    '/testmol': molapp.server
})

run_simple('localhost', 8080, app, use_reloader=True, use_debugger=True)

