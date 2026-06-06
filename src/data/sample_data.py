import pandas as pd
import numpy as np
from datetime import datetime, timedelta

COST_TYPES = ['饲料', '人工', '维修', '转运']
BARNS = [f'栏区{i}' for i in range(1, 9)]
RESPONSIBLE_GROUPS = ['A组', 'B组', 'C组', 'D组']
FEED_TYPES = ['玉米', '豆粕', '麸皮', '预混料']
LABOR_TYPES = ['饲养员', '兽医', '清洁工', '技术员']
REPAIR_TYPES = ['设备维修', '栏舍维修', '水电维修', '工具更换']
TRANSPORT_TYPES = ['饲料运输', '生猪转运', '物资运输', '废弃物处理']

REMARKS_POOL = [
    '本月价格波动较大，供应商提价5%',
    '设备老化需更换零件，费用偏高',
    '雨季导致运输延误，产生额外费用',
    '临时加班人员费用',
    '季度性防疫物资采购',
    '栏舍消毒专项费用',
    '正常月度开支',
    '价格较上月下降，批量采购优惠',
    '应急维修，非计划内支出',
    '新进人员培训费用',
    '设备定期保养维护',
    '高温季节降温设施运行费用增加',
]


def generate_sample_data(n_rows=120):
    np.random.seed(42)
    base_date = datetime(2024, 1, 1)
    
    data = []
    for i in range(n_rows):
        cost_type = np.random.choice(COST_TYPES)
        days_offset = np.random.randint(0, 180)
        date = base_date + timedelta(days=days_offset)
        
        if cost_type == '饲料':
            item = np.random.choice(FEED_TYPES)
            amount = round(np.random.uniform(2000, 15000), 2)
        elif cost_type == '人工':
            item = np.random.choice(LABOR_TYPES)
            amount = round(np.random.uniform(3000, 20000), 2)
        elif cost_type == '维修':
            item = np.random.choice(REPAIR_TYPES)
            amount = round(np.random.uniform(500, 8000), 2)
        else:
            item = np.random.choice(TRANSPORT_TYPES)
            amount = round(np.random.uniform(800, 6000), 2)
        
        is_abnormal = amount > 12000 or (cost_type == '维修' and amount > 5000)
        
        remark = np.random.choice(REMARKS_POOL) if np.random.random() > 0.3 else ''
        if is_abnormal and not remark:
            remark = '费用异常偏高，需核实'
        
        data.append({
            'id': f'COST-{i+1:04d}',
            '日期': date.strftime('%Y-%m-%d'),
            '成本类型': cost_type,
            '项目': item,
            '金额': amount,
            '栏区': np.random.choice(BARNS),
            '责任组': np.random.choice(RESPONSIBLE_GROUPS),
            '备注': remark,
            '状态': '待复核' if is_abnormal else '正常',
            '是否异常': '是' if is_abnormal else '否',
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values('日期', ascending=False).reset_index(drop=True)
    return df


def get_column_defs():
    return [
        {'headerName': 'ID', 'field': 'id', 'width': 90, 'pinned': 'left', 'editable': False},
        {'headerName': '日期', 'field': '日期', 'width': 110, 'editable': True},
        {'headerName': '成本类型', 'field': '成本类型', 'width': 100, 'editable': True, 
         'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': COST_TYPES}},
        {'headerName': '项目', 'field': '项目', 'width': 130, 'editable': True},
        {'headerName': '金额', 'field': '金额', 'width': 120, 'editable': True, 
         'type': 'numericColumn', 'valueFormatter': {'function': "params.value ? '¥' + Number(params.value).toLocaleString() : ''"}},
        {'headerName': '栏区', 'field': '栏区', 'width': 90, 'editable': True,
         'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': BARNS}},
        {'headerName': '责任组', 'field': '责任组', 'width': 90, 'editable': True,
         'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': RESPONSIBLE_GROUPS}},
        {'headerName': '备注', 'field': '备注', 'width': 200, 'editable': True,
         'cellEditor': 'agLargeTextCellEditor',
         'cellEditorParams': {'maxLength': 500, 'rows': 6},
         'tooltipField': '备注',
         'autoHeight': True,
         'wrapText': True},
        {'headerName': '状态', 'field': '状态', 'width': 100, 'editable': True,
         'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': ['待复核', '已确认', '正常', '有异议']}},
        {'headerName': '是否异常', 'field': '是否异常', 'width': 90, 'editable': False},
    ]


def get_default_col_widths():
    return {
        'id': 90,
        '日期': 110,
        '成本类型': 100,
        '项目': 130,
        '金额': 120,
        '栏区': 90,
        '责任组': 90,
        '备注': 200,
        '状态': 100,
        '是否异常': 90,
    }
