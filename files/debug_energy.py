import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from App.audio_analysis.energy_detector import EnergyDetector
from App.utils.audio_loader import AudioLoader


def main():
    file_path = "data/downloads/01 - Pitbull - Fun Official Video ft Chris Brown.mp3"
    
    loader = AudioLoader()
    audio, sr = loader.load_audio(file_path)
    
    detector = EnergyDetector()
    
    analysis = detector.analyze_full_track(audio, sr)
    
    print(f"Audio duration: {len(audio)/sr:.2f}s")
    print(f"Avg energy: {analysis['avg_energy']:.6f}")
    print(f"Max energy: {analysis['max_energy']:.6f}")
    print(f"Energy variance: {analysis['energy_variance']:.6f}")
    print(f"\nHigh energy regions (threshold=0.7): {len(analysis['high_energy_regions'])}")
    
    for i, (start, end) in enumerate(analysis['high_energy_regions'][:5]):
        print(f"  {i+1}. {start:.2f}s - {end:.2f}s ({end-start:.2f}s)")
    
    print(f"\nEnergy peaks: {len(analysis['energy_peaks'])}")
    
    print(f"\nTrying different thresholds:")
    for threshold in [0.5, 0.6, 0.7, 0.8]:
        regions = detector.get_high_energy_regions(audio, sr, threshold=threshold)
        print(f"  Threshold {threshold}: {len(regions)} regions")


if __name__ == "__main__":
    main()
