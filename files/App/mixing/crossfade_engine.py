import numpy as np
from typing import Tuple, Literal


class CrossfadeEngine:
    def __init__(self, fade_duration: float = 1.5, sample_rate: int = 22050):
        self.fade_duration = fade_duration
        self.sample_rate = sample_rate
        self.fade_samples = int(fade_duration * sample_rate)

    def linear_crossfade(self, audio1: np.ndarray, audio2: np.ndarray) -> np.ndarray:
        fade1_len = min(self.fade_samples, len(audio1))
        fade2_len = min(self.fade_samples, len(audio2))
        
        result = np.concatenate([audio1[:-fade1_len]])
        
        fade_out = np.linspace(1, 0, fade1_len)
        fade_in = np.linspace(0, 1, fade2_len)
        
        crossfade_section = audio1[-fade1_len:] * fade_out + audio2[:fade2_len] * fade_in
        
        result = np.concatenate([result, crossfade_section, audio2[fade2_len:]])
        
        return result

    def equal_power_crossfade(self, audio1: np.ndarray, audio2: np.ndarray) -> np.ndarray:
        fade1_len = min(self.fade_samples, len(audio1))
        fade2_len = min(self.fade_samples, len(audio2))
        
        result = np.concatenate([audio1[:-fade1_len]])
        
        t = np.linspace(0, np.pi / 2, fade1_len)
        fade_out = np.cos(t)
        fade_in = np.sin(t)
        
        crossfade_section = audio1[-fade1_len:] * fade_out + audio2[:fade2_len] * fade_in
        
        result = np.concatenate([result, crossfade_section, audio2[fade2_len:]])
        
        return result

    def exponential_crossfade(self, audio1: np.ndarray, audio2: np.ndarray, curve: float = 2.0) -> np.ndarray:
        fade1_len = min(self.fade_samples, len(audio1))
        fade2_len = min(self.fade_samples, len(audio2))
        
        result = np.concatenate([audio1[:-fade1_len]])
        
        t = np.linspace(0, 1, fade1_len)
        fade_out = (1 - t) ** curve
        fade_in = t ** curve
        
        fade_out = fade_out / np.max(fade_out)
        fade_in = fade_in / np.max(fade_in)
        
        crossfade_section = audio1[-fade1_len:] * fade_out + audio2[:fade2_len] * fade_in
        
        result = np.concatenate([result, crossfade_section, audio2[fade2_len:]])
        
        return result

    def s_curve_crossfade(self, audio1: np.ndarray, audio2: np.ndarray) -> np.ndarray:
        fade1_len = min(self.fade_samples, len(audio1))
        fade2_len = min(self.fade_samples, len(audio2))
        
        result = np.concatenate([audio1[:-fade1_len]])
        
        t = np.linspace(-np.pi / 2, np.pi / 2, fade1_len)
        fade_out = 0.5 * (1 - np.sin(t))
        fade_in = 0.5 * (1 + np.sin(t))
        
        crossfade_section = audio1[-fade1_len:] * fade_out + audio2[:fade2_len] * fade_in
        
        result = np.concatenate([result, crossfade_section, audio2[fade2_len:]])
        
        return result

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
        
        fade_curve = np.linspace(0, 1, fade_samples)
        audio[:fade_samples] *= fade_curve
        
        return audio

    def apply_fade_out(self, audio: np.ndarray, duration: float = 0.5) -> np.ndarray:
        fade_samples = int(duration * self.sample_rate)
        fade_samples = min(fade_samples, len(audio))
        
        fade_curve = np.linspace(1, 0, fade_samples)
        audio[-fade_samples:] *= fade_curve
        
        return audio
