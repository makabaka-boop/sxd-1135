from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


COLORS = {
    '饲料': '#4CAF50',
    '人工': '#2196F3',
    '维修': '#FF9800',
    '转运': '#9C27B0',
}


def create_cost_composition_chart(df: pd.DataFrame):
    if df is None or len(df) == 0:
        return go.Figure()
    
    cost_by_type = df.groupby('成本类型')['金额'].sum().reset_index()
    cost_by_type = cost_by_type.sort_values('金额', ascending=False)
    
    fig = go.Figure(data=[go.Pie(
        labels=cost_by_type['成本类型'],
        values=cost_by_type['金额'],
        hole=0.5,
        marker=dict(colors=[COLORS.get(t, '#999') for t in cost_by_type['成本类型']]),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>金额: ¥%{value:,.2f}<br>占比: %{percent}<extra></extra>',
    )])
    
    fig.update_layout(
        title='成本构成分析',
        showlegend=True,
        margin=dict(l=20, r=20, t=50, b=20),
        height=350,
    )
    
    return fig


def create_abnormal_cost_chart(df: pd.DataFrame):
    if df is None or len(df) == 0:
        return go.Figure()
    
    abnormal_df = df[df['是否异常'] == '是']
    
    if len(abnormal_df) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text='暂无异常费用',
            xref='paper', yref='paper',
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color='#999'),
        )
        fig.update_layout(height=350, title='异常费用分布')
        return fig
    
    abnormal_by_type = abnormal_df.groupby('成本类型')['金额'].agg(['sum', 'count']).reset_index()
    abnormal_by_type.columns = ['成本类型', '总金额', '异常笔数']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=abnormal_by_type['成本类型'],
        y=abnormal_by_type['总金额'],
        name='异常金额',
        marker_color='#e74c3c',
        hovertemplate='<b>%{x}</b><br>异常金额: ¥%{y:,.2f}<extra></extra>',
    ))
    
    fig.add_trace(go.Scatter(
        x=abnormal_by_type['成本类型'],
        y=abnormal_by_type['异常笔数'],
        name='异常笔数',
        yaxis='y2',
        mode='lines+markers',
        marker=dict(size=10, color='#f39c12'),
        line=dict(width=3),
        hovertemplate='<b>%{x}</b><br>异常笔数: %{y}<extra></extra>',
    ))
    
    fig.update_layout(
        title='异常费用分析',
        barmode='group',
        xaxis=dict(title='成本类型'),
        yaxis=dict(title='金额 (元)', side='left'),
        yaxis2=dict(title='笔数', side='right', overlaying='y', showgrid=False),
        legend=dict(orientation='h', y=-0.15),
        margin=dict(l=20, r=20, t=50, b=40),
        height=350,
    )
    
    return fig


def create_responsibility_group_chart(df: pd.DataFrame):
    if df is None or len(df) == 0:
        return go.Figure()
    
    group_data = df.groupby(['责任组', '成本类型'])['金额'].sum().reset_index()
    
    fig = px.bar(
        group_data,
        x='责任组',
        y='金额',
        color='成本类型',
        color_discrete_map=COLORS,
        barmode='group',
        title='各责任组成本对比',
    )
    
    fig.update_layout(
        xaxis_title='责任组',
        yaxis_title='金额 (元)',
        legend_title='成本类型',
        margin=dict(l=20, r=20, t=50, b=20),
        height=350,
        legend=dict(orientation='h', y=-0.15),
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>%{fullData.name}: ¥%{y:,.2f}<extra></extra>',
    )
    
    return fig


def create_summary_cards(df: pd.DataFrame):
    if df is None or len(df) == 0:
        total_amount = 0
        abnormal_count = 0
        total_rows = 0
        avg_amount = 0
    else:
        total_amount = df['金额'].sum()
        abnormal_count = len(df[df['是否异常'] == '是'])
        total_rows = len(df)
        avg_amount = df['金额'].mean()
    
    cards = [
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('总成本', className='card-subtitle mb-2 text-muted'),
                    html.H3(f'¥{total_amount:,.2f}', className='card-title text-primary'),
                ])
            ], className='text-center shadow-sm'),
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('记录总数', className='card-subtitle mb-2 text-muted'),
                    html.H3(f'{total_rows}', className='card-title text-success'),
                ])
            ], className='text-center shadow-sm'),
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('异常笔数', className='card-subtitle mb-2 text-muted'),
                    html.H3(f'{abnormal_count}', className='card-title text-danger'),
                ])
            ], className='text-center shadow-sm'),
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('平均金额', className='card-subtitle mb-2 text-muted'),
                    html.H3(f'¥{avg_amount:,.2f}', className='card-title text-warning'),
                ])
            ], className='text-center shadow-sm'),
        ], md=3),
    ]
    
    return dbc.Row(cards, className='mb-4')


def get_layout():
    return html.Div([
        html.Div(id='summary-cards-container'),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className='fas fa-chart-pie me-2'),
                        '成本构成'
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='cost-composition-chart', config={'displayModeBar': False}),
                    ]),
                ]),
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className='fas fa-exclamation-triangle me-2'),
                        '异常费用'
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='abnormal-cost-chart', config={'displayModeBar': False}),
                    ]),
                ]),
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className='fas fa-users me-2'),
                        '责任组对比'
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='responsibility-group-chart', config={'displayModeBar': False}),
                    ]),
                ]),
            ], md=4),
        ]),
    ])
