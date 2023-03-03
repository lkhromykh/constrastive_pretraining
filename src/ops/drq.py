import jax
import jax.numpy as jnp

import haiku as hk
import chex
import optax

from src.config import CoderConfig
from src.networks import CoderNetworks
from src.training_state import TrainingState
from .augmentations import augmentation_fn
from src import types_ as types


def drq(cfg: CoderConfig, networks: CoderNetworks):

    def critic_loss_fn(value, target_value):
        chex.assert_rank([value, target_value], [1, 0])
        target_value = jax.lax.stop_gradient(target_value)
        return jnp.square(value - target_value[jnp.newaxis])

    def loss_fn(params: hk.Params,
                target_params: hk.Params,
                rng: types.RNG,
                o_tm1, a_tm1, r_t, disc_t, o_t
                ) -> jax.Array:
        chex.assert_rank([r_t, a_tm1], [0, 2])
        rngs = jax.random.split(rng, 4)

        o_tm1[types.IMG_KEY] = augmentation_fn(
            rngs[0], o_tm1[types.IMG_KEY], cfg.shift)
        o_t[types.IMG_KEY] = augmentation_fn(
            rngs[1], o_t[types.IMG_KEY], cfg.shift)
        s_tm1 = networks.make_state(params, o_tm1)
        s_t = networks.make_state(target_params, o_t)

        policy_t = networks.actor(params, s_t)
        entropy_t = policy_t.entropy()
        a_t = policy_t.sample(seed=rngs[2])

        critic_idxs = jax.random.choice(
            rngs[3], cfg.ensemble_size, (cfg.num_critics,), replace=False)
        q_t = networks.critic(target_params, s_t, a_t)
        min_q_t = jnp.take(q_t, critic_idxs).min()
        v_t = min_q_t + cfg.entropy_coef * entropy_t
        target_q_tm1 = r_t + cfg.gamma * disc_t * v_t

        q_tm1 = networks.critic(params, s_tm1, a_tm1)
        critic_loss = critic_loss_fn(q_tm1, target_q_tm1)
        actor_loss = - (jnp.mean(q_t) + cfg.entropy_coef * entropy_t)

        metrics = dict(
            critic_loss=critic_loss,
            actor_loss=actor_loss,
            entropy=entropy_t,
            reward=r_t,
            value=v_t
        )
        return critic_loss + actor_loss, metrics

    @chex.assert_max_traces(2)
    def step(state: TrainingState,
             batch: types.Trajectory
             ) -> tuple[TrainingState, types.Metrics]:
        params = state.params
        target_params = state.target_params

        o_tm1, a_tm1, r_t, disc_t, o_t = map(
            batch.get,
            ('observations', 'actions', 'rewards', 'discounts', 'next_observations')
        )
        rngs = jax.random.split(state.rng, cfg.drq_batch_size + 1)
        in_axes = 2 * (None,) + 6 * (0,)
        grad_fn = jax.grad(loss_fn, has_aux=True)
        grad_fn = jax.vmap(grad_fn, in_axes=in_axes)

        out = grad_fn(
            params, target_params, rngs[:-1],
            o_tm1, a_tm1, r_t, disc_t, o_t
        )
        grads, metrics = jax.tree_util.tree_map(lambda t: jnp.mean(t, 0), out)

        state = state.update(grads)
        metrics.update(drq_grads_norm=optax.global_norm(grads))
        return state._replace(rng=rngs[-1]), metrics

    return step
