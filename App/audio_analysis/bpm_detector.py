import librosa
import numpy as np
from typing import Tuple, Optional


class BPMDetector:
    def __init__(self, hop_length: int = 512):
        self.hop_length = hop_length

    def detect_bpm(self, audio: np.ndarray, sr: int) -> float:
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sr, hop_length=self.hop_length)
        return float(tempo)

    def detect_bpm_with_confidence(self, audio: np.ndarray, sr: int) -> Tuple[float, float]:
        tempo, beats = librosa.beat.beat_track(y=audio, sr=sr, hop_length=self.hop_length)
        
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr, hop_length=self.hop_length)
        pulse = librosa.beat.plp(onset_envelope=onset_env, sr=sr, hop_length=self.hop_length)
        
        beat_frames = librosa.util.match_events(beats, pulse)
        confidence = np.mean(pulse[beat_frames])
        
        return float(tempo), float(confidence)

    def get_beat_frames(self, audio: np.ndarray, sr: int, bpm: Optional[float] = None) -> np.ndarray:
        if bpm is None:
            bpm = self.detect_bpm(audio, sr)
        
        tempo, beat_frames = librosa.beat.beat_track(y=audio, sr=sr, hop_length=self.hop_length)
        return beat_frames

    def get_beat_times(self, audio: np.ndarray, sr: int, bpm: Optional[float] = None) -> np.ndarray:
        beat_frames = self.get_beat_frames(audio, sr, bpm)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=self.hop_length)
        return beat_times

    def get_downbeat_times(self, audio: np.ndarray, sr: int) -> np.ndarray:
        tempo, beat_frames = librosa.beat.beat_track(y=audio, sr=sr, hop_length=self.hop_length)
        
        try:
            dm = librosa.beat.beat_track(y=audio, sr=sr, hop_length=self.hop_length, trim=False)[1]
            downbeat_frames = librosa.beat.beat_track(y=audio, sr=sr, hop_length=self.hop_length)[1]
        except:
            downbeat_frames = beat_frames[::4]
        
        downbeat_times = librosa.frames_to_time(downbeat_frames, sr=sr, hop_length=self.hop_length)
        return downbeat_times

    def estimate_time_signature(self, audio: np.ndarray, sr: int) -> int:
        beat_frames = self.get_beat_frames(audio, sr)
        
        if len(beat_frames) < 8:
            return 4
        
        beat_intervals = np.diff(beat_frames)
        
        from scipy.signal import find_peaks
        hist, bin_edges = np.histogram(beat_intervals, bins=20, density=True)
        peaks, _ = find_peaks(hist, distance=2)
        
        if len(peaks) == 0:
            return 4
        
        dominant_interval = bin_edges[peaks[0]]
        
        time_signature = int(round(4 * dominant_interval / np.median(beat_intervals)))
        time_signature = max(3, min(7, time_signature))
        
        return time_signature

    def get_measure_boundaries(self, audio: np.ndarray, sr: int) -> np.ndarray:
        time_signature = self.estimate_time_signature(audio, sr)
        beat_frames = self.get_beat_frames(audio, sr)
        
        measure_frames = beat_frames[::time_signature]
        measure_times = librosa.frames_to_time(measure_frames, sr=sr, hop_length=self.hop_length)
        
        return measure_times

    def analyze_rhythm(self, audio: np.ndarray, sr: int) -> dict:
        bpm, confidence = self.detect_bpm_with_confidence(audio, sr)
        beat_frames = self.get_beat_frames(audio, sr)
        beat_times = self.get_beat_times(audio, sr)
        downbeat_times = self.get_downbeat_times(audio, sr)
        time_signature = self.estimate_time_signature(audio, sr)
        measure_boundaries = self.get_measure_boundaries(audio, sr)
        
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr, hop_length=self.hop_length)
        
        return {
            'bpm': bpm,
            'confidence': confidence,
            'beat_frames': beat_frames,
            'beat_times': beat_times,
            'downbeat_times': downbeat_times,
            'time_signature': time_signature,
            'measure_boundaries': measure_boundaries,
            'onset_envelope': onset_env,
            'num_beats': len(beat_frames),
            'duration': len(audio) / sr
        }
