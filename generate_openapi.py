import json
from backend.app_factory import create_app

app = create_app()

openapi_schema = app.openapi()

with open("openapi.json", "w") as f:
    json.dump(openapi_schema, f, indent=2)

print("openapi.json generated successfully.")
