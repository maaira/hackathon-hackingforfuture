from fastapi import FastAPI, HTTPException
from influxdb_client import InfluxDBClient, Point, Dialect
from influxdb_client.client.flux_table import FluxStructureEncoder
from influxdb_client.client.write_api import SYNCHRONOUS
from pydantic import BaseModel
import json
import os

app = FastAPI()

# Configurações do InfluxDB
url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
token = os.getenv("INFLUXDB_TOKEN", "YOUR_API_TOKEN")
org = os.getenv("INFLUXDB_ORG", "YOUR_ORG")
bucket = os.getenv("INFLUXDB_BUCKET", "your_bucket")

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

# Definição do modelo de entrada
class QueryModel(BaseModel):
    measurement: str
    start: str
    stop: str

@app.post("/gettimeline")
async def query_influxdb(query: QueryModel):
    flux_query = f'''
    from(bucket: "{bucket}")
        |> range(start: {query.start}, stop: {query.stop})
        |> filter(fn: (r) => r._measurement == "{query.measurement}")
    '''
    try:
        tables = query_api.query(flux_query, org=org)
        result = []
        for table in tables:
            for record in table.records:
                result.append({
                    "time": record.get_time(),
                    "value": record.get_value(),
                    "field": record.get_field(),
                    "tags": record.values
                })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)