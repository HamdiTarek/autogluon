import logging
from collections import defaultdict

from pandas import DataFrame

from .abstract import AbstractFeatureGenerator

logger = logging.getLogger(__name__)


# TODO: Not necessary to exist after fitting, can just update outer context feature_out/feature_in and then delete this
class DropDuplicatesFeatureGenerator(AbstractFeatureGenerator):
    def _fit_transform(self, X: DataFrame, **kwargs) -> (DataFrame, dict):
        features_to_drop = self._drop_duplicate_features(X)
        self._remove_features_in(features_to_drop)
        if features_to_drop:
            self._log(15, f'\t{len(features_to_drop)} duplicate columns removed: {features_to_drop}')
        X_out = X[self.features_in]
        return X_out, self.feature_metadata_in.type_group_map_special

    def _transform(self, X):
        return X

    # TODO: optimize categorical/object handling
    def _drop_duplicate_features(self, X: DataFrame) -> list:
        feature_sum_map = defaultdict(list)
        for feature in self.feature_metadata_in.type_group_map_raw['int'] + self.feature_metadata_in.type_group_map_raw['float']:
            feature_sum_map[round(X[feature].sum(), 2)].append(feature)

        features_to_keep = []
        features_to_remove = []
        for key in feature_sum_map:
            if len(feature_sum_map[key]) <= 1:
                features_to_keep += feature_sum_map[key]
            else:
                features_to_keep += list(X[feature_sum_map[key]].T.drop_duplicates().T.columns)
                features_to_remove += [feature for feature in feature_sum_map[key] if feature not in features_to_keep]

        if features_to_keep or features_to_remove:
            X = X.drop(columns=features_to_keep + features_to_remove)

        if len(X.columns) > 0:
            X_without_dups = X.T.drop_duplicates().T
            columns_orig = X.columns.values
            columns_new = X_without_dups.columns.values
            features_to_remove += [column for column in columns_orig if column not in columns_new]

        return features_to_remove
