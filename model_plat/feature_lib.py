import numpy as np
from typing import Tuple, Any
import pandas as pd


def calculate_woe_iv_by_single_feature(df, feature, target) -> Tuple[str, Any, float]:
    """
    单个特征的WOE、IV计算
    Args:
        df: pandas
        feature: 需计算IV的那个单独特征列
        target: 目标列

    Returns:tuple(特征列、_、iv)

    """

    event = df[target].sum()
    non_event = len(df) - event
    agg = df.groupby(feature)[target].agg(['count', 'sum'])
    agg['non_event'] = agg['count'] - agg['sum']
    agg = agg.rename(columns={'sum': 'event'})
    agg['woe'] = np.log(((agg['event'] + 0.5) / event) / ((agg['non_event'] + 0.5) / non_event))
    agg['iv'] = (agg['event'] / event - agg['non_event'] / non_event) * agg['woe']
    iv_sum = agg['iv'].sum()
    woe: dict = agg['woe'].to_dict()
    # first_key = list(woe.keys())[0]
    # first_key_value = woe[first_key]
    # print(f"**********feature {feature} target = {target} calc finished; result iv = {iv_sum}, random pick woe = {first_key_value}")
    all_woes = {}
    total_iv = 0
    total_iv += iv_sum
    for k, v in woe.items():
        all_woes.setdefault(k, []).append(v)
    avg_woe = {k: np.mean(v) for k, v in all_woes.items()}
    avg_iv = total_iv
    # print(f"col_name = {feature}, avg_woe = {avg_woe}, avg_iv = {avg_iv}")
    return feature, None, avg_iv


def calculate_psi_v2(train_proba, test_proba, bins=10, eps=1e-6):
    def calc_ratio(y_proba):
        y_proba_1d = y_proba.reshape(1, -1)
        ratios = []
        for i, interval in enumerate(intervals):
            if i == len(interval) - 1:
                # include the probability==1
                n_samples = (y_proba_1d[np.where((y_proba_1d >= interval[0]) & (y_proba_1d <= interval[1]))]).shape[0]
            else:
                n_samples = (y_proba_1d[np.where((y_proba_1d >= interval[0]) & (y_proba_1d < interval[1]))]).shape[0]
            ratio = n_samples / y_proba.shape[0]
            if ratio == 0:
                ratios.append(eps)
            else:
                ratios.append(ratio)
        return np.array(ratios)

    distance = 1 / bins
    intervals = [(i * distance, (i + 1) * distance) for i in range(bins)]
    train_ratio = calc_ratio(train_proba)
    test_ratio = calc_ratio(test_proba)
    return np.sum((train_ratio - test_ratio) * np.log(train_ratio / test_ratio))


def calculate_psi_bydf(expected_df, expected_target, actual_df, actual_target, buckettype='bins', bins=10, axis=0, eps=1e-6):
    return calculate_psi(expected_df[expected_target], actual_df[actual_target], buckettype, bins, axis, eps)


def calculate_psi(expected, actual, buckettype='bins', bins=10, axis=0, eps=1e-6):
    """
    Calculate the PSI (population stability index) across all variables

    Args:
       eps:
       expected: numpy matrix of original values
       actual: numpy matrix of new values
       buckettype: type of strategy for creating buckets, bins splits into even splits, quantiles splits into quantile buckets
       bins: number of quantiles to use in bucketing variables
       axis: axis by which variables are defined, 0 for vertical, 1 for horizontal

    Returns:
       psi_values: ndarray of psi values for each variable

    Author:
       Matthew Burke
       github.com/mwburke
       mwburke.github.io.com
    """

    def psi(expected_array, actual_array, buckets):
        '''Calculate the PSI for a single variable

        Args:
           expected_array: numpy array of original values
           actual_array: numpy array of new values, same size as expected
           buckets: number of percentile ranges to bucket the values into

        Returns:
           psi_value: calculated PSI value
        '''

        def scale_range(input, min, max):
            input += -(np.min(input))
            input /= np.max(input) / (max - min)
            input += min
            return input

        breakpoints = np.arange(0, buckets + 1) / (buckets) * 100

        if buckettype == 'bins':
            breakpoints = scale_range(breakpoints, np.min(expected_array), np.max(expected_array))
        elif buckettype == 'quantiles':
            breakpoints = np.stack([np.percentile(expected_array, b) for b in breakpoints])

        expected_fractions = np.histogram(expected_array, breakpoints)[0] / len(expected_array)
        actual_fractions = np.histogram(actual_array, breakpoints)[0] / len(actual_array)

        def sub_psi(e_perc, a_perc):
            '''Calculate the actual PSI value from comparing the values.
               Update the actual value to a very small number if equal to zero
            '''
            if a_perc == 0:
                a_perc = eps
            if e_perc == 0:
                e_perc = eps

            value = (e_perc - a_perc) * np.log(e_perc / a_perc)
            return value

        psi_value = sum(sub_psi(expected_fractions[i], actual_fractions[i]) for i in range(0, len(expected_fractions)))

        return psi_value

    if len(expected.shape) == 1:
        psi_values = np.empty(len(expected.shape))
    else:
        psi_values = np.empty(expected.shape[1 - axis])

    for i in range(0, len(psi_values)):
        if len(psi_values) == 1:
            psi_values = psi(expected, actual, bins)
        elif axis == 0:
            psi_values[i] = psi(expected[:, i], actual[:, i], bins)
        elif axis == 1:
            psi_values[i] = psi(expected[i, :], actual[i, :], bins)

    return psi_values
