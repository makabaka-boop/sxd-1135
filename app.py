import dash
import dash_bootstrap_components as dbc
from dash import html
from src.components.editable_table import get_layout as get_table_layout
from src.components.charts import get_layout as get_charts_layout
from src.callbacks import register_callbacks


app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    ],
    suppress_callback_exceptions=True,
    title='养殖场成本数据分析系统',
)

server = app.server

app.layout = dbc.Container([
    html.Div([
        dbc.Row([
            dbc.Col([
                html.H2(
                    [html.I(className='fas fa-tractor me-3 text-primary'),
                     '养殖场成本数据分析系统'],
                    className='text-center my-4',
                ),
                html.P(
                    '支持饲料、人工、维修、转运成本的明细修正与分析',
                    className='text-center text-muted mb-4',
                ),
            ]),
        ]),
        
        html.Hr(),
        
        get_table_layout(),
        
        html.Hr(),
        
        get_charts_layout(),
        
        html.Footer([
            html.Hr(),
            html.P(
                '© 2024 养殖场成本管理系统 | 会话内数据自动保存',
                className='text-center text-muted small',
            ),
        ]),
    ]),
], fluid=True, className='px-4 py-3')


register_callbacks(app)


if __name__ == '__main__':
    app.run(debug=False, port=8070, host='0.0.0.0')
