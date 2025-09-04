# hadolint ignore=DL3007
FROM levan.home:5000/datarobot/datarobot-portable-prediction-api:latest
ARG MODEL_PACKAGE
USER root
ENV PREDICTION_API_MODEL_REPOSITORY_PATH=/opt/ml/model/model.mlpkg
COPY $MODEL_PACKAGE /opt/ml/model/model.mlpkg
RUN chown -R 4093 /opt/ml/model/
USER 4093
ENTRYPOINT ["bin/_portable_prediction_server.sh"]
