import librosa
import numpy as np
from typing import List, Dict, Tuple, Optional
from .energy_detector import EnergyDetector
from .bpm_detector import BPMDetector
from .key_detector import KeyDetector


class SegmentFinder:
    def __init__(self, min_duration: float = 7.0, max_duration: float = 30.0):
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.energy_detector = EnergyDetector()
        self.bpm_detector = BPMDetector()
        self.key_detector = KeyDetector()

    def find_interesting_segments(
        self,
        audio: np.ndarray,
        sr: int,
        num_segments: int = 3,
        energy_analysis: Optional[Dict] = None,
        rhythm_analysis: Optional[Dict] = None,
        harmony_analysis: Optional[Dict] = None
    ) -> List[Dict]:
        if energy_analysis is None:
            energy_analysis = self.energy_detector.analyze_full_track(audio, sr)
        if rhythm_analysis is None:
            rhythm_analysis = self.bpm_detector.analyze_rhythm(audio, sr)
        if harmony_analysis is None:
            harmony_analysis = self.key_detector.analyze_harmony(audio, sr)
        
        high_energy_regions = energy_analysis.get('high_energy_regions') or \
            self.energy_detector.get_high_energy_regions(audio, sr, threshold=0.6, merge_gap=2.0)
        beat_times = rhythm_analysis['beat_times']
        measure_boundaries = rhythm_analysis['measure_boundaries']
        
        candidates = []
        
        for region_start, region_end in high_energy_regions:
            region_duration = region_end - region_start
            
            if region_duration < 3.0:
                continue
            
            segment_start = region_start
            segment_end = min(segment_start + self.max_duration, region_end)
            
            if segment_end - segment_start < self.min_duration:
                continue
            
            segment_start = self._align_to_beat(segment_start, beat_times)
            segment_end = self._align_to_beat(segment_end, beat_times)
            
            if segment_end - segment_start < self.min_duration:
                continue
            
            start_sample = int(segment_start * sr)
            end_sample = int(segment_end * sr)
            
            if start_sample >= len(audio) or end_sample > len(audio):
                continue
            
            segment_audio = audio[start_sample:end_sample]
            
            if len(segment_audio) == 0:
                continue
            
            hop_length = self.energy_detector.hop_length
            start_frame = max(start_sample // hop_length, 0)
            end_frame = min(end_sample // hop_length, len(energy_analysis['rms_energy']))
            
            if end_frame <= start_frame:
                continue
            
            interest_score = self.energy_detector.compute_segment_interest_score(
                energy_analysis['rms_energy'],
                energy_analysis['spectral_flux'],
                energy_analysis['onset_strength'],
                start_frame,
                end_frame
            )
            
            energy_level = np.mean(np.abs(segment_audio))
            
            candidates.append({
                'start_time': segment_start,
                'end_time': segment_end,
                'duration': segment_end - segment_start,
                'interest_score': interest_score,
                'energy_level': energy_level,
                'start_sample': start_sample,
                'end_sample': end_sample
            })
        
        candidates.sort(key=lambda x: x['interest_score'], reverse=True)
        
        selected_segments = self._select_diverse_segments(candidates, num_segments)
        
        for segment in selected_segments:
            segment['key'] = harmony_analysis['key']
            segment['mode'] = harmony_analysis['mode']
            segment['bpm'] = rhythm_analysis['bpm']
        
        return selected_segments

    def _align_to_beat(self, time: float, beat_times: np.ndarray) -> float:
        closest_beat = beat_times[np.argmin(np.abs(beat_times - time))]
        return closest_beat

    def _select_diverse_segments(self, candidates: List[Dict], num_segments: int) -> List[Dict]:
        if len(candidates) <= num_segments:
            return candidates
        
        selected = [candidates[0]]
        
        for _ in range(num_segments - 1):
            best_candidate = None
            best_score = -1
            
            for candidate in candidates:
                if candidate in selected:
                    continue
                
                min_distance = min(
                    abs(candidate['start_time'] - s['start_time'])
                    for s in selected
                )
                
                score = candidate['interest_score'] * (1 + min_distance / 60.0)
                
                if score > best_score:
                    best_score = score
                    best_candidate = candidate
            
            if best_candidate:
                selected.append(best_candidate)
        
        selected.sort(key=lambda x: x['start_time'])
        return selected

    def extract_segment_audio(self, audio: np.ndarray, segment: Dict) -> np.ndarray:
        return audio[segment['start_sample']:segment['end_sample']]

    def analyze_track_for_mixing(self, audio: np.ndarray, sr: int, num_segments: int = 3) -> Dict:
        energy_analysis = self.energy_detector.analyze_full_track(audio, sr)
        rhythm_analysis = self.bpm_detector.analyze_rhythm(audio, sr)
        harmony_analysis = self.key_detector.analyze_harmony(audio, sr)
        segments = self.find_interesting_segments(
            audio,
            sr,
            num_segments,
            energy_analysis=energy_analysis,
            rhythm_analysis=rhythm_analysis,
            harmony_analysis=harmony_analysis
        )
        
        return {
            'segments': segments,
            'energy_analysis': energy_analysis,
            'rhythm_analysis': rhythm_analysis,
            'harmony_analysis': harmony_analysis,
            'duration': len(audio) / sr
        }
