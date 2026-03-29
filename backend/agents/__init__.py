from .scout import ScoutAgent
from .creative import CreativeAgent
from .scorer import ScorerAgent
from .optimizer import OptimizerAgent
from .deployer import DeployerAgent
from .learner import LearnerAgent

ALL_AGENTS = {
    "scout": ScoutAgent,
    "creative": CreativeAgent,
    "scorer": ScorerAgent,
    "optimizer": OptimizerAgent,
    "deployer": DeployerAgent,
    "learner": LearnerAgent,
}
