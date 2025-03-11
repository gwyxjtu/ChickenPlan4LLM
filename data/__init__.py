import json
from module.utils import PROJECT_PATH

with open(PROJECT_PATH + "/data/device_set/ggp_knowledge_set.json", "r", encoding="utf-8") as f:
    ggp_knowledge = json.load(f)
with open(PROJECT_PATH + "/data/device_set/device_knowledge.json", "r", encoding="utf-8") as f:
    device_knowledge = json.load(f)
with open(PROJECT_PATH + "/data/device_set/load_knowledge_set.json", "r", encoding="utf-8") as f:
    load_knowledge = json.load(f)

__all__ = [
    "ggp_knowledge",
    "device_knowledge",
    "load_knowledge",
]
