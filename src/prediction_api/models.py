from pydantic import BaseModel


class ModelInfo(BaseModel):
    blueprintId: str
    featurelistId: str
    featurelistName: str
    id: str
    hasFinetuners: bool
    isAugmented: bool
    isFrozen: bool
    isStarred: bool
    isTrainedIntoHoldout: bool
    isTrainedIntoValidation: bool
    isTrainedOnGpu: bool
    lifecycle: dict
    linkFunction: str
    metrics: dict
    modelCategory: str
    modelFamily: str
    modelFamilyFullName: str
    modelNumber: int
    modelType: str
    monotonicDecreasingFeaturelistId: str
    monotonicIncreasingFeaturelistId: str
    parentModelid: str
    predictionThreshold: float
    predictionThresholdReadOnly: bool
    processes: list[str]
    projectId: str
    samplePct: float
    supportsComposableML: bool
    supportsMonotonicConstraints: bool
    trainingDuration: int
    trainingEndDate: str
    trainingRowCount: int
    trainingStartDate: str
    modelFileName: str

    class Config:
        orm_mode = True
