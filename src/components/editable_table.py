from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
from src.data.sample_data import get_column_defs, get_default_col_widths


def create_editable_table(table_id: str, data: list = None, column_widths: dict = None):
    col_defs = get_column_defs()
    
    if column_widths:
        for col in col_defs:
            field = col['field']
            if field in column_widths:
                col['width'] = column_widths[field]
    
    default_col_def = {
        'resizable': True,
        'sortable': True,
        'filter': True,
        'minWidth': 60,
    }
    
    return dag.AgGrid(
        id=table_id,
        columnDefs=col_defs,
        rowData=data or [],
        defaultColDef=default_col_def,
        dashGridOptions={
            'editType': 'fullRow',
            'animateRows': True,
            'pagination': True,
            'paginationPageSize': 20,
            'domLayout': 'normal',
            'rowHeight': 48,
            'headerHeight': 48,
        },
        style={'height': '600px', 'width': '100%'},
        className='ag-theme-alpine',
        columnSize='responsiveSizeToFit',
        columnSizeOptions={
            'skipHeader': False,
            'columnLimits': [
                {'key': '备注', 'minWidth': 150, 'maxWidth': 500},
            ]
        },
        getRowStyle={
            'styleConditions': [
                {
                    'condition': "params.data['是否异常'] == '是'",
                    'style': {'backgroundColor': '#fff3cd'}
                },
                {
                    'condition': "params.data['状态'] == '待复核'",
                    'style': {'backgroundColor': '#f8d7da'}
                },
                {
                    'condition': "params.data['状态'] == '已确认'",
                    'style': {'backgroundColor': '#d1e7dd'}
                },
            ]
        },
        persisted_props=['columnState'],
        persistence_type='session',
    )


def get_layout():
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5('角色选择', className='mb-2'),
                    dbc.RadioItems(
                        id='role-selector',
                        options=[
                            {'label': '👔 管理者 - 上传明细', 'value': 'manager'},
                            {'label': '👷 执行者 - 补充备注', 'value': 'executor'},
                            {'label': '🔍 复核者 - 确认异常', 'value': 'reviewer'},
                        ],
                        value='executor',
                        inline=True,
                        className='mb-3',
                    ),
                ])
            ], width=12),
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('操作工具栏'),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.Upload(
                                    id='upload-data',
                                    children=dbc.Button(
                                        [html.I(className='fas fa-upload me-2'), '上传成本明细'],
                                        color='primary',
                                        id='upload-btn',
                                    ),
                                    multiple=False,
                                    accept='.csv,.xlsx,.xls',
                                ),
                            ], width='auto'),
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className='fas fa-download me-2'), '导出Excel'],
                                    color='success',
                                    id='export-btn',
                                    outline=True,
                                ),
                                dcc.Download(id='download-dataframe-xlsx'),
                            ], width='auto'),
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className='fas fa-sync me-2'), '重置列宽'],
                                    color='secondary',
                                    id='reset-col-widths-btn',
                                    outline=True,
                                ),
                            ], width='auto'),
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className='fas fa-plus me-2'), '添加行'],
                                    color='info',
                                    id='add-row-btn',
                                    outline=True,
                                ),
                            ], width='auto'),
                            dbc.Col([
                                dbc.Switch(
                                    id='filter-abnormal-switch',
                                    label='只显示异常',
                                    value=False,
                                    className='mt-2',
                                ),
                            ], width='auto'),
                            dbc.Col([
                                html.Div(id='upload-status', className='mt-2 text-muted'),
                            ]),
                        ]),
                    ]),
                ]),
            ], width=12),
        ], className='mb-3'),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className='fas fa-table me-2'),
                        '成本明细表 (可双击编辑，拖动列边框调整宽度)'
                    ]),
                    dbc.CardBody([
                        html.Div(id='table-container', className='table-container'),
                        html.Div(id='save-status', className='mt-2 text-success d-none'),
                    ]),
                ]),
            ], width=12),
        ], className='mb-4'),
        
        dcc.Store(id='session-id'),
        dcc.Store(id='current-data'),
        dcc.Store(id='column-widths-store'),
    ])
