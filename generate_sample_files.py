import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

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


def generate_sample_excel(output_dir='examples'):
    os.makedirs(output_dir, exist_ok=True)
    
    np.random.seed(42)
    base_date = datetime(2024, 1, 1)
    
    n_rows = 120
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
        
        remark = np.random.choice(REMARKS_POOL) if np.random.random() > 0.3 else ''
        
        data.append({
            '日期': date.strftime('%Y-%m-%d'),
            '成本类型': cost_type,
            '项目': item,
            '金额': amount,
            '栏区': np.random.choice(BARNS),
            '责任组': np.random.choice(RESPONSIBLE_GROUPS),
            '备注': remark,
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values('日期', ascending=False).reset_index(drop=True)
    
    excel_path = os.path.join(output_dir, '养殖场成本明细示例.xlsx')
    csv_path = os.path.join(output_dir, '养殖场成本明细示例.csv')
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='成本明细')
        
        workbook = writer.book
        worksheet = writer.sheets['成本明细']
        
        column_widths = {
            '日期': 12,
            '成本类型': 10,
            '项目': 15,
            '金额': 12,
            '栏区': 8,
            '责任组': 8,
            '备注': 40,
        }
        for i, col in enumerate(df.columns):
            worksheet.column_dimensions[chr(65 + i)].width = column_widths.get(col, 15)
    
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f'✅ 示例文件已生成:')
    print(f'   Excel: {excel_path}')
    print(f'   CSV: {csv_path}')
    print(f'   共 {len(df)} 条记录')


if __name__ == '__main__':
    generate_sample_excel()
