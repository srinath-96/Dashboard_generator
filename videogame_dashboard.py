import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
# import os # Add os import for potential path handling if needed by generated code itself

# Load the dataset
df = pd.read_csv(r'/Users/srinathmurali/Desktop/Dashboard_Gen/vgchartz-2024.csv') # Use raw string literal r'' for path compatibility

# Data Preprocessing
df = df.dropna(subset=['console'])
df = df[df['console'].isin(['PS2', 'PS3', 'PS4'])]
df['critic_score'] = pd.to_numeric(df['critic_score'], errors='coerce')
# df['user_score'] = pd.to_numeric(df['user_score'], errors='coerce')

# Calculate total sales
sales_cols = ['na_sales', 'eu_sales', 'jp_sales', 'other_sales']
available_cols = [col for col in sales_cols if col in df.columns]
df['total_sales'] = df[available_cols].sum(axis=1)

# Identify top 5 publishers
top_publishers = df.groupby('publisher')['total_sales'].sum().nlargest(5).index.tolist()
df_filtered = df[df['publisher'].isin(top_publishers)]


app = dash.Dash(__name__)
server = app.server

# PlayStation-themed color scheme
colors = {
    'background': '#003791',
    'text': '#FFFFFF',
    'accent': '#0070F0'
}

app.layout = html.Div(style={'backgroundColor': colors['background'], 'color': colors['text']}, children=[
    html.H1(children='Sony PlayStation Game Sales Dashboard',
            style={'textAlign': 'center', 'color': colors['text']}),

    html.Div([
        dcc.Graph(id='sales-comparison', style={'width': '100%', 'display': 'inline-block'}),
    ]),

    html.Div([
        dcc.Graph(id='top-publishers', style={'width': '100%', 'display': 'inline-block'}),
    ]),

    html.Div([
        dcc.Dropdown(
            id='publisher-dropdown',
            options=[{'label': publisher, 'value': publisher} for publisher in top_publishers],
            value=top_publishers[0] if top_publishers else None,
            style={'width': '50%', 'color': 'black'}
        ),
        dcc.Graph(id='best-selling-games', style={'width': '100%', 'display': 'inline-block'}),
    ]),

    html.Div([
        dcc.Graph(id='critic-vs-sales', style={'width': '100%', 'display': 'inline-block'}),
    ]),

    html.Div([
        dcc.Graph(id='regional-sales', style={'width': '100%', 'display': 'inline-block'}),
    ])
])

@app.callback(
    Output('sales-comparison', 'figure'),
    Input('sales-comparison', 'id')
)
def update_sales_comparison(id):
    sales_by_console = df.groupby('console')['total_sales'].sum().reset_index()
    fig = px.bar(sales_by_console, x='console', y='total_sales',
                 title='Sales Comparison Across Sony Platforms',
                 labels={'console': 'Console', 'total_sales': 'Total Sales (Millions)'},
                 color_discrete_sequence=[colors['accent']])
    fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])
    return fig

@app.callback(
    Output('top-publishers', 'figure'),
    Input('top-publishers', 'id')
)
def update_top_publishers(id):
    publisher_sales = df.groupby('publisher')['total_sales'].sum().nlargest(5).reset_index()
    fig = px.bar(publisher_sales, x='publisher', y='total_sales',
                 title='Top 5 Publishers for Sony Consoles',
                 labels={'publisher': 'Publisher', 'total_sales': 'Total Sales (Millions)'},
                 color_discrete_sequence=[colors['accent']])
    fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])
    return fig

@app.callback(
    Output('best-selling-games', 'figure'),
    Input('publisher-dropdown', 'value')
)
def update_best_selling_games(selected_publisher):
    publisher_df = df_filtered[df_filtered['publisher'] == selected_publisher].nlargest(5, 'total_sales')

    if publisher_df.empty:
        return go.Figure(data=[go.Scatter(x=[], y=[])],
                           layout=go.Layout(title=f"No data for {selected_publisher}",
                                             plot_bgcolor=colors['background'],
                                             paper_bgcolor=colors['background'],
                                             font_color=colors['text']))
    fig = px.bar(publisher_df, x='title', y='total_sales',
                 title=f'Top 5 Best-Selling Games by {selected_publisher}',
                 labels={'title': 'Game Title', 'total_sales': 'Total Sales (Millions)'},
                 color_discrete_sequence=[colors['accent']])
    fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])
    return fig

@app.callback(
    Output('critic-vs-sales', 'figure'),
    Input('critic-vs-sales', 'id')
)
def update_critic_vs_sales(id):
    valid_scores_df = df_filtered.dropna(subset=['critic_score', 'total_sales'])
    if valid_scores_df.empty:
        return go.Figure(data=[go.Scatter(x=[], y=[])],
                           layout=go.Layout(title="No data available for Critic Scores vs. Sales",
                                             plot_bgcolor=colors['background'],
                                             paper_bgcolor=colors['background'],
                                             font_color=colors['text']))
    fig = px.scatter(valid_scores_df, x='critic_score', y='total_sales',
                     title='Critic Scores vs. Sales',
                     labels={'critic_score': 'Critic Score', 'total_sales': 'Total Sales (Millions)'},
                     color='console', color_discrete_sequence=[colors['accent'], '#66B2FF', '#99D6FF'])
    fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])

    return fig

@app.callback(
    Output('regional-sales', 'figure'),
    Input('regional-sales', 'id')
)
def update_regional_sales(id):
    regional_sales = df_filtered[available_cols].sum().reset_index()
    regional_sales.columns = ['region', 'sales']
    fig = px.pie(regional_sales, values='sales', names='region',
                 title='Regional Sales Distribution',
                 color_discrete_sequence=[colors['accent'], '#66B2FF', '#99D6FF', '#CCE6FF'])
    fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])
    return fig

if __name__ == '__main__':
    app.run(debug=True)