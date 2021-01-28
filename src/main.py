#!/usr/bin/env python
# coding: utf-8

import dash, math

import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from data import DataManager
from time_accessor import WeekTimeAccessor
from itertools import product
from dash_table import DataTable

from selenium.webdriver.support import expected_conditions as EC

app = dash.Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])
app.title = "Allocate++"
data = DataManager().get_data()

selection_div = html.Div(children=[], style={"display": "grid", "grid-template-columns": "repeat(4, 10fr)", "grid-gap": "10px"})

for unit, content in data.groupby("Unit"):
    unit_div = html.Div(children=[html.H5(children=unit)])
    for group, choices in content.groupby("Group"):
        unit_div.children.append(html.Label(group))
        unit_div.children.append(dcc.Dropdown(id=f"{unit}:{group}", options=choices[["Day", "Time"]].apply(lambda row : {"label": f"{row['Day']} {row['Time']}", "value": f"{row['Day']}, {row['Time']}"}, axis=1).tolist()))
    selection_div.children.append(unit_div)

app.layout = html.Div(children=[
    html.H1(children="Allocate++"),
    dcc.Tabs(children=[
        dcc.Tab(label="Overall Situation", value="Overall Situation", children=[
            html.H5("Number of Possible Clashes"),
            dcc.Graph(figure=go.Figure(go.Heatmap(x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], y=list(range(1, 25)), z=data.week_time.time_collides, colorscale=[[False, "#f5ebeb"], [True, "#c93c3c"]]))),
            html.H5("Options"),
            DataTable(id="table", columns=[{"name": column, "id": column} for column in data.columns], data=data.to_dict("records"))
    ]), dcc.Tab(label="Scheduler", value="Scheduler", children=[
        selection_div,
        dcc.Graph(id="schedule", figure=go.Figure(go.Heatmap(x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], y=list(range(1, 25)), z=[], colorscale=[[False, "#f5ebeb"], [True, "#c93c3c"]]))),
        DataTable(id="selected", columns=[{"name": column, "id": column} for column in data.columns], data=[])
    ])], value="Overall Situation"),
])

@app.callback(
    [dash.dependencies.Output("selected", "data"), dash.dependencies.Output("schedule", "figure")],
    [dash.dependencies.Input(f"{unit}:{group}", "value") for (unit, group), content in data.groupby(["Unit", "Group"])]
)
def update_output(*value):
    inputs, triggered = dash.callback_context.inputs, dash.callback_context.triggered

    selected = data.copy()
    selected["Include"] = False

    for group, choice in inputs.items():
        if choice != None:
            format_date = lambda date : f"{int(date.split(':')[0])}:{str(int(date.split(':')[1])).zfill(2)}"
            selected.loc[(selected["Unit"] == group[:-6].split(":")[0]) & (selected["Group"] == group[:-6].split(":")[1]) & (selected["Day"] == choice.split(", ")[0]) & (selected["Time"] == format_date(choice.split(', ')[1])), "Include"] = True

    z = selected[selected["Include"] == True][["Unit", "Group", "Day", "Time", "Duration"]].week_time.time_collides

    return selected[selected["Include"] == True].to_dict("records"), go.Figure(go.Heatmap(x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], y=list(range(1, 25)), z=z, colorscale=[[False, "#f5ebeb"], [True, "#c93c3c"]]))

if __name__ == "__main__":
    app.run_server(debug=True)