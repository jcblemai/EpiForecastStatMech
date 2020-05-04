# Lint as: python3
"""Tests for epi_forecast_stat_mech.high_level."""

from absl.testing import absltest

from epi_forecast_stat_mech import high_level
from epi_forecast_stat_mech import sir_sim

from jax.config import config
import numpy as np

config.parse_flags_with_absl()  # Necessary for running on TPU.


def create_synthetic_dataset(
    seed=0,
    num_epidemics=50,
    num_important_cov=1,
    num_unimportant_cov=2,
    constant_pop_size=200000,
    num_time_steps=100,
):
  """Creates synthetic data."""
  np.random.seed(seed)  # TODO(shoyer): use np.random.RandomState
  num_simulations = 1
  trajectories = sir_sim.generate_simulations(
      sir_sim.generate_betas_many_cov2,
      (num_epidemics, num_important_cov, num_unimportant_cov),
      num_simulations, num_epidemics,
      constant_pop_size=constant_pop_size,
      num_time_steps=num_time_steps)
  trajectories = trajectories.squeeze('sample')
  return trajectories


class TestHighLevel(absltest.TestCase):
  """Tests for high_level module."""

  def test_StatMechEstimator(self):
    """Verify we can fit and predict from StatMechEstimator."""
    prediction_length = 10
    num_samples = 11

    data = create_synthetic_dataset(num_epidemics=50, num_time_steps=100)
    estimator = high_level.StatMechEstimator().fit(data, train_steps=1000)

    predictions = estimator.predict(prediction_length, num_samples)
    self.assertCountEqual(['location', 'sample', 'time'], predictions.dims)
    self.assertLen(predictions.time, prediction_length)
    np.testing.assert_array_equal(data.location, predictions.location)
    self.assertLen(predictions.sample, num_samples)

  def test_RtLiveEstimator(self):
    """Verify we can fit and predict from RtLiveEstimator."""
    prediction_length = 10
    num_samples = 11

    data = create_synthetic_dataset(num_epidemics=50, num_time_steps=100)
    estimator = high_level.RtLiveEstimator(gamma=1.0).fit(data)

    predictions = estimator.predict(prediction_length, num_samples)
    self.assertCountEqual(['location', 'sample', 'time'], predictions.dims)
    self.assertLen(predictions.time, prediction_length)
    np.testing.assert_array_equal(data.location, predictions.location)
    self.assertLen(predictions.sample, num_samples)

  def test_SparseEstimator(self):
    """Verify we can fit and predict from SparseEstimator."""
    prediction_length = 10
    num_samples = 11

    data = create_synthetic_dataset(num_epidemics=50, num_time_steps=100)
    estimator = high_level.StatMechEstimator().fit(data, train_steps=1000)

    predictions = estimator.predict(prediction_length, num_samples)
    self.assertCountEqual(['location', 'sample', 'time'], predictions.dims)
    self.assertLen(predictions.time, prediction_length)
    np.testing.assert_array_equal(data.location, predictions.location)
    self.assertLen(predictions.sample, num_samples)


if __name__ == '__main__':
  absltest.main()
