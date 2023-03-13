import dataclasses

from rltools.config import Config

Layers = tuple[int]

# TODO: LayerNorm, ensemble, symmetric sampling. 2302.02948


@dataclasses.dataclass
class CoderConfig(Config):
    # BYOL
    # https://github.com/deepmind/deepmind-research/blob/master/byol/configs/byol.py
    shift: int = 4
    byol_batch_size: int = 256
    byol_learning_rate: float = 1e-3
    byol_targets_update: float = 5e-3
    byol_steps: int = 100

    # DrQ
    # https://github.com/facebookresearch/drqv2/blob/main/cfgs/config.yaml
    gamma: float = .99
    utd: int = 2
    entropy_coef: float = 1e-2
    num_actions: int = 20
    detach_encoder: bool = False
    drq_batch_size: int = 256
    drq_learning_rate: float = 3e-4
    drq_targets_update: float = 5e-3
    drq_eval_every: int = 1000

    # Architecture
    activation: str = 'elu'
    normalization: str = 'rms'

    cnn_emb_dim: int = 256
    cnn_depths: Layers = (64, 64, 64, 64)
    cnn_kernels: Layers = (3, 3, 3, 3)
    cnn_strides: Layers = (2, 2, 2, 2)

    act_dim_nbins: int = 3
    actor_layers: Layers = (256, 256)
    critic_layers: Layers = (256, 256)
    ensemble_size: int = 10
    num_critics: int = 2

    # Train common
    buffer_capacity: int = 3e4
    max_grad: float = 10

    logdir: str = 'logdir/ur_pick'
    task: str = 'ur_pick'
    seed: int = 0
