## DataBase
## Start
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 設定 MSSQL 連線
export MSSQL_HOST="你的MSSQL IP"
export MSSQL_PORT="1433"
export MSSQL_DB="ecommerce_chaos"
export MSSQL_USER="sa"
export MSSQL_PWD="YourStrong!Passw0rd"

# 設定 Instana Agent
export INSTANA_AGENT_HOST="你的_instana_agent_host"
export INSTANA_AGENT_PORT="42699"
export INSTANA_SERVICE_NAME=EcommerceDemo
# 啟動
python wsgi.py