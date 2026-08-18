"""Stream BGR image frames to a browser-compatible H.264 MP4."""

from __future__ import annotations

import subprocess
from pathlib import Path
from types import TracebackType

import numpy as np
from numpy.typing import NDArray


class H264VideoWriter:
    """Write fixed-size uint8 BGR frames through an FFmpeg raw-video pipe."""

    def __init__(
        self,
        output_path: Path,
        fps: float,
        crf: int = 18,
        preset: str = "medium",
    ) -> None:
        if fps <= 0:
            raise ValueError("video fps must be positive")
        self.output_path = Path(output_path)
        self.fps = float(fps)
        self.crf = int(crf)
        self.preset = str(preset)
        self.frame_shape: tuple[int, int, int] | None = None
        self.frame_count = 0
        self._process: subprocess.Popen[bytes] | None = None

    def __enter__(self) -> H264VideoWriter:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            self.close()
        except Exception:
            if exc_type is None:
                raise

    def write(self, frame: NDArray[np.uint8]) -> None:
        """Validate and append one BGR frame."""
        frame = np.asarray(frame)
        if frame.dtype != np.uint8 or frame.ndim != 3 or frame.shape[2] != 3:
            raise ValueError("video frames must be uint8 BGR arrays with shape [H,W,3]")
        if self._process is None:
            self._start(frame.shape)
        if frame.shape != self.frame_shape:
            raise ValueError(
                f"video frame shape changed from {self.frame_shape} to {frame.shape}"
            )
        assert self._process is not None and self._process.stdin is not None
        try:
            self._process.stdin.write(np.ascontiguousarray(frame).tobytes())
        except BrokenPipeError as error:
            raise RuntimeError("FFmpeg H.264 input pipe closed unexpectedly") from error
        self.frame_count += 1

    def close(self) -> None:
        """Finish encoding and raise if FFmpeg rejected the stream."""
        if self._process is None:
            raise RuntimeError("cannot encode an empty video")
        process = self._process
        self._process = None
        assert process.stdin is not None and process.stderr is not None
        process.stdin.close()
        error_text = process.stderr.read().decode("utf-8", errors="replace").strip()
        return_code = process.wait()
        if return_code != 0:
            detail = f": {error_text}" if error_text else ""
            raise RuntimeError(f"FFmpeg H.264 encoding failed{detail}")

    def _start(self, frame_shape: tuple[int, int, int]) -> None:
        """Start FFmpeg after the first frame establishes video dimensions."""
        height, width, _ = frame_shape
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "rawvideo",
            "-pixel_format",
            "bgr24",
            "-video_size",
            f"{width}x{height}",
            "-framerate",
            f"{self.fps:g}",
            "-i",
            "-",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            self.preset,
            "-crf",
            str(self.crf),
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(self.output_path),
        ]
        try:
            self._process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as error:
            raise RuntimeError("video encoding requires ffmpeg in PATH") from error
        self.frame_shape = frame_shape
