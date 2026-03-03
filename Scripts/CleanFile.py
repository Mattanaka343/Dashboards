import pandas as pd

data = pd.read_csv('../Data/Raw/nurvai_stage_recordings.csv')

column_name_map = {
    'duration_sec': 'Duration(s)',
    'recorded_at': 'StartTime',
    'metadata.task_context.operator_code': 'Operator',
    'metadata.technical_report.quality_gate.is_valid': 'IsValid',
    'metadata.technical_report.quality_gate.reason':'FailReason',
    'station_id': 'Station',
    'metadata.task_context.skill_name': 'SkillName'
} 

data = data[list(column_name_map.keys())]
data = data.rename(columns=column_name_map)

for idx in range(data.shape[0]):
    entry = data.iloc[idx]
    if isinstance(entry['FailReason'], str) and 'TOO_SHORT' in entry['FailReason'].upper():
        data.loc[idx,'IsValid'] = False
    else:
        data.loc[idx,'IsValid'] = True

data.to_csv('../Data/Processed/general_data.csv',index=False)

