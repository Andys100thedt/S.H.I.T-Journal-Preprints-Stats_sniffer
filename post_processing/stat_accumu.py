import dataclasses

@dataclasses.dataclass
class StatFlowDataset:
    dataset: dict[str, list[StatFrame]]

@dataclasses.dataclass
class StatFrame:
    timestamp: float
    score_plain: float
    score_weighted: float
    rated_count: float

@dataclasses.dataclass
class IntegratedStatClue:
    latest_score_plain: float
    latest_score_weighted: float
    latest_rated_count: float
    variation_plain: float
    variation_weighted: float
    jump_rate_plain: float

@dataclasses.dataclass
class IntegratedDataset:
    dataset: dict[str, IntegratedStatClue]

@dataclasses.dataclass
class IntegratedStatResult:
    rising: float
    controversy: float
    hotness: float

@dataclasses.dataclass
class StatResultDatabase:
    database: dict[str, IntegratedStatResult]

_STATIC_FRAME = StatFrame(
    timestamp=-1,
    score_plain=0.0,
    score_weighted=3.7911405091200641,
    rated_count=0.0,
)