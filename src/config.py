import dataclasses

from rltools.config import Config

Layers = tuple[int, ...]

# TODO: LayerNorm, ensemble, symmetric sampling. 2302.02948


@dataclasses.dataclass
class CoderConfig(Config):
    # BYOL
    # https://github.com/deepmind/deepmind-research/blob/master/byol/configs/byol.py
    shift: int = 4
    byol_batch_size: int = 32
    byol_learning_rate: float = 1e-3
    byol_targets_update: float = 5e-3
    byol_steps: int = 1000

    # DrQ-like
    # https://github.com/facebookresearch/drqv2/blob/main/cfgs/config.yaml
    gamma: float = .98
    lambda_: float = 1.
    utd: int = 10
    detach_encoder: bool = True
    drq_batch_size: int = 32
    drq_learning_rate: float = 1e-3
    drq_targets_update: float = 1e-2
    log_every: int = 5
    pretrain_steps: int = 40

    # Architecture
    activation: str = 'relu'
    normalization: str = 'layer'

    cnn_emb_dim: int = 64
    cnn_depths: Layers = (64, 64, 64, 64)
    cnn_kernels: Layers = (3, 3, 3, 3)
    cnn_strides: Layers = (2, 2, 2, 2)
    critic_layers: Layers = (64, 64, 64)
    ensemble_size: int = 2

    # Train common
    jit: bool = True
    replay_capacity: int = 10_000
    max_grad: float = 50.
    weight_decay: float = 1e-6

    logdir: str = 'logdir'
    task: str = 'test'
    time_limit: int = 1
    seed: int = 0
