from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy import ndarray
from pandas import DataFrame
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import PCA


@dataclass
class PcaPrismTransformer(BaseEstimator, TransformerMixin):
    n_bins: int = 5
    use_angle_bins: bool = False
    fan_from_apex: bool = True
    apex: tuple[float, float] | None = None
    apex_quantile: float = 0.05
    random_state: int = 42
    column_substring: str = "_season_"

    pca_model: PCA | None = field(init=False, default=None)
    fitted_apex: tuple[float, float] | None = field(init=False, default=None)
    selected_columns_: list[str] = field(init=False, default_factory=list)

    def fit(
        self, X: DataFrame | ndarray, y: ndarray | None = None
    ) -> PcaPrismTransformer:
        X_array = self._get_fit_array(X)

        self.pca_model = PCA(n_components=2, random_state=self.random_state)
        transformed = self.pca_model.fit_transform(X_array)

        x_values = transformed[:, 0]
        y_values = transformed[:, 1]

        if self.fan_from_apex:
            if self.apex is not None:
                self.fitted_apex = self.apex
            else:
                cutoff = np.quantile(x_values, self.apex_quantile)
                left_mask = x_values <= cutoff
                if np.sum(left_mask) < 3:
                    left_mask = x_values <= np.sort(x_values)[min(len(x_values) - 1, 4)]

                self.fitted_apex = (
                    float(np.median(x_values[left_mask])),
                    float(np.median(y_values[left_mask])),
                )
        else:
            self.fitted_apex = (0.0, 0.0)

        return self

    def transform(self, X: DataFrame | ndarray) -> ndarray:
        if self.pca_model is None or self.fitted_apex is None:
            raise ValueError(
                "PcaPrismTransformer must be fitted before calling transform()."
            )

        X_array = self._get_transform_array(X)

        transformed = self.pca_model.transform(X_array)
        x_values = transformed[:, 0]
        y_values = transformed[:, 1]

        shifted_x = x_values - self.fitted_apex[0]
        shifted_y = y_values - self.fitted_apex[1]
        angle = np.arctan2(shifted_y, shifted_x)

        values = equal_size_bins(angle, self.n_bins) if self.use_angle_bins else angle
        return values.reshape(-1, 1)

    def transform_to_pca_space(self, X: DataFrame | ndarray) -> ndarray:
        if self.pca_model is None:
            raise ValueError(
                "PcaPrismTransformer must be fitted before calling transform_to_pca_space()."
            )

        X_array = self._get_transform_array(X)
        return self.pca_model.transform(X_array)

    def _get_fit_array(self, X: DataFrame | ndarray) -> ndarray:
        if isinstance(X, DataFrame):
            self.selected_columns_ = [
                column for column in X.columns if self.column_substring in column
            ]
            if not self.selected_columns_:
                raise ValueError(
                    f'No columns contained substring "{self.column_substring}".'
                )
            return X[self.selected_columns_].to_numpy(dtype=float)

        return np.asarray(X, dtype=float)

    def _get_transform_array(self, X: DataFrame | ndarray) -> ndarray:
        if isinstance(X, DataFrame):
            if not self.selected_columns_:
                raise ValueError("No fitted columns were stored during fit().")
            return X[self.selected_columns_].to_numpy(dtype=float)

        return np.asarray(X, dtype=float)


def equal_size_bins(values: ndarray, n_bins: int) -> ndarray:
    values = np.asarray(values, dtype=float)

    order = np.argsort(values)
    labels = np.empty(len(values), dtype=int)

    bin_sizes = np.full(n_bins, len(values) // n_bins, dtype=int)
    bin_sizes[: len(values) % n_bins] += 1

    start = 0
    for bin_index, size in enumerate(bin_sizes):
        end = start + size
        labels[order[start:end]] = bin_index
        start = end

    return labels
