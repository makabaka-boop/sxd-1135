import pandas as pd
import io
import base64
from typing import Tuple, Optional


def parse_uploaded_file(contents: str, filename: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    if contents is None:
        return None, '未选择文件'
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, '不支持的文件格式，请上传 CSV 或 Excel 文件'
        
        required_cols = ['日期', '成本类型', '项目', '金额', '栏区', '责任组']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return None, f'缺少必要列: {", ".join(missing_cols)}'
        
        if 'id' not in df.columns:
            df.insert(0, 'id', [f'COST-{i+1:04d}' for i in range(len(df))])
        
        if '备注' not in df.columns:
            df['备注'] = ''
        
        if '状态' not in df.columns:
            df['状态'] = '正常'
        
        if '是否异常' not in df.columns:
            df['是否异常'] = df['金额'].apply(
                lambda x: '是' if x > 12000 else '否'
            )
            df.loc[(df['成本类型'] == '维修') & (df['金额'] > 5000), '是否异常'] = '是'
            df.loc[df['是否异常'] == '是', '状态'] = '待复核'
        
        return df, None
        
    except Exception as e:
        return None, f'文件解析失败: {str(e)}'


def dataframe_to_records(df: pd.DataFrame) -> list:
    return df.to_dict('records')


def records_to_dataframe(records: list) -> pd.DataFrame:
    return pd.DataFrame(records)


def validate_row(row: dict) -> Tuple[bool, str]:
    if not row.get('日期'):
        return False, '日期不能为空'
    if not row.get('成本类型'):
        return False, '成本类型不能为空'
    if not row.get('项目'):
        return False, '项目不能为空'
    try:
        amount = float(row.get('金额', 0))
        if amount < 0:
            return False, '金额不能为负数'
    except (ValueError, TypeError):
        return False, '金额必须是数字'
    return True, ''


def detect_abnormal(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['是否异常'] = '否'
    df.loc[df['金额'] > 12000, '是否异常'] = '是'
    df.loc[(df['成本类型'] == '维修') & (df['金额'] > 5000), '是否异常'] = '是'
    df.loc[df['是否异常'] == '是', '状态'] = df['状态'].apply(
        lambda x: '待复核' if x == '正常' else x
    )
    return df
