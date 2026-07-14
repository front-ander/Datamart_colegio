import pandas as pd
from ETL_colegio import MYSQL_CONFIG, connect_with_retry

mysql_url = f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}"
engine = connect_with_retry(mysql_url)

print("--- ASIGNACIONES PROFESOR ---")
print(pd.read_sql('SHOW COLUMNS FROM asignaciones_profesor', engine))
