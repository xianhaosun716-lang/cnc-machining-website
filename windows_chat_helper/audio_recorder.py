from __future__ import annotations

import threading
from pathlib import Path
from typing import List

import numpy as np
import sounddevice as sd
import soundfile as sf


class AudioRecorder:
    """Simple microphone recorder using sounddevice.

    Records mono audio and saves it to WAV. Keeps implementation minimal for stable MVP.
    """

    def __init__(self, sample_rate: int = 16000) -> None:
        self.sample_rate = sample_rate
        self.channels = 1
        self._frames: List[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()
        self._recording = False

    @property
    def is_recording(self) -> bool:
        return self._recording

    def _callback(self, indata: np.ndarray, frames: int, time, status) -> None:  # type: ignore[no-untyped-def]
        if status:
            # Keeping this non-fatal for user simplicity.
            print(f"Audio status warning: {status}")
        with self._lock:
            if self._recording:
                self._frames.append(indata.copy())

    def start(self) -> None:
        self._frames = []
        self._recording = True
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def stop_and_save(self, output_path: Path) -> Path:
        self._recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if not self._frames:
                raise RuntimeError("未录到声音，请检查麦克风后重试。")
            audio = np.concatenate(self._frames, axis=0)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(output_path), audio, self.sample_rate)
        return output_path
