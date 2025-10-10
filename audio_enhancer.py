#!/usr/bin/env python3
"""
Audio Enhancement Module for Downloaded Videos
Enhances audio quality, volume, and applies audio normalization
"""

import os
import subprocess
import logging
import tempfile
import json
from typing import Optional

logger = logging.getLogger(__name__)

class AudioEnhancer:
    """Class to enhance audio quality of downloaded videos"""
    
    def __init__(self):
        self.temp_files = []
    
    def enhance_video_audio(self, input_path: str) -> Optional[str]:
        """
        Enhance audio quality of a video file
        
        Args:
            input_path: Path to input video file
            
        Returns:
            Path to enhanced video file or None if failed
        """
        try:
            if not os.path.exists(input_path):
                logger.error(f"Input file does not exist: {input_path}")
                return None
            
            # Check if video has audio stream
            if not self._has_audio_stream(input_path):
                logger.info("Video has no audio stream, returning original")
                return input_path
            
            # Create output path
            dir_name = os.path.dirname(input_path)
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(dir_name, f"{base_name}_enhanced.mp4")
            
            # Apply audio enhancement
            if self._apply_audio_enhancement(input_path, output_path):
                # Verify the enhanced file is valid
                if self._verify_enhanced_video(output_path):
                    # Replace original with enhanced version
                    os.replace(output_path, input_path)
                    logger.info(f"Audio enhancement successful: {input_path}")
                    return input_path
                else:
                    # Enhanced file is invalid, clean up and return original
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    logger.warning("Enhanced video is invalid, returning original")
                    return input_path
            else:
                logger.warning("Audio enhancement failed, returning original")
                return input_path
                
        except Exception as e:
            logger.error(f"Error enhancing audio: {e}")
            return input_path
    
    def _has_audio_stream(self, video_path: str) -> bool:
        """Check if video has audio stream"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                audio_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'audio']
                return len(audio_streams) > 0
            
            return False
            
        except Exception as e:
            logger.warning(f"Could not check audio streams: {e}")
            return True  # Assume has audio if we can't check
    
    def _apply_audio_enhancement(self, input_path: str, output_path: str) -> bool:
        """Apply audio enhancement using ffmpeg"""
        try:
            # Get video duration for progress tracking
            duration = self._get_video_duration(input_path)
            
            # Build ffmpeg command with comprehensive audio enhancement
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:v', 'copy',  # Copy video stream without re-encoding
                '-c:a', 'aac',   # High quality AAC audio
                '-b:a', '320k',  # Maximum audio bitrate
                '-ar', '48000',  # High sample rate
                '-ac', '2',      # Stereo output
                # Audio filters for enhancement
                '-af', (
                    'volume=2.5,'  # Boost volume by 2.5x
                    'highpass=f=30,'  # Remove low frequency noise
                    'lowpass=f=18000,'  # Remove high frequency noise
                    'equalizer=f=60:t=h:width=30:g=3,'  # Boost deep bass
                    'equalizer=f=200:t=h:width=100:g=2,'  # Boost bass
                    'equalizer=f=1000:t=h:width=500:g=1.5,'  # Boost low mids
                    'equalizer=f=3000:t=h:width=1000:g=2,'  # Boost speech frequencies
                    'equalizer=f=8000:t=h:width=2000:g=1.5,'  # Boost presence
                    'compand=attacks=0.05:decays=0.1:points=-80/-80|-40/-20|-20/-10|-10/-5|0/0,'  # Stronger compression
                    'alimiter=level_in=2:level_out=0.9:limit=0.95,'  # Prevent clipping
                    'loudnorm=I=-14:TP=-1:LRA=7:measured_I=-20:measured_LRA=15:measured_TP=-3:linear=true'  # Aggressive loudness normalization
                ),
                '-movflags', '+faststart',  # Optimize for streaming
                output_path
            ]
            
            logger.info(f"Applying audio enhancement with ffmpeg...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info("Audio enhancement completed successfully")
                return True
            else:
                logger.error(f"Audio enhancement failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Audio enhancement timed out")
            return False
        except Exception as e:
            logger.error(f"Error in audio enhancement: {e}")
            return False
    
    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return float(data.get('format', {}).get('duration', 0))
            
        except Exception as e:
            logger.warning(f"Could not get video duration: {e}")
        
        return 0.0
    
    def _verify_enhanced_video(self, video_path: str) -> bool:
        """Verify that enhanced video is valid"""
        try:
            if not os.path.exists(video_path):
                return False
                
            # Check file size
            file_size = os.path.getsize(video_path)
            if file_size < 1024:  # Less than 1KB
                return False
            
            # Use ffprobe to verify
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', '-show_format', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Check for video and audio streams
                video_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'video']
                audio_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'audio']
                
                if video_streams and audio_streams:
                    duration = float(data.get('format', {}).get('duration', 0))
                    if duration > 0:
                        logger.info(f"Enhanced video verified: {duration}s, {len(video_streams)}v/{len(audio_streams)}a streams")
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Could not verify enhanced video: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not clean up {file_path}: {e}")
        self.temp_files.clear() 