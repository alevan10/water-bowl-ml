FROM levan.home:5000/datarobot/datarobot/datarobot-portable-prediction-api:latest
ARG MODEL_PACKAGE
USER root
COPY $MODEL_PACKAGE /opt/ml/model/model.mlpkg
RUN chown -R 4093 /opt/ml/model/
USER 4093
ENTRYPOINT ["bin/_portable_prediction_server.sh"]
