FROM levan.home:5000/datarobot/datarobot/datarobot-portable-prediction-api:latest

USER root
COPY model_65f73bcadfa2eef464dcd0bc.mlpkg /opt/ml/model/model_65f73bcadfa2eef464dcd0bc.mlpkg
RUN chown -R 4093 /opt/ml/model/
USER 4093
ENTRYPOINT ["bin/_portable_prediction_server.sh"]
