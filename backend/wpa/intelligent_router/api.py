from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any
import pandas as pd
import joblib
from io import BytesIO

from backend.core.state_store import get_state_store, StateStore, ModelScoreboardModel

router = APIRouter(tags=["WPA - Intelligent Router"])

# In-memory cache for loaded models to avoid downloading from MinIO on every request
MODEL_CACHE: Dict[str, Any] = {}

@router.post("/predict")
async def intelligent_predict(
    input_data: List[Dict[str, Any]] = Body(...),
    state_store: StateStore = Depends(get_state_store)
):
    """
    Dynamically selects the best model from the scoreboard, loads it,
    and performs a prediction.
    """
    db = state_store.SessionLocal()
    try:
        # 1. Select the best model from the scoreboard
        best_model_entry = db.query(ModelScoreboardModel).order_by(ModelScoreboardModel.composite_score.desc()).first()
        if not best_model_entry:
            raise HTTPException(status_code=404, detail="No models found in the scoreboard.")

        model_path = best_model_entry.artifact_path
        model_key = best_model_entry.model_key

        # 2. Load model (with caching)
        if model_key not in MODEL_CACHE:
            print(f"Model '{model_key}' not in cache. Loading from storage...")
            try:
                # The artifact path in scoreboard is the zip path. We need to extract the joblib.
                # For simplicity here, we assume a direct joblib path. A real implementation
                # would unzip this. Let's adjust the path for this example.
                joblib_path = model_path.replace(".zip", "/pipeline.joblib").replace("exporter/", "exported_models/")

                response = state_store.s3_client.get_object(Bucket="sadi", Key=joblib_path)
                model_bytes = BytesIO(response['Body'].read())
                MODEL_CACHE[model_key] = joblib.load(model_bytes)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load model artifact: {e}")

        pipeline = MODEL_CACHE[model_key]

        # 3. Perform prediction
        input_df = pd.DataFrame(input_data)
        try:
            predictions = pipeline.predict(input_df)
            return {"predictions": predictions.tolist()}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error during prediction: {e}")

    finally:
        db.close()
