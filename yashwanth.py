import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load the CSV file
df = pd.read_csv('yashwanth123.csv')

# Create a dictionary to map month names to numeric values
month_dict = {
    'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
    'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'
}

# Replace month names with numeric values
df['Month'] = df['Month'].map(month_dict)

# Convert 'Year' and 'Month' to datetime for time series analysis
df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'], format='%Y-%m')

# Create Dash app
app = dash.Dash(__name__)

# Define app layout
app.layout = html.Div([
    html.H1('Tourism Insights in India Dashboard', style={'textAlign': 'center', 'margin-bottom': '40px'}),

    # Dropdowns for Year, State, and Purpose of Visit
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())],
                value=df['Year'].min(),
                multi=False,
                style={'width': '100%'}
            )
        ], className='four columns'),

        html.Div([
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': state, 'value': state} for state in sorted(df['State/UT'].unique())],
                value=df['State/UT'].iloc[0],
                multi=False,
                style={'width': '100%'}
            )
        ], className='four columns'),

        html.Div([
            dcc.Dropdown(
                id='purpose-dropdown',
                options=[{'label': purpose, 'value': purpose} for purpose in sorted(df['Purpose of Visit'].unique())],
                value=df['Purpose of Visit'].iloc[0],
                multi=False,
                style={'width': '100%'}
            )
        ], className='four columns')
    ], className='row', style={'margin': '20px 0'}),

    # Graphs
    html.Div([
        dcc.Graph(id='revenue-growth', style={'height': '400px'}),
        dcc.Graph(id='tourist-arrival', style={'height': '400px'}),
        dcc.Graph(id='tourism-category-pie', style={'height': '400px'})
    ])
])

# Callback to update graphs based on dropdown selections
@app.callback(
    [Output('revenue-growth', 'figure'),
     Output('tourist-arrival', 'figure'),
     Output('tourism-category-pie', 'figure')],
    [Input('year-dropdown', 'value'),
     Input('state-dropdown', 'value'),
     Input('purpose-dropdown', 'value')]
)
def update_graphs(selected_year, selected_state, selected_purpose):
    # Filter data based on selected dropdowns
    filtered_df = df[(df['Year'] == selected_year) & 
                     (df['State/UT'] == selected_state) & 
                     (df['Purpose of Visit'] == selected_purpose)]
    
    # Revenue Growth Bar Chart (Month-wise)
    revenue_growth = filtered_df.groupby(['Year', 'Month'])['Revenue (INR)'].sum().reset_index()
    revenue_growth['Month'] = revenue_growth['Month'].apply(lambda x: pd.to_datetime(f'{x}', format='%m').strftime('%B'))
    
    revenue_growth_fig = {
        'data': [{
            'x': revenue_growth['Month'],
            'y': revenue_growth['Revenue (INR)'],
            'type': 'bar',
            'name': 'Revenue Growth',
            'marker': {'color': 'royalblue'}
        }],
        'layout': {
            'title': 'Monthly Revenue Growth in India (INR)',
            'xaxis': {'title': 'Month', 'title_font': {'size': 14}, 'tickangle': 45},
            'yaxis': {'title': 'Revenue (INR)', 'title_font': {'size': 14}},
            'barmode': 'group',
            'plot_bgcolor': 'rgb(242, 242, 242)',
            'paper_bgcolor': 'rgb(255, 255, 255)',
            'font': {'family': 'Arial, sans-serif'}
        }
    }

    # Tourist Arrival Line Graph (Month-wise)
    tourist_arrival = filtered_df.groupby(['Year', 'Month'])['Tourist Count'].sum().reset_index()
    tourist_arrival['Month'] = tourist_arrival['Month'].apply(lambda x: pd.to_datetime(f'{x}', format='%m').strftime('%B'))
    
    tourist_arrival_fig = {
        'data': [{
            'x': tourist_arrival['Month'],
            'y': tourist_arrival['Tourist Count'],
            'type': 'line',
            'name': 'Tourist Arrival',
            'marker': {'color': 'green', 'size': 10}
        }],
        'layout': {
            'title': 'Monthly Tourist Arrival Trend in India',
            'xaxis': {'title': 'Month', 'title_font': {'size': 14}},
            'yaxis': {'title': 'Tourist Count', 'title_font': {'size': 14}},
            'plot_bgcolor': 'rgb(242, 242, 242)',
            'paper_bgcolor': 'rgb(255, 255, 255)',
            'font': {'family': 'Arial, sans-serif'}
        }
    }

    # Tourism Category Pie Chart
    tourism_category = filtered_df['Tourism Category'].value_counts().reset_index()
    tourism_category.columns = ['Tourism Category', 'Count']
    tourism_category_pie_fig = px.pie(tourism_category, names='Tourism Category', values='Count', 
                                      title='Tourism Categories Distribution')
    tourism_category_pie_fig.update_traces(
        textinfo='percent+label',
        marker=dict(colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0'])
    )

    return revenue_growth_fig, tourist_arrival_fig, tourism_category_pie_fig

if __name__ == '__main__':
    # Use port 8051 instead of 8050 to avoid address conflicts
    app.run_server(debug=True, port=8051)
