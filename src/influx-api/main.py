from fastapi import FastAPI, HTTPException, Query
from influxdb_client import InfluxDBClient, Point
import os
from influxdb_client import InfluxDBClient, Point, Dialect
from influxdb_client.client.flux_table import FluxStructureEncoder
from influxdb_client.client.write_api import SYNCHRONOUS
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Configurações do InfluxDB
url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
token = os.getenv("INFLUXDB_TOKEN", "qMlzq7OG1TBzJDSp6VCuWKjuwFqdmcnYsbJ72nvKvRaYq3L4E3GRkdk0IiH3i_iYsWi6PwVWyBNTsRCiyzbP_A==")
org = os.getenv("INFLUXDB_ORG", "my-org")
bucket = os.getenv("INFLUXDB_BUCKET", "3d-printer")
print(token)
client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
# Definição do modelo de entrada    
class QueryModel(BaseModel):
    measurement: str
    start: str
    stop: str
    bucket: str

@app.get("/gettimeline/")
async def query_influxdb(measurement: str = Query(..., description="Measurement name"),
    start: str = Query(..., description="Start time in ISO format"),
    stop: str = Query(..., description="Stop time in ISO format"),
    bucket : str = Query(..., description="Bucket inside InfluxDB")):
    flux_query = f'''
    from(bucket: "{bucket}")
        |> range(start: {start}, stop: {stop})
        |> filter(fn: (r) => r._measurement == "{measurement}")
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