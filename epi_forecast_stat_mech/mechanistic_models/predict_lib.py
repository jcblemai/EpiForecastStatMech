# Lint as: python3
"""Helpers to make predictions using mechanistic models."""

import jax
import jax.numpy as jnp
import numpy as np
import xarray

from epi_forecast_stat_mech.evaluation import monte_carlo  # pylint: disable=g-bad-import-order


def wrap_predictions(predictions, locations, num_samples, times):
  # TODO(jamieas): consider indexing by seed.
  sample = np.arange(num_samples)
  return xarray.DataArray(
      predictions,
      coords=[locations, sample, times],
      dims=['location', 'sample', 'time']).rename('new_infections')


def simulate_predictions(mech_model,
                         mech_params,
                         data,
                         epidemics,
                         test_data,
                         num_samples,
                         rng,
                         include_observed=False):
  time_steps = len(test_data.time)
  predictions = monte_carlo.trajectories_from_model(
      mech_model,
      mech_params,
      rng,
      epidemics,
      time_steps,
      num_samples,
      include_observed)
  if include_observed:
    times = np.concatenate((data.time, test_data.time))
  else:
    times = test_data.time
  return wrap_predictions(predictions, data.location, num_samples, times)


def simulate_dynamic_predictions(mech_model,
                                 mech_params,
                                 data,
                                 epidemics,
                                 dynamic_covariates,
                                 num_samples,
                                 rng,
                                 include_observed=False):

  predictions = monte_carlo.trajectories_from_dynamic_model(
      mech_model,
      mech_params,
      rng,
      epidemics,
      dynamic_covariates,
      num_samples)

  full_predictions = wrap_predictions(predictions, data.location, num_samples,
                                      dynamic_covariates.time)
  if not include_observed:
    time_steps = dynamic_covariates.sizes['time'] - epidemics.t.shape[1]
    return full_predictions.isel(time=slice(-time_steps, None))
  return full_predictions


def encoded_mech_params_array(data, mech_model, mech_params):
  return xarray.DataArray(
      mech_params,
      dims=('location', 'encoded_param'),
      coords=dict(
          location=data.location,
          encoded_param=list(mech_model.encoded_param_names)))


def mech_params_array(data, mech_model, mech_params):
  decoded_mech_params = jax.vmap(mech_model.decode_params)(mech_params)
  return xarray.DataArray(
      decoded_mech_params,
      dims=('location', 'param'),
      coords=dict(
          location=data.location,
          param=list(mech_model.param_names)))
