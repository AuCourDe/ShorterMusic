import librosa
import numpy as np
from typing import Tuple, List, Optional


class EnergyDetector:
    def __init__(self, frame_size: int = 2048, hop_length: int = 512):
        self.frame_size = frame_size
        self.hop_length = hop_length

    def compute_rms_energy(self, audio: np.ndarray) -> np.ndarray:
        rms = librosa.feature.rms(y=audio, frame_length=self.frame_size, hop_length=self.hop_length)[0]
        return rms

    def compute_spectral_flux(self, audio: np.ndarray, sr: int) -> np.ndarray:
        stft = librosa.stft(audio, hop_length=self.hop_length)
        magnitude = np.abs(stft)
        
        flux = np.diff(magnitude, axis=1)
        flux = np.maximum(flux, 0)
        flux = np.sum(flux, axis=0)
        
        return np.pad(flux, (0, 1), mode='constant')

    def compute_onset_strength(self, audio: np.ndarray, sr: int) -> np.ndarray:
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr, hop_length=self.hop_length)
        return onset_env

    def find_energy_peaks(self, energy: np.ndarray, prominence: float = 0.3, distance: int = 10) -> np.ndarray:
        from scipy.signal import find_peaks
        
        energy_normalized = (energy - np.min(energy)) / (np.max(energy) - np.min(energy) + 1e-10)
        peaks, _ = find_peaks(energy_normalized, prominence=prominence, distance=distance)
        
        return peaks

    def compute_segment_interest_score(
        self,
        rms_energy: np.ndarray,
        spectral_flux: np.ndarray,
        onset_strength: np.ndarray,
        start_idx: int,
        end_idx: int
    ) -> float:
        segment_energy = rms_energy[start_idx:end_idx]
        segment_flux = spectral_flux[start_idx:end_idx]
        segment_onset = onset_strength[start_idx:end_idx]
        
        avg_energy = np.mean(segment_energy)
        avg_flux = np.mean(segment_flux)
        avg_onset = np.mean(segment_onset)
        
        energy_var = np.var(segment_energy)
        flux_var = np.var(segment_flux)
        
        score = (
            0.4 * avg_energy +
            0.2 * avg_flux +
            0.2 * avg_onset +
            0.1 * energy_var +
            0.1 * flux_var
        )
        
        return score

    def get_high_energy_regions(
        self,
        audio: Optional[np.ndarray],
        sr: int,
        threshold: float = 0.7,
        merge_gap: float = 1.0,
        energy: Optional[np.ndarray] = None,
        frame_times: Optional[np.ndarray] = None
    ) -> List[Tuple[float, float]]:
        if energy is None:
            if audio is None:
                raise ValueError("audio or precomputed energy must be provided")
            energy = self.compute_rms_energy(audio)
        energy_normalized = (energy - np.min(energy)) / (np.max(energy) - np.min(energy) + 1e-10)
        
        high_energy_mask = energy_normalized >= threshold
        
        if frame_times is None:
            frame_times = librosa.frames_to_time(np.arange(len(energy)), sr=sr, hop_length=self.hop_length)
        
        regions = []
        in_region = False
        region_start = 0
        
        for i, is_high in enumerate(high_energy_mask):
            if is_high and not in_region:
                region_start = frame_times[i]
                in_region = True
            elif not is_high and in_region:
                region_end = frame_times[i]
                regions.append((region_start, region_end))
                in_region = False
        
        if in_region:
            regions.append((region_start, frame_times[-1]))
        
        if not regions:
            return regions
        
        merged_regions = [regions[0]]
        
        for current_start, current_end in regions[1:]:
            last_start, last_end = merged_regions[-1]
            
            if current_start - last_end <= merge_gap:
                merged_regions[-1] = (last_start, current_end)
            else:
                merged_regions.append((current_start, current_end))
        
        return merged_regions

    def analyze_full_track(self, audio: np.ndarray, sr: int) -> dict:
        rms = self.compute_rms_energy(audio)
        spectral_flux = self.compute_spectral_flux(audio, sr)
        onset_strength = self.compute_onset_strength(audio, sr)
        peaks = self.find_energy_peaks(rms)
        frame_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=self.hop_length)
        high_energy_regions = self.get_high_energy_regions(
            None,
            sr,
            energy=rms,
            frame_times=frame_times
        )
        
        return {
            'rms_energy': rms,
            'spectral_flux': spectral_flux,
            'onset_strength': onset_strength,
            'energy_peaks': peaks,
            'high_energy_regions': high_energy_regions,
            'frame_times': frame_times,
            'avg_energy': np.mean(rms),
            'max_energy': np.max(rms),
            'energy_variance': np.var(rms)
        }
