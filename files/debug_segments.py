import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from App.core.app import ShorterMusicApp


def main():
    files = [
        "data/downloads/01 - Pitbull - Fun Official Video ft Chris Brown.mp3",
        "data/downloads/02 - Madonna - Bitch Im Madonna ft Nicki Minaj.mp3"
    ]
    
    app = ShorterMusicApp()
    
    for file_path in files:
        print(f"\n{'='*60}")
        print(f"Processing: {file_path}")
        print('='*60)
        
        try:
            result = app.process_single_track(file_path, num_segments=2)
            
            print(f"Analysis: {result['analysis']}")
            print(f"Segments found: {len(result['segments_with_audio'])}")
            
            for i, (segment, audio) in enumerate(result['segments_with_audio']):
                print(f"  Segment {i+1}: {segment['start_time']:.2f}s - {segment['end_time']:.2f}s (score: {segment['interest_score']:.2f})")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
