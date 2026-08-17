"""基于针孔相机的通用三角网格 ray-casting 渲染。

本模块只依赖 NumPy/Open3D，不理解 MANO、depth、左右手或项目 provider。
调用方负责提供同一坐标系下的 mesh 和相机，并解释渲染结果的业务语义。
"""

from __future__ import annotations

import numpy as np
import open3d as o3d


class MeshRenderer:
    """用 Open3D z-buffer 渲染 mesh silhouette 或多 mesh 可见 face。"""

    def __init__(self, intrinsics, image_shape, camera_to_world=None):
        """保存针孔相机；未给 ``camera_to_world`` 时输入顶点视为相机坐标。"""
        self.intrinsics = np.asarray(intrinsics, dtype=np.float32)
        assert self.intrinsics.shape == (3, 3)

        self.image_shape = tuple(int(value) for value in image_shape)
        assert len(self.image_shape) == 2
        assert self.image_shape[0] > 0 and self.image_shape[1] > 0

        self.world_to_camera = None
        if camera_to_world is not None:
            camera_to_world = np.asarray(camera_to_world, dtype=np.float64)
            assert camera_to_world.shape == (4, 4)
            self.world_to_camera = np.linalg.inv(camera_to_world)

    def render_silhouette(self, vertices, faces) -> np.ndarray:
        """渲染单个 mesh 的 bool silhouette，输出形状为 ``(H,W)``。"""
        vertices_camera = self._to_camera(vertices)
        output = np.zeros(self.image_shape, dtype=bool)
        bounds = self._projection_bounds(vertices_camera)
        if bounds is None:
            return output

        scene = o3d.t.geometry.RaycastingScene()
        scene.add_triangles(self._triangle_mesh(vertices_camera, faces))
        rays = self._camera_rays(bounds)
        hits = scene.cast_rays(o3d.core.Tensor(rays))['t_hit'].numpy()
        x0, x1, y0, y1 = bounds
        output[y0:y1, x0:x1] = np.isfinite(hits)
        return output

    def visible_face_indices(self, vertices_by_mesh, faces_by_mesh):
        """联合渲染多个 mesh，返回各 mesh 被 z-buffer 命中的唯一 face index。

        多个 mesh 加入同一 scene，因此输出包含 mesh 之间的相互遮挡关系。
        """
        vertices_by_mesh = list(vertices_by_mesh)
        faces_by_mesh = list(faces_by_mesh)
        assert len(vertices_by_mesh) == len(faces_by_mesh) > 0

        vertices_camera = [
            self._to_camera(vertices) for vertices in vertices_by_mesh
        ]
        scene = o3d.t.geometry.RaycastingScene()
        geometry_ids = [
            int(scene.add_triangles(self._triangle_mesh(vertices, faces)))
            for vertices, faces in zip(vertices_camera, faces_by_mesh)
        ]

        visible_faces = [[] for _ in faces_by_mesh]
        # 分 mesh 投影包围盒发射 rays，与整幅图渲染等价，同时减少空白区域开销。
        for vertices in vertices_camera:
            bounds = self._projection_bounds(vertices)
            if bounds is None:
                continue
            hits = scene.cast_rays(o3d.core.Tensor(self._camera_rays(bounds)))
            hit_geometry = hits['geometry_ids'].numpy()
            hit_faces = hits['primitive_ids'].numpy()
            for mesh_index, geometry_id in enumerate(geometry_ids):
                belongs_to_mesh = hit_geometry == geometry_id
                if belongs_to_mesh.any():
                    visible_faces[mesh_index].append(
                        hit_faces[belongs_to_mesh].astype(np.int64, copy=False)
                    )

        return [
            (
                np.unique(np.concatenate(face_groups))
                if face_groups
                else np.empty(0, dtype=np.int64)
            )
            for face_groups in visible_faces
        ]

    def _to_camera(self, vertices) -> np.ndarray:
        """将顶点整理为 float32 相机坐标。"""
        vertices = np.asarray(vertices, dtype=np.float64)
        assert vertices.ndim == 2 and vertices.shape[1] == 3
        if self.world_to_camera is not None:
            vertices = (
                vertices @ self.world_to_camera[:3, :3].T
                + self.world_to_camera[:3, 3]
            )
        return np.ascontiguousarray(vertices, dtype=np.float32)

    @staticmethod
    def _triangle_mesh(vertices, faces):
        """构造 Open3D tensor mesh。"""
        faces = np.ascontiguousarray(faces, dtype=np.uint32)
        assert faces.ndim == 2 and faces.shape[1] == 3
        mesh = o3d.t.geometry.TriangleMesh()
        mesh.vertex.positions = o3d.core.Tensor(vertices)
        mesh.triangle.indices = o3d.core.Tensor(faces)
        return mesh

    def _projection_bounds(self, vertices_camera):
        """返回图像内 mesh 投影包围盒 ``(x0,x1,y0,y1)``。"""
        positive = vertices_camera[:, 2] > 1e-6
        if not positive.any():
            return None

        vertices = vertices_camera[positive]
        intrinsics = self.intrinsics
        u = intrinsics[0, 0] * vertices[:, 0] / vertices[:, 2] + intrinsics[0, 2]
        v = intrinsics[1, 1] * vertices[:, 1] / vertices[:, 2] + intrinsics[1, 2]
        height, width = self.image_shape
        x0 = max(0, int(np.floor(np.nanmin(u))) - 2)
        x1 = min(width, int(np.ceil(np.nanmax(u))) + 3)
        y0 = max(0, int(np.floor(np.nanmin(v))) - 2)
        y1 = min(height, int(np.ceil(np.nanmax(v))) + 3)
        return None if x1 <= x0 or y1 <= y0 else (x0, x1, y0, y1)

    def _camera_rays(self, bounds):
        """生成相机原点出发、覆盖投影包围盒的 rays。"""
        x0, x1, y0, y1 = bounds
        rows, cols = np.mgrid[y0:y1, x0:x1]
        intrinsics = self.intrinsics
        directions = np.stack(
            [
                (cols - intrinsics[0, 2]) / intrinsics[0, 0],
                (rows - intrinsics[1, 2]) / intrinsics[1, 1],
                np.ones_like(cols),
            ],
            axis=-1,
        ).astype(np.float32)
        return np.concatenate([np.zeros_like(directions), directions], axis=-1)
