import numpy as np
from typing import List, Dict, Tuple, Optional
from .crossfade_engine import CrossfadeEngine
from App.audio_analysis.key_detector import KeyDetector
from App.utils.audio_loader import AudioLoader


class TransitionManager:
    def __init__(self, sample_rate: int = 22050, audio_tools: Optional[AudioLoader] = None,
                 enable_time_stretch: bool = False):
        self.sample_rate = sample_rate
        self.crossfade_engine = CrossfadeEngine(sample_rate=sample_rate)
        self.key_detector = KeyDetector()
        self.audio_tools = audio_tools or AudioLoader(sample_rate=sample_rate)
        # Phase-vocoder time-stretch matches BPM but adds an "underwater" artifact on
        # percussive music, so it is disabled by default to preserve audio quality.
        self.enable_time_stretch = enable_time_stretch
        self._min_stretch_rate = 0.85
        self._max_stretch_rate = 1.15

    def calculate_transition_cost(self, segment1: Dict, segment2: Dict) -> float:
        key_distance = self.key_detector.get_key_distance(
            (segment1['key'], segment1['mode']),
            (segment2['key'], segment2['mode'])
        )
        
        bpm_diff = abs(segment1['bpm'] - segment2['bpm']) / max(segment1['bpm'], segment2['bpm'])
        
        energy_diff = abs(segment1['energy_level'] - segment2['energy_level'])
        
        cost = (
            0.5 * key_distance +
            0.3 * bpm_diff +
            0.2 * energy_diff
        )
        
        return cost

    def find_optimal_order(self, segments: List[Dict]) -> List[Dict]:
        if len(segments) <= 1:
            return segments
        
        n = len(segments)
        cost_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    cost_matrix[i][j] = self.calculate_transition_cost(segments[i], segments[j])
        
        order = self._solve_tsp_greedy(cost_matrix)
        
        ordered_segments = [segments[i] for i in order]
        return ordered_segments

    def _solve_tsp_greedy(self, cost_matrix: np.ndarray) -> List[int]:
        n = len(cost_matrix)
        
        if n == 0:
            return []
        
        visited = [False] * n
        order = []
        
        current = 0
        order.append(current)
        visited[current] = True
        
        for _ in range(n - 1):
            min_cost = float('inf')
            next_city = -1
            
            for i in range(n):
                if not visited[i] and cost_matrix[current][i] < min_cost:
                    min_cost = cost_matrix[current][i]
                    next_city = i
            
            if next_city != -1:
                visited[next_city] = True
                order.append(next_city)
                current = next_city
        
        return order

    def create_transition(self, audio1: np.ndarray, audio2: np.ndarray, 
                         segment1: Dict, segment2: Dict) -> np.ndarray:
        key_distance = self.key_detector.get_key_distance(
            (segment1['key'], segment1['mode']),
            (segment2['key'], segment2['mode'])
        )
        
        bpm_diff = abs(segment1['bpm'] - segment2['bpm'])
        
        if key_distance > 0.4:
            fade_duration = 3.0
        elif bpm_diff > 10:
            fade_duration = 2.5
        else:
            fade_duration = 2.0
        
        self.crossfade_engine.fade_duration = fade_duration
        self.crossfade_engine.fade_samples = int(fade_duration * self.sample_rate)
        
        if key_distance > 0.5:
            method = 's_curve'
        else:
            method = 'equal_power'
        
        transition = self.crossfade_engine.apply_crossfade(audio1, audio2, method)
        
        return transition

    def create_mix(self, segments_with_audio: List[Tuple[Dict, np.ndarray]]) -> np.ndarray:
        if len(segments_with_audio) == 0:
            return np.array([])
        
        if len(segments_with_audio) == 1:
            return segments_with_audio[0][1]
        
        bpm_values = [s[0].get('bpm') for s in segments_with_audio if s[0].get('bpm')]
        target_bpm = float(np.median(bpm_values)) if bpm_values else None
        
        prepared_segments = []
        for segment, audio in segments_with_audio:
            prepared_audio = self._prepare_segment_audio(segment, audio, target_bpm)
            if len(prepared_audio) == 0:
                continue
            prepared_segments.append((segment, prepared_audio))
        
        if not prepared_segments:
            return np.array([])
        
        ordered_segments = self.find_optimal_order([s[0] for s in prepared_segments])
        
        segment_map = {id(seg): audio for seg, audio in prepared_segments}
        
        ordered_audio = [segment_map[id(s)] for s in ordered_segments]
        
        mix = self.crossfade_engine.concatenate_with_crossfade(ordered_audio, method='equal_power')
        
        mix = self.crossfade_engine.apply_fade_in(mix, duration=1.0)
        mix = self.crossfade_engine.apply_fade_out(mix, duration=1.0)
        
        return mix

    def _prepare_segment_audio(self, segment: Dict, audio: np.ndarray, target_bpm: Optional[float]) -> np.ndarray:
        prepared = np.ascontiguousarray(audio, dtype=np.float32)
        bpm = segment.get('bpm')
        if self.enable_time_stretch and target_bpm and bpm and bpm > 0:
            rate = target_bpm / bpm
            if rate > 0:
                rate = float(np.clip(rate, self._min_stretch_rate, self._max_stretch_rate))
                if abs(rate - 1.0) > 0.01:
                    prepared = self.audio_tools.time_stretch(prepared, rate)
        prepared = self._apply_soft_edges(prepared)
        return prepared

    def _apply_soft_edges(self, audio: np.ndarray, duration: float = 0.01) -> np.ndarray:
        if len(audio) == 0:
            return audio
        fade_samples = int(duration * self.sample_rate)
        fade_samples = max(1, min(fade_samples, len(audio) // 2))
        if fade_samples <= 0:
            return audio
        audio = audio.copy()
        fade_in_curve = np.linspace(0.0, 1.0, fade_samples, dtype=audio.dtype)
        fade_out_curve = fade_in_curve[::-1]
        if audio.ndim > 1:
            fade_in_curve = fade_in_curve.reshape(-1, 1)
            fade_out_curve = fade_out_curve.reshape(-1, 1)
        audio[:fade_samples] *= fade_in_curve
        audio[-fade_samples:] *= fade_out_curve
        return audio

    def get_transition_info(self, segment1: Dict, segment2: Dict) -> Dict:
        key_distance = self.key_detector.get_key_distance(
            (segment1['key'], segment1['mode']),
            (segment2['key'], segment2['mode'])
        )
        
        bpm_diff = abs(segment1['bpm'] - segment2['bpm'])
        
        compatibility = 1.0 - self.calculate_transition_cost(segment1, segment2)
        
        return {
            'key_distance': key_distance,
            'bpm_difference': bpm_diff,
            'compatibility_score': compatibility,
            'recommended_fade_duration': 2.0 + key_distance * 2.0,
            'transition_quality': 'excellent' if compatibility > 0.8 else 'good' if compatibility > 0.6 else 'fair'
        }
