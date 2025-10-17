import os, pyodbc
from dotenv import load_dotenv
load_dotenv()

DRIVER=os.getenv("MSSQL_DRIVER","ODBC Driver 18 for SQL Server")
SERVER=os.getenv("MSSQL_SERVER",r"(localdb)\MSSQLLocalDB")
DATABASE=os.getenv("MSSQL_DATABASE","Constructora")
ENCRYPT=os.getenv("MSSQL_ENCRYPT","no")
TRUST=os.getenv("MSSQL_TRUST_SERVER_CERTIFICATE","yes")

conn = pyodbc.connect(
    f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};"
    f"Trusted_Connection=Yes;Encrypt={ENCRYPT};TrustServerCertificate={TRUST};"
)
cur = conn.cursor()
cur.execute("SELECT 1")
print(cur.fetchone())
conn.close()
