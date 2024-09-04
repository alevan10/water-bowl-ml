from prediction_api.models import ModelInfo


class DBModelInfo:
    __table_args__ = {"keep_existing": True}
    __mapper_args__ = {"eager_defaults": True}

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, DBModelInfo):
            return self.to_dict() == other.to_dict()
        return False

    def to_dict(self):
        return {
            "id": "deadbeef",
        }

    def to_api_return(self) -> ModelInfo:
        return ModelInfo(**self.to_dict())
