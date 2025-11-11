import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# === Dados de exemplo ===
data = {
    'Category': [
        'Fresh Packaged', 'Healthy Beverage', 'Fresh Packaged', 'Organic Pet', 'Organic Beauty',
        'Healthy', 'Organic Frozen', 'Organic Baby', 'Organic Frozen', 'Healthy',
        'Healthy', 'Healthy Beverage'
    ],
    'SKU': [
        'FP2020', 'HB1016', 'FP3055', 'OP8025', 'OY2545',
        'HT2054', 'OF1060', 'OB1265', 'OF2035', 'HT1064',
        'HT1045', 'HB0156'
    ],
    'Perish/Non': [
        'Non-Perishable', 'Non-Perishable', 'Non-Perishable', 'Perishable', 'Perishable',
        'Non-Perishable', 'Perishable', 'Perishable', 'Perishable', 'Non-Perishable',
        'Non-Perishable', 'Non-Perishable'
    ],
    'Available': [
        4063, 4974, 2032, 2073, 4250,
        350, 420, 130, 358, 438,
        294, 331
    ],
    'Demand': [
        4493, 2578, 2574, 2424, 1795,
        410, 367, 346, 316, 301,
        285, 212
    ]
}

df = pd.DataFrame(data)
df['Diff_%'] = ((df['Available'] - df['Demand']) / df['Demand']) * 100

# === Inicializa o app ===
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Inventory & Demand Dashboard"

# === Layout ===
app.layout = dbc.Container([
    html.H2("Inventory & Demand Dashboard", className="text-center mt-4 mb-4"),

    # KPIs
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Avg Overstock", className="card-title"),
                html.H3(id="avg-overstock", className="text-success")
            ])
        ], color="light", outline=True), width=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Avg Stockout", className="card-title"),
                html.H3(id="avg-stockout", className="text-danger")
            ])
        ], color="light", outline=True), width=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Mean Diff%", className="card-title"),
                html.H3(id="avg-diff", className="text-primary")
            ])
        ], color="light", outline=True), width=4),
    ], className="mb-4"),

    # Filtro
    dbc.Row([
        dbc.Col([
            html.Label("Select Category:"),
            dcc.Dropdown(
                id='category-filter',
                options=[{'label': c, 'value': c} for c in df['Category'].unique()],
                value=None,
                placeholder="All Categories",
                multi=True
            )
        ], width=4),
    ], justify="center"),

    # Heatmap + Alertas
    dbc.Row([
        dbc.Col([dcc.Graph(id='heatmap')], width=7),
        dbc.Col([
            html.H5("📢 Inventory Alerts"),
            html.Div(id='alerts-box', style={
                'border': '1px solid #ddd',
                'borderRadius': '10px',
                'padding': '10px',
                'backgroundColor': '#f9f9f9',
                'height': '400px',
                'overflowY': 'auto'
            })
        ], width=5)
    ]),

    # Gráfico temporal
    dbc.Row([
        dbc.Col([
            html.H5("Demand Trend"),
            dcc.Graph(id="trend-graph", style={'height': '400px'})
        ])
    ])
], fluid=True)


# === Callback principal ===
@app.callback(
    [Output('heatmap', 'figure'),
     Output('alerts-box', 'children'),
     Output('avg-overstock', 'children'),
     Output('avg-stockout', 'children'),
     Output('avg-diff', 'children'),
     Output('trend-graph', 'figure')],
    [Input('category-filter', 'value')]
)
def update_dashboard(selected_categories):
    filtered_df = df.copy()
    if selected_categories:
        filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]

    # Resumo por categoria
    summary = filtered_df.groupby('Category')[['Available', 'Demand', 'Diff_%']].mean().sort_values('Diff_%', ascending=False)

    # Heatmap (vermelho "Crest-style")
    fig_heat = px.imshow(
        summary.T,
        color_continuous_scale=[
            (0.0, "#fff5f0"),
            (0.3, "#fcbba1"),
            (0.6, "#fb6a4a"),
            (1.0, "#cb181d")
        ],
        aspect='auto',
        text_auto=".1f"
    )
    fig_heat.update_layout(
        title="Inventory vs Demand (Average Values)",
        xaxis_title="Category",
        yaxis_title="Metrics",
        height=500
    )

    # Simulação de tendência temporal
    np.random.seed(0)
    categories = filtered_df['Category'].unique()
    trend_data = []
    for c in categories:
        dates = pd.date_range('2024-01-01', periods=12, freq='M')
        demand = np.random.randint(50, 200, size=12)
        trend_data.extend([(c, d, v) for d, v in zip(dates, demand)])
    trend_df = pd.DataFrame(trend_data, columns=['Category', 'Date', 'Demand'])

    fig_trend = px.line(
        trend_df, x='Date', y='Demand', color='Category',
        title="Monthly Demand Trend",
        height=400
    )

    # KPIs
    avg_diff = filtered_df['Diff_%'].mean()
    avg_overstock = filtered_df.loc[filtered_df['Diff_%'] > 25, 'Diff_%'].mean()
    avg_stockout = filtered_df.loc[filtered_df['Diff_%'] < -5, 'Diff_%'].mean()

    # Alertas
    alerts = []
    for category, row in summary.iterrows():
        diff = row['Diff_%']
        if diff > 25:
            alerts.append(html.P(f"⚠️ {category}: Overstock detected (+{diff:.1f}%).", style={'color': 'darkorange'}))
        elif diff < -5:
            alerts.append(html.P(f"🚨 {category}: Stockout risk ({diff:.1f}%).", style={'color': 'red'}))
        else:
            alerts.append(html.P(f"✅ {category}: Optimal inventory ({diff:.1f}%).", style={'color': 'green'}))

    return (
        fig_heat,
        alerts,
        f"{avg_overstock:.1f}%" if not pd.isna(avg_overstock) else "—",
        f"{avg_stockout:.1f}%" if not pd.isna(avg_stockout) else "—",
        f"{avg_diff:.1f}%" if not pd.isna(avg_diff) else "—",
        fig_trend
    )


# === Executa app ===
if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    import os

    # Render ou outra nuvem define a porta em uma variável de ambiente
    port = int(os.environ.get("PORT", 8050))

    # host="0.0.0.0" permite acesso externo (necessário para deploy)
    app.run_server(host="0.0.0.0", port=port, debug=False)
