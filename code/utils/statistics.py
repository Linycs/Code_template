"""任意维数值序列的通用统计对象与命名容器。"""

from __future__ import annotations

import json
import warnings
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

import numpy as np


def _json_value(value):
    """递归转换 NumPy 值，并将非有限浮点数写为 ``null``。"""
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_value(value.tolist())
    if isinstance(value, np.generic):
        return _json_value(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


@dataclass
class StatisticsSeq:
    """带有效性、权重、轴名称和说明信息的任意维 NumPy 数值序列。"""

    values: np.ndarray
    info: dict = field(default_factory=dict)
    valid: np.ndarray | None = None
    weights: np.ndarray | None = None
    axis_names: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        self.values = np.asarray(self.values)
        assert self.values.ndim >= 1, "StatisticsSeq.values 至少需要一维"
        assert np.issubdtype(self.values.dtype, np.number), "values 必须是数值数组"

        if self.axis_names is None:
            self.axis_names = tuple(
                f"axis_{index}" for index in range(self.values.ndim)
            )
        else:
            self.axis_names = tuple(self.axis_names)
        assert len(self.axis_names) == self.values.ndim
        assert len(set(self.axis_names)) == len(self.axis_names)

        if self.valid is None:
            self.valid = np.ones(self.values.shape, dtype=bool)
        else:
            self.valid = np.broadcast_to(
                np.asarray(self.valid, dtype=bool),
                self.values.shape,
            ).copy()

        if self.weights is None:
            self.weights = np.ones(self.values.shape, dtype=np.float64)
        else:
            self.weights = np.broadcast_to(
                np.asarray(self.weights, dtype=np.float64),
                self.values.shape,
            ).copy()
        assert np.isfinite(self.weights[self.valid]).all()
        assert (self.weights[self.valid] >= 0).all()
        self.info = dict(self.info)

    def map_values(self, transform, info: dict | None = None) -> "StatisticsSeq":
        """保留有效性、权重和轴契约，生成数值变换后的新统计序列。"""
        mapped_info = dict(self.info)
        if info:
            mapped_info.update(info)
        return StatisticsSeq(
            values=np.asarray(transform(self.values)),
            info=mapped_info,
            valid=self.valid,
            weights=self.weights,
            axis_names=self.axis_names,
        )

    def analyze(
        self,
        axis: str | int | Iterable[str | int] | None = None,
        quantiles: tuple[float, ...] = (0.5, 0.9),
    ) -> dict:
        """沿指定轴计算有效数、均值、加权均值和分布统计。"""
        axes = self._resolve_axes(axis)
        for quantile in quantiles:
            assert 0.0 <= quantile <= 1.0

        valid = self.valid & np.isfinite(self.values)
        values = np.where(valid, self.values, np.nan)
        effective_weights = np.where(valid, self.weights, 0.0)
        weight_sum = effective_weights.sum(axis=axes)

        with warnings.catch_warnings(), np.errstate(invalid="ignore", divide="ignore"):
            warnings.simplefilter("ignore", category=RuntimeWarning)
            result = {
                "reduced_axes": [self.axis_names[index] for index in axes],
                "remaining_axes": [
                    name for index, name in enumerate(self.axis_names) if index not in axes
                ],
                "count": valid.sum(axis=axes),
                "weight_sum": weight_sum,
                "mean": np.nanmean(values, axis=axes),
                "weighted_mean": np.divide(
                    (np.where(valid, self.values, 0.0) * effective_weights).sum(axis=axes),
                    weight_sum,
                    out=np.full(np.shape(weight_sum), np.nan, dtype=np.float64),
                    where=weight_sum > 0,
                ),
                "median": np.nanmedian(values, axis=axes),
                "std": np.nanstd(values, axis=axes),
                "min": np.nanmin(values, axis=axes),
                "max": np.nanmax(values, axis=axes),
                "quantiles": {
                    self._quantile_name(value): np.nanquantile(values, value, axis=axes)
                    for value in quantiles
                },
            }
        return _json_value(result)

    def analysis(self, quantiles: tuple[float, ...] = (0.5, 0.9)) -> dict:
        """返回全局统计，以及分别沿每个命名轴归约的统计。"""
        return {
            "all": self.analyze(axis=None, quantiles=quantiles),
            "by_axis": {
                name: self.analyze(axis=name, quantiles=quantiles)
                for name in self.axis_names
            },
        }

    def to_dict(self, include_analysis: bool = True) -> dict:
        """返回包含原始数组、说明信息及可选分析结果的 JSON 结构。"""
        result = {
            "axis_names": list(self.axis_names),
            "shape": list(self.values.shape),
            "info": _json_value(self.info),
            "values": _json_value(self.values),
            "valid": _json_value(self.valid),
            "weights": _json_value(self.weights),
        }
        if include_analysis:
            result["analysis"] = self.analysis()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "StatisticsSeq":
        """从 ``to_dict`` 结果恢复统计序列，分析结果会重新计算。"""
        return cls(
            values=np.asarray(data["values"]),
            info=data.get("info", {}),
            valid=np.asarray(data["valid"], dtype=bool),
            weights=np.asarray(data["weights"], dtype=np.float64),
            axis_names=tuple(data["axis_names"]),
        )

    def _resolve_axes(
        self,
        axis: str | int | Iterable[str | int] | None,
    ) -> tuple[int, ...]:
        if axis is None:
            return tuple(range(self.values.ndim))
        requested = (axis,) if isinstance(axis, (str, int)) else tuple(axis)
        axes = tuple(
            self.axis_names.index(item) if isinstance(item, str) else int(item)
            for item in requested
        )
        assert axes and len(set(axes)) == len(axes)
        assert all(0 <= item < self.values.ndim for item in axes)
        return tuple(sorted(axes))

    @staticmethod
    def _quantile_name(value: float) -> str:
        return f"p{int(round(value * 100)):02d}"


class StatisticsManager:
    """管理具名 ``StatisticsSeq``，并支持注册采集器和统一持久化。"""

    def __init__(self, info: dict | None = None):
        self.info = dict(info or {})
        self.sequences: dict[str, StatisticsSeq] = {}
        self._collectors: dict[
            str,
            Callable[[], StatisticsSeq | dict[str, StatisticsSeq]],
        ] = {}

    def add(self, name: str, sequence: StatisticsSeq, replace: bool = False) -> None:
        """加入具名序列；默认禁止静默覆盖已有记录。"""
        assert name and isinstance(sequence, StatisticsSeq)
        assert replace or name not in self.sequences, f"统计序列已存在: {name}"
        self.sequences[name] = sequence

    def get(self, name: str) -> StatisticsSeq:
        return self.sequences[name]

    def remove(self, name: str) -> StatisticsSeq:
        return self.sequences.pop(name)

    def names(self) -> tuple[str, ...]:
        return tuple(self.sequences)

    def register(
        self,
        name: str,
        collector: Callable[[], StatisticsSeq | dict[str, StatisticsSeq]],
    ) -> None:
        """注册不带统计逻辑的数据采集器，供 snapshot 批量调用。"""
        assert name and callable(collector)
        assert name not in self._collectors, f"统计采集器已存在: {name}"
        self._collectors[name] = collector

    def capture(self, snapshot: str, replace: bool = False) -> tuple[str, ...]:
        """调用全部采集器，并以 ``snapshot/collector[/item]`` 命名结果。"""
        assert snapshot
        captured = []
        for collector_name, collector in self._collectors.items():
            result = collector()
            items = result.items() if isinstance(result, dict) else (("", result),)
            for item_name, sequence in items:
                parts = [snapshot, collector_name]
                if item_name:
                    parts.append(str(item_name))
                sequence_name = "/".join(parts)
                self.add(sequence_name, sequence, replace=replace)
                captured.append(sequence_name)
        return tuple(captured)

    def analyze(self, name: str, **kwargs) -> dict:
        return self.get(name).analyze(**kwargs)

    def analyze_all(self) -> dict:
        return {name: sequence.analysis() for name, sequence in self.sequences.items()}

    def to_dict(self, info: dict | None = None, include_analysis: bool = True) -> dict:
        manager_info = dict(self.info)
        if info:
            manager_info.update(info)
        return {
            "info": _json_value(manager_info),
            "sequences": {
                name: sequence.to_dict(include_analysis=include_analysis)
                for name, sequence in self.sequences.items()
            },
        }

    def save(
        self,
        path: str,
        info: dict | None = None,
        include_analysis: bool = True,
    ) -> str:
        """以 JSON 保存全部具名序列、说明信息和分析结果。"""
        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                self.to_dict(info=info, include_analysis=include_analysis),
                file,
                ensure_ascii=False,
                indent=2,
            )
        return path

    @classmethod
    def load(cls, path: str) -> "StatisticsManager":
        """读取 ``save`` 生成的 JSON；顶层运行说明不进入序列容器。"""
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        manager = cls(info=data.get("info", {}))
        for name, sequence in data["sequences"].items():
            manager.add(name, StatisticsSeq.from_dict(sequence))
        return manager
