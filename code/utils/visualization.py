"""与业务无关的多 shape 三维可视化和文件导出。"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

class ColorPalette:
    """从 matplotlib 色板中按色系和深浅取得归一化 RGB。"""

    FAMILIES = {
        "warm": "Oranges",
        "cool": "Blues",
        "green": "Greens",
    }
    SHADES = {"light": 0.55, "dark": 0.80}

    @classmethod
    def get(cls, family, shade):
        color = matplotlib.colormaps[cls.FAMILIES[family]](cls.SHADES[shade])
        return tuple(float(value) for value in color[:3])

class VisMultiShape:
    """在同一坐标系中管理多个 point cloud/mesh，并按指定路径导出。"""

    def __init__(self, coordinate_frame: str = "", unit: str = ""):
        self.coordinate_frame = str(coordinate_frame)
        self.unit = str(unit)
        self.shapes = []

    def add_shape(
        self,
        vertices,
        color,
        label: str,
        faces=None,
        point_size: float = 2.0,
        alpha: float = 0.72,
    ) -> "VisMultiShape":
        """加入点云或三角 mesh；``faces=None`` 时按点云处理。"""
        vertices = self._vertices(vertices)
        assert point_size > 0 and 0.0 <= alpha <= 1.0
        if faces is not None:
            faces = np.asarray(faces, dtype=np.int32)
            assert faces.ndim == 2 and faces.shape[1] == 3
            assert len(faces) == 0 or (
                int(faces.min()) >= 0 and int(faces.max()) < len(vertices)
            )
        self.shapes.append(
            {
                "geometry_type": "mesh" if faces is not None else "point_cloud",
                "vertices": vertices,
                "faces": faces,
                "color": self._color(color),
                "label": str(label),
                "point_size": None if faces is not None else float(point_size),
                "alpha": float(alpha),
            }
        )
        return self

    def export_ply(self, path: str | Path) -> Path:
        """把全部 shape 合并为带颜色、类型和 shape 编号的二进制 PLY。"""
        assert self.shapes, "至少添加一个 shape 后才能导出"
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        vertices_out, colors_out, types_out, indices_out, faces_out = [], [], [], [], []
        vertex_offset = 0
        for shape_index, shape in enumerate(self.shapes):
            vertices = shape["vertices"]
            vertices_out.append(vertices)
            colors_out.append(
                np.tile(
                    np.rint(shape["color"] * 255.0).astype(np.uint8),
                    (len(vertices), 1),
                )
            )
            geometry_type = 0 if shape["geometry_type"] == "mesh" else 1
            types_out.append(np.full(len(vertices), geometry_type, dtype=np.uint8))
            indices_out.append(np.full(len(vertices), shape_index, dtype=np.uint16))
            if shape["faces"] is not None and len(shape["faces"]):
                faces_out.append(shape["faces"] + vertex_offset)
            vertex_offset += len(vertices)

        assert vertex_offset > 0, "所有 shape 均为空，无法导出"
        all_vertices = np.concatenate(vertices_out).astype(np.float32, copy=False)
        all_colors = np.concatenate(colors_out)
        all_types = np.concatenate(types_out)
        all_indices = np.concatenate(indices_out)
        all_faces = (
            np.concatenate(faces_out).astype(np.int32, copy=False)
            if faces_out
            else np.empty((0, 3), dtype=np.int32)
        )

        vertex_dtype = np.dtype(
            [
                ("x", "<f4"),
                ("y", "<f4"),
                ("z", "<f4"),
                ("red", "u1"),
                ("green", "u1"),
                ("blue", "u1"),
                ("geometry_type", "u1"),
                ("shape_index", "<u2"),
            ]
        )
        vertex_records = np.empty(len(all_vertices), dtype=vertex_dtype)
        vertex_records["x"], vertex_records["y"], vertex_records["z"] = all_vertices.T
        vertex_records["red"], vertex_records["green"], vertex_records["blue"] = all_colors.T
        vertex_records["geometry_type"] = all_types
        vertex_records["shape_index"] = all_indices

        face_dtype = np.dtype([("count", "u1"), ("indices", "<i4", (3,))])
        face_records = np.empty(len(all_faces), dtype=face_dtype)
        face_records["count"] = 3
        face_records["indices"] = all_faces

        comments = ["comment geometry_type 0=mesh 1=point_cloud"]
        if self.coordinate_frame:
            comments.append(f"comment coordinate_frame {self.coordinate_frame}")
        if self.unit:
            comments.append(f"comment units {self.unit}")
        labels = "|".join(
            shape["label"].replace("|", "/") for shape in self.shapes
        )
        comments.append(f"comment shape_labels {labels}")
        header = (
            "ply\nformat binary_little_endian 1.0\n"
            + "\n".join(comments)
            + "\n"
            + f"element vertex {len(all_vertices)}\n"
            + "property float x\nproperty float y\nproperty float z\n"
            + "property uchar red\nproperty uchar green\nproperty uchar blue\n"
            + "property uchar geometry_type\nproperty ushort shape_index\n"
            + f"element face {len(all_faces)}\n"
            + "property list uchar int vertex_indices\nend_header\n"
        ).encode("ascii", errors="replace")
        with path.open("wb") as file:
            file.write(header)
            file.write(vertex_records.tobytes())
            file.write(face_records.tobytes())
        return path

    def export_image(
        self,
        path: str | Path,
        title: str = "",
        views=((22, -68), (12, 112)),
        display_scale: float = 1.0,
        display_unit: str = "",
        axis_names=("x", "y", "z"),
        min_half_extent: float = 1.0,
    ) -> Path:
        """把全部 shape 居中后按指定视角渲染到图片路径。"""
        assert self.shapes and len(views) > 0
        assert display_scale > 0 and min_half_extent > 0
        assert len(axis_names) == 3
        nonempty = [shape["vertices"] for shape in self.shapes if len(shape["vertices"])]
        assert nonempty, "所有 shape 均为空，无法渲染"

        center = np.median(np.concatenate(nonempty), axis=0)
        display_vertices = [
            (shape["vertices"] - center) * display_scale for shape in self.shapes
        ]
        nonempty_display = [value for value in display_vertices if len(value)]
        lower, upper = np.percentile(np.concatenate(nonempty_display), [1, 99], axis=0)
        half_extent = max(float((upper - lower).max()) * 0.58, min_half_extent)
        midpoint = (lower + upper) * 0.5

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        figure = plt.figure(figsize=(6 * len(views), 6), dpi=130)
        for panel, (elevation, azimuth) in enumerate(views, start=1):
            axis = figure.add_subplot(1, len(views), panel, projection="3d")
            legend_handles = []
            for shape, vertices in zip(self.shapes, display_vertices):
                if shape["geometry_type"] == "mesh":
                    if len(shape["faces"]):
                        collection = Poly3DCollection(
                            vertices[shape["faces"]],
                            facecolor=shape["color"],
                            edgecolor="none",
                            alpha=shape["alpha"],
                        )
                        axis.add_collection3d(collection)
                    legend_handles.append(
                        Patch(
                            facecolor=shape["color"],
                            alpha=shape["alpha"],
                            label=shape["label"],
                        )
                    )
                elif len(vertices):
                    axis.scatter(
                        vertices[:, 0],
                        vertices[:, 1],
                        vertices[:, 2],
                        s=shape["point_size"],
                        color=shape["color"],
                        alpha=shape["alpha"],
                    )
                    legend_handles.append(
                        Line2D(
                            [],
                            [],
                            linestyle="none",
                            marker="o",
                            markersize=max(float(shape["point_size"]) ** 0.5, 2.0),
                            color=shape["color"],
                            alpha=shape["alpha"],
                            label=shape["label"],
                        )
                    )
            axis.set_xlim(midpoint[0] - half_extent, midpoint[0] + half_extent)
            axis.set_ylim(midpoint[1] - half_extent, midpoint[1] + half_extent)
            axis.set_zlim(midpoint[2] - half_extent, midpoint[2] + half_extent)
            axis.set_box_aspect((1, 1, 1))
            suffix = f" / {display_unit}" if display_unit else ""
            axis.set_xlabel(f"{axis_names[0]}{suffix}")
            axis.set_ylabel(f"{axis_names[1]}{suffix}")
            axis.set_zlabel(f"{axis_names[2]}{suffix}")
            axis.view_init(elev=elevation, azim=azimuth)
            if panel == 1 and legend_handles:
                axis.legend(handles=legend_handles, loc="upper left", fontsize=7)
        if title:
            figure.suptitle(title)
        figure.tight_layout()
        figure.savefig(path)
        plt.close(figure)
        return path

    @staticmethod
    def _vertices(values) -> np.ndarray:
        vertices = np.asarray(values, dtype=np.float32)
        assert vertices.ndim == 2 and vertices.shape[1] == 3
        return vertices

    @staticmethod
    def _color(value) -> np.ndarray:
        color = np.asarray(value, dtype=np.float32)
        assert color.shape == (3,)
        assert np.isfinite(color).all() and (color >= 0).all() and (color <= 1).all()
        return color
