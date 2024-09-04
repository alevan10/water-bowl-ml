FROM python:3.11
WORKDIR /opt/predictions
COPY src/prediction_api prediction_api/
ENV PYTHONPATH "/opt/predictions:/opt/predictions/prediction_api"
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "prediction_api.app:app", "--host", "0.0.0.0", "--port", "80"]
