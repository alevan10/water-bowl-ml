FROM python:3.12
WORKDIR /opt/predictions
COPY src/prediction_api prediction_api/
ENV PYTHONPATH "/opt/predictions:/opt/predictions/prediction_api"
RUN pip install --no-cache-dir -r api-requirements.txt
CMD ["uvicorn", "prediction_api.app:app", "--host", "0.0.0.0", "--port", "8082"]
