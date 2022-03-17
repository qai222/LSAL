from dash import Dash, dcc, html, Input, Output
import plotly.express as px

import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv('output/WC__RandomForestRegressor.csv')

ligands = sorted(set(df["ligand"].tolist()))
ligands_labelled = sorted(set(df.dropna(subset=["y_real"])["ligand"].tolist()))

update_ligand_names = []
for n in df["ligand"]:
    if n in ligands_labelled:
        update_ligand_names.append("LABELLED--" + n)
    else:
        update_ligand_names.append(n)
df["ligand"] = update_ligand_names
ligands = sorted(set(df["ligand"].tolist()))
ligands_labelled = sorted(set(df.dropna(subset=["y_real"])["ligand"].tolist()))


app = Dash(__name__)
app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                ligands,
                ligands_labelled[0],
                id='ligand_iupac_name'
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

    ]),

    dcc.Graph(id='indicator-graphic'),

])


@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('ligand_iupac_name', 'value'),
    )
def update_graph(ligand_iupac_name):
    dff = df[df["ligand"] == ligand_iupac_name]

    x = dff["amount"]
    y = dff["mean"]
    ye = dff["std"]


    fig = px.scatter(x=x, y=y, error_y=ye,)

    if ligand_iupac_name in ligands_labelled:
        yreal = dff["y_real"]
        fig.add_trace(go.Scatter(x=x, y=yreal, name="experimental", mode="markers"))

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    fig.update_xaxes(title="Ligand Amount (uL * M)",)

    fig.update_yaxes(title="Figure of Merit (a.u.)",)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)