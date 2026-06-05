import librosa
import numpy as np
from typing import Tuple, Optional, List


class KeyDetector:
    def __init__(self):
        self.key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.modes = ['major', 'minor']

    def detect_key(self, audio: np.ndarray, sr: int) -> Tuple[str, str]:
        chromagram = librosa.feature.chroma_stft(y=audio, sr=sr)
        
        chroma_mean = np.mean(chromagram, axis=1)
        
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        major_scores = []
        minor_scores = []
        
        for i in range(12):
            major_rotated = np.roll(major_profile, i)
            minor_rotated = np.roll(minor_profile, i)
            
            major_score = np.corrcoef(chroma_mean, major_rotated)[0, 1]
            minor_score = np.corrcoef(chroma_mean, minor_rotated)[0, 1]
            
            major_scores.append(major_score)
            minor_scores.append(minor_score)
        
        major_scores = np.array(major_scores)
        minor_scores = np.array(minor_scores)
        
        best_major_idx = np.argmax(major_scores)
        best_minor_idx = np.argmax(minor_scores)
        
        if major_scores[best_major_idx] > minor_scores[best_minor_idx]:
            return self.key_names[best_major_idx], 'major'
        else:
            return self.key_names[best_minor_idx], 'minor'

    def get_key_distance(self, key1: Tuple[str, str], key2: Tuple[str, str]) -> float:
        key1_idx = self.key_names.index(key1[0])
        key2_idx = self.key_names.index(key2[0])
        
        circle_distance = min(abs(key1_idx - key2_idx), 12 - abs(key1_idx - key2_idx))
        
        mode_penalty = 0 if key1[1] == key2[1] else 0.3
        
        distance = circle_distance / 12.0 + mode_penalty
        
        return distance

    def get_compatible_keys(self, key: Tuple[str, str], max_distance: float = 0.3) -> List[Tuple[str, str]]:
        compatible = []
        
        for key_name in self.key_names:
            for mode in self.modes:
                test_key = (key_name, mode)
                distance = self.get_key_distance(key, test_key)
                if distance <= max_distance:
                    compatible.append(test_key)
        
        return compatible

    def analyze_harmony(self, audio: np.ndarray, sr: int) -> dict:
        chromagram = librosa.feature.chroma_stft(y=audio, sr=sr)
        key, mode = self.detect_key(audio, sr)
        
        chroma_variance = np.var(chromagram, axis=1)
        chroma_mean = np.mean(chromagram, axis=1)
        
        tonal_centroid = np.argmax(chroma_mean)
        
        return {
            'key': key,
            'mode': mode,
            'chromagram': chromagram,
            'chroma_mean': chroma_mean,
            'chroma_variance': chroma_variance,
            'tonal_centroid': tonal_centroid
        }
