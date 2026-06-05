import numpy as np
from typing import Literal


def _envelope(curve: np.ndarray, audio: np.ndarray) -> np.ndarray:
    # Reshape a 1-D fade curve to broadcast over mono (N,) or stereo (N, C) audio.
    if audio.ndim > 1:
        return curve.reshape(-1, 1)
    return curve


class CrossfadeEngine:
    def __init__(self, fade_duration: float = 1.5, sample_rate: int = 22050):
        self.fade_duration = fade_duration
        self.sample_rate = sample_rate
        self.fade_samples = int(fade_duration * sample_rate)

    def _fade_length(self, audio1: np.ndarray, audio2: np.ndarray) -> int:
        return min(self.fade_samples, len(audio1), len(audio2))

    def linear_crossfade(self, audio1: np.ndarray, audio2: np.ndarray) -> np.ndarray:
        fade_len = self._fade_length(audio1, audio2)
        if fade_len <= 0:
            return np.concatenate([audio1, audio2], axis=0)

        fade_out = _envelope(np.linspace(1, 0, fade_len), audio1)
        fade_in = _envelope(np.linspace(0, 1, fade_len), audio2)

        crossfade_section = audio1[-fade_len:] * fade_out + audio2[:fade_len] * fade_in

        return np.concatenate([audio1[:-fade_len], crossfade_section, audio2[fade_len:]], axis=0)

    def equal_power_crossfade(self, audio1: np.ndarray, audio2: np.ndarray) -> np.ndarray:
        fade_len = self._fade_length(audio1, audio2)
        if fade_len <= 0:
            return np.concatenate([audio1, audio2], axis=0)

        t = np.linspace(0, np.pi / 2, fade_len)
        fade_out = _envelope(np.cos(t), audio1)
        fade_in = _envelope(np.sin(t), audio2)

        crossfade_section = audio1[-fade_len:] * fade_out + audio2[:fade_len] * fade_in

        return np.concatenate([audio1[:-fade_len], crossfade_section, audio2[fade_len:]], axis=0)

    def exponential_crossfade(self, audio1: np.ndarray, audio2: np.ndarray, curve: float = 2.0) -> np.ndarray:
        fade_len = self._fade_length(audio1, audio2)
        if fade_len <= 0:
            return np.concatenate([audio1, audio2], axis=0)

        t = np.linspace(0, 1, fade_len)
        fade_out = (1 - t) ** curve
        fade_in = t ** curve
        fade_out = _envelope(fade_out / np.max(fade_out), audio1)
        fade_in = _envelope(fade_in / np.max(fade_in), audio2)

        crossfade_section = audio1[-fade_len:] * fade_out + audio2[:fade_len] * fade_in

        return np.concatenate([audio1[:-fade_len], crossfade_section, audio2[fade_len:]], axis=0)

    def s_curve_crossfade(self, audio1: np.ndarray, audio2: np.ndarray) -> np.ndarray:
        fade_len = self._fade_length(audio1, audio2)
        if fade_len <= 0:
            return np.concatenate([audio1, audio2], axis=0)

        t = np.linspace(-np.pi / 2, np.pi / 2, fade_len)
        fade_out = _envelope(0.5 * (1 - np.sin(t)), audio1)
        fade_in = _envelope(0.5 * (1 + np.sin(t)), audio2)

        crossfade_section = audio1[-fade_len:] * fade_out + audio2[:fade_len] * fade_in

        return np.concatenate([audio1[:-fade_len], crossfade_section, audio2[fade_len:]], axis=0)

    def apply_crossfade(self, audio1: np.ndarray, audio2: np.ndarray,
                       method: Literal['linear', 'equal_power', 'exponential', 's_curve'] = 'equal_power') -> np.ndarray:
        if method == 'linear':
            return self.linear_crossfade(audio1, audio2)
        elif method == 'equal_power':
            return self.equal_power_crossfade(audio1, audio2)
        elif method == 'exponential':
            return self.exponential_crossfade(audio1, audio2)
        elif method == 's_curve':
            return self.s_curve_crossfade(audio1, audio2)
        else:
            return self.equal_power_crossfade(audio1, audio2)

    def concatenate_with_crossfade(self, audio_segments: list,
                                   method: Literal['linear', 'equal_power', 'exponential', 's_curve'] = 'equal_power') -> np.ndarray:
        if len(audio_segments) == 0:
            return np.array([])

        if len(audio_segments) == 1:
            return audio_segments[0]

        result = audio_segments[0]

        for segment in audio_segments[1:]:
            result = self.apply_crossfade(result, segment, method)

        return result

    def apply_fade_in(self, audio: np.ndarray, duration: float = 0.5) -> np.ndarray:
        fade_samples = int(duration * self.sample_rate)
        fade_samples = min(fade_samples, len(audio))
        if fade_samples <= 0:
            return audio

        fade_curve = _envelope(np.linspace(0, 1, fade_samples), audio)
        audio[:fade_samples] *= fade_curve

        return audio

    def apply_fade_out(self, audio: np.ndarray, duration: float = 0.5) -> np.ndarray:
        fade_samples = int(duration * self.sample_rate)
        fade_samples = min(fade_samples, len(audio))
        if fade_samples <= 0:
            return audio

        fade_curve = _envelope(np.linspace(1, 0, fade_samples), audio)
        audio[-fade_samples:] *= fade_curve

        return audio
