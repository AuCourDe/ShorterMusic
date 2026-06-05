import os
import sys
import librosa
import soundfile as sf
import numpy as np
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional


class AudioLoader:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.ffmpeg_path = self._find_ffmpeg()

    def _find_ffmpeg(self) -> str:
        base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
        bundled_ffmpeg = base_dir / "bin" / "ffmpeg" / "ffmpeg.exe"
        if bundled_ffmpeg.exists():
            return str(bundled_ffmpeg)

        for path in os.environ.get("PATH", "").split(os.pathsep):
            ffmpeg = Path(path) / "ffmpeg.exe"
            if ffmpeg.exists():
                return str(ffmpeg)

        return "ffmpeg"

    def load_audio(self, file_path: str, sr: Optional[int] = None, mono: bool = True) -> Tuple[np.ndarray, int]:
        sr = sr or self.sample_rate
        y, sr = librosa.load(file_path, sr=sr, mono=mono)
        # librosa returns stereo as (channels, samples); transpose to (samples, channels).
        if not mono and y.ndim > 1:
            y = y.T
        return y, sr

    def load_segment(self, file_path: str, start_time: float, end_time: float, sr: Optional[int] = None) -> np.ndarray:
        sr = sr or self.sample_rate
        y, _ = librosa.load(file_path, sr=sr, mono=True, offset=start_time, duration=end_time - start_time)
        return y

    def normalize_audio(self, audio: np.ndarray, target_dB: float = -3.0) -> np.ndarray:
        if np.max(np.abs(audio)) < 1e-10:
            return audio
        
        current_dB = 20 * np.log10(np.max(np.abs(audio)) + 1e-10)
        gain = target_dB - current_dB
        normalized = audio * (10 ** (gain / 20))
        
        normalized = np.clip(normalized, -1.0, 1.0)
        
        return normalized

    def save_audio(self, audio: np.ndarray, file_path: str, sr: Optional[int] = None) -> None:
        sr = sr or self.sample_rate
        output_path = Path(file_path)
        suffix = output_path.suffix.lower()
        
        if suffix == '.mp3':
            self._export_mp3(audio, output_path, sr)
            return
        
        format_hint = None
        if suffix == '.wav':
            format_hint = 'WAV'
        elif suffix == '.flac':
            format_hint = 'FLAC'
        elif suffix in ('.ogg', '.oga'):
            format_hint = 'OGG'
        
        sf.write(str(output_path), audio, sr, format=format_hint)

    def apply_gain(self, audio: np.ndarray, gain_db: float) -> np.ndarray:
        if np.max(np.abs(audio)) < 1e-10 or gain_db == 0:
            return audio
        
        gain_factor = 10 ** (gain_db / 20.0)
        amplified = audio * gain_factor
        return np.clip(amplified, -1.0, 1.0)

    def get_duration(self, file_path: str) -> float:
        duration = librosa.get_duration(path=file_path)
        return duration

    def convert_to_mono(self, audio: np.ndarray) -> np.ndarray:
        if len(audio.shape) > 1:
            return librosa.to_mono(audio.T)
        return audio

    def resample(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        return librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)

    def time_stretch(self, audio: np.ndarray, rate: float) -> np.ndarray:
        if rate <= 0 or np.max(np.abs(audio)) < 1e-10:
            return audio
        stretched = librosa.effects.time_stretch(audio, rate=rate)
        return np.ascontiguousarray(stretched, dtype=np.float32)

    def validate_audio_file(self, file_path: str) -> bool:
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            
            supported_formats = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.wma']
            if path.suffix.lower() not in supported_formats:
                return False
            
            self.load_audio(file_path)
            return True
        except Exception:
            return False

    def _export_mp3(self, audio: np.ndarray, output_path: Path, sr: int) -> None:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            sf.write(str(tmp_path), audio, sr, format='WAV', subtype='PCM_16')
            channels = 2 if audio.ndim > 1 and audio.shape[1] > 1 else 1
            cmd = [
                self.ffmpeg_path,
                '-y',
                '-loglevel', 'error',
                '-i', str(tmp_path),
                '-vn',
                '-ar', str(sr),
                '-ac', str(channels),
                '-b:a', '192k',
                str(output_path)
            ]
            subprocess.run(cmd, check=True)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
