from dash import Input, Output, State, callback, no_update, html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import io
from datetime import datetime
from src.utils.session_cache import session_cache
from src.utils.data_processor import (
    parse_uploaded_file, dataframe_to_records, records_to_dataframe,
    detect_abnormal, validate_row
)
from src.data.sample_data import generate_sample_data, get_default_col_widths
from src.components.charts import (
    create_cost_composition_chart, create_abnormal_cost_chart,
    create_responsibility_group_chart, create_summary_cards
)
from src.components.editable_table import create_editable_table


def register_callbacks(app):
    
    @app.callback(
        Output('session-id', 'data'),
        Input('session-id', 'data'),
    )
    def init_session(session_id):
        if session_id is None:
            session_id = session_cache.create_session()
            sample_df = generate_sample_data()
            session_cache.update_data(session_id, dataframe_to_records(sample_df))
            session_cache.update_column_widths(session_id, get_default_col_widths())
        return session_id
    
    @app.callback(
        [Output('current-data', 'data'),
         Output('upload-status', 'children')],
        [Input('upload-data', 'contents'),
         Input('add-row-btn', 'n_clicks')],
        [State('upload-data', 'filename'),
         State('current-data', 'data'),
         State('session-id', 'data')],
        prevent_initial_call=False,
    )
    def handle_data_update(contents, add_clicks, filename, current_data, session_id):
        ctx = list(callback_context.triggered_prop_ids.values())[0] if callback_context.triggered_prop_ids else None
        
        if session_id is None:
            return no_update, ''
        
        if ctx == 'upload-data':
            if contents is None:
                return no_update, ''
            df, error = parse_uploaded_file(contents, filename)
            if error:
                return no_update, html.Span(error, className='text-danger')
            records = dataframe_to_records(df)
            session_cache.update_data(session_id, records)
            return records, html.Span(f'✅ 已加载 {len(df)} 条记录', className='text-success')
        
        if ctx == 'add-row-btn':
            existing_records = session_cache.get_data(session_id) or []
            new_id = f'COST-{len(existing_records)+1:04d}'
            new_row = {
                'id': new_id,
                '日期': datetime.now().strftime('%Y-%m-%d'),
                '成本类型': '饲料',
                '项目': '新增项目',
                '金额': 0,
                '栏区': '栏区1',
                '责任组': 'A组',
                '备注': '',
                '状态': '正常',
                '是否异常': '否',
            }
            existing_records.insert(0, new_row)
            session_cache.update_data(session_id, existing_records)
            return existing_records, html.Span(f'✅ 已添加新行', className='text-success')
        
        if current_data is None:
            sample_df = generate_sample_data()
            records = dataframe_to_records(sample_df)
            session_cache.update_data(session_id, records)
            return records, ''
        
        return current_data, ''
    
    @app.callback(
        Output('table-container', 'children'),
        [Input('current-data', 'data'),
         Input('filter-abnormal-switch', 'value'),
         Input('reset-col-widths-btn', 'n_clicks'),
         Input('role-selector', 'value')],
        [State('session-id', 'data')],
    )
    def update_table(data, filter_abnormal, reset_clicks, role, session_id):
        if data is None or session_id is None:
            return html.Div('加载中...')
        
        ctx = callback_context.triggered_id
        
        col_widths = session_cache.get_column_widths(session_id) or get_default_col_widths()
        if ctx == 'reset-col-widths-btn':
            col_widths = get_default_col_widths()
            session_cache.update_column_widths(session_id, col_widths)
        
        df = records_to_dataframe(data)
        if filter_abnormal:
            df = df[df['是否异常'] == '是']
        
        records = dataframe_to_records(df)
        table = create_editable_table('main-table', records, col_widths)
        
        if role == 'executor':
            for col in table.columnDefs:
                if col['field'] not in ['备注', '栏区', '责任组']:
                    col['editable'] = False
        elif role == 'reviewer':
            for col in table.columnDefs:
                if col['field'] not in ['状态', '备注']:
                    col['editable'] = False
        
        return table
    
    @app.callback(
        [Output('current-data', 'data', allow_duplicate=True),
         Output('save-status', 'children'),
         Output('save-status', 'className')],
        Input('main-table', 'cellValueChanged'),
        State('main-table', 'rowData'),
        State('session-id', 'data'),
        prevent_initial_call=True,
    )
    def handle_cell_edit(changed, row_data, session_id):
        if row_data is None or session_id is None:
            return no_update, '', ''
        
        df = records_to_dataframe(row_data)
        df = detect_abnormal(df)
        records = dataframe_to_records(df)
        session_cache.update_data(session_id, records)
        
        return records, '✅ 已自动保存', 'mt-2 text-success'
    
    @app.callback(
        Output('main-table', 'columnState'),
        Input('main-table', 'columnState'),
        State('session-id', 'data'),
        prevent_initial_call=True,
    )
    def save_column_widths(column_state, session_id):
        if column_state is None or session_id is None:
            return no_update
        
        widths = {}
        for col in column_state:
            if 'colId' in col and 'width' in col:
                widths[col['colId']] = col['width']
        
        if widths:
            session_cache.update_column_widths(session_id, widths)
        
        return no_update
    
    @app.callback(
        [Output('summary-cards-container', 'children'),
         Output('cost-composition-chart', 'figure'),
         Output('abnormal-cost-chart', 'figure'),
         Output('responsibility-group-chart', 'figure')],
        Input('current-data', 'data'),
    )
    def update_charts(data):
        if data is None:
            return [], {}, {}, {}
        
        df = records_to_dataframe(data)
        
        cards = create_summary_cards(df)
        fig1 = create_cost_composition_chart(df)
        fig2 = create_abnormal_cost_chart(df)
        fig3 = create_responsibility_group_chart(df)
        
        return cards, fig1, fig2, fig3
    
    @app.callback(
        Output('download-dataframe-xlsx', 'data'),
        Input('export-btn', 'n_clicks'),
        State('current-data', 'data'),
        prevent_initial_call=True,
    )
    def export_excel(n_clicks, data):
        if data is None:
            return no_update
        
        df = records_to_dataframe(data)
        
        def generate_xlsx():
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='成本明细')
                
                workbook = writer.book
                worksheet = writer.sheets['成本明细']
                
                for i, col in enumerate(df.columns):
                    max_len = max(
                        df[col].astype(str).map(len).max(),
                        len(str(col))
                    )
                    worksheet.column_dimensions[chr(65 + i)].width = min(max_len + 2, 50)
            
            return output.getvalue()
        
        return dcc.send_bytes(
            generate_xlsx,
            f'养殖场成本明细_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )


from dash import callback_context
