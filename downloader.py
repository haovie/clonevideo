#!/usr/bin/env python3
"""
Optimized video downloader using yt-dlp with browser cookies and gallery-dl for TikTok photos
"""

import os
import yt_dlp
import tempfile
import logging
import glob
import subprocess
import json
import shutil
from typing import Optional
from config import DOWNLOAD_DIR, MAX_FILE_SIZE, DOWNLOAD_TIMEOUT
from audio_enhancer import AudioEnhancer

logger = logging.getLogger(__name__)

class GalleryDLDownloader:
    """Download TikTok photo slideshows using gallery-dl"""
    
    def __init__(self):
        pass
    
    def download_tiktok_photos(self, url: str, output_dir: str) -> bool:
        """Download TikTok photos using gallery-dl command line interface"""
        try:
            # Use subprocess to call gallery-dl directly (more reliable)
            cmd = [
                'gallery-dl',
                '--dest', output_dir,
                '--filename', '{num:>02}_{id}.{extension}',
                url
            ]
            
            logger.info(f"Running gallery-dl command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                # Check if files were downloaded
                downloaded_files = []
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.mp3', '.m4a', '.wav', '.aac')):
                            downloaded_files.append(os.path.join(root, file))
                
                logger.info(f"Gallery-dl downloaded {len(downloaded_files)} files from TikTok")
                return len(downloaded_files) > 0
            else:
                logger.error(f"Gallery-dl failed with exit code {result.returncode}")
                logger.error(f"STDERR: {result.stderr}")
                return False
            
        except subprocess.TimeoutExpired:
            logger.error("Gallery-dl timed out")
            return False
        except FileNotFoundError:
            logger.error("gallery-dl command not found. Install with: pip install gallery-dl")
            return False
        except Exception as e:
            logger.error(f"Gallery-dl download failed: {e}")
            return False

class SlideshowCreator:
    """Create video slideshow from TikTok photos with high quality audio"""
    
    def __init__(self):
        self.temp_files = []
    
    def create_slideshow(self, temp_dir: str) -> Optional[str]:
        """Create slideshow from photos and audio in temp_dir"""
        try:
            # Find all image and audio files recursively
            image_files = []
            audio_files = []
            
            logger.info(f"Searching for media files in: {temp_dir}")
            
            for root, dirs, files in os.walk(temp_dir):
                logger.debug(f"Checking directory: {root}")
                for file in files:
                    file_path = os.path.join(root, file)
                    logger.debug(f"Found file: {file_path}")
                    
                    if os.path.isfile(file_path):
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            image_files.append(file_path)
                            logger.info(f"Found image: {file}")
                        elif file.lower().endswith(('.mp3', '.m4a', '.wav', '.aac')):
                            audio_files.append(file_path)
                            logger.info(f"Found audio: {file}")
            
            logger.info(f"Total found: {len(image_files)} images, {len(audio_files)} audio files")
            
            if not image_files:
                logger.error(f"No images found in {temp_dir}")
                # List all files for debugging
                all_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        all_files.append(os.path.join(root, file))
                logger.error(f"All files found: {all_files}")
                return None
            
            # Sort files to ensure consistent order (by filename)
            image_files.sort(key=lambda x: os.path.basename(x))
            audio_files.sort(key=lambda x: os.path.basename(x))
            
            logger.info(f"Creating slideshow with {len(image_files)} images and {len(audio_files)} audio files")
            
            # Create slideshow output path
            output_path = os.path.join(temp_dir, "tiktok_slideshow.mp4")
            
            # If we have audio, create slideshow with audio
            if audio_files:
                return self._create_slideshow_with_audio(image_files, audio_files[0], output_path)
            else:
                # Create slideshow without audio (fallback)
                logger.warning("No audio found, creating slideshow without audio")
                return self._create_slideshow_no_audio(image_files, output_path)
                
        except Exception as e:
            logger.error(f"Error creating slideshow: {e}")
            return None
    
    def _create_slideshow_with_audio(self, image_files: list, audio_file: str, output_path: str) -> Optional[str]:
        """Create slideshow with audio using ffmpeg"""
        try:
            # Get audio duration for slideshow timing
            audio_duration = self._get_audio_duration(audio_file)
            if audio_duration <= 0:
                audio_duration = 15  # Fallback to 15 seconds for TikTok
            
            # Calculate duration per image (minimum 1 second, maximum based on audio)
            duration_per_image = max(1.0, audio_duration / len(image_files))
            
            # Build ffmpeg command for high-quality slideshow
            cmd = self._build_ffmpeg_command_with_audio(image_files, audio_file, output_path, duration_per_image)
            
            # Run ffmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"TikTok slideshow created with audio: {output_path}")
                return output_path
            else:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating slideshow with audio: {e}")
            return None
    
    def _create_slideshow_no_audio(self, image_files: list, output_path: str) -> Optional[str]:
        """Create slideshow without audio as fallback"""
        try:
            duration_per_image = 2.0  # 2 seconds per image
            
            cmd = self._build_ffmpeg_command_no_audio(image_files, output_path, duration_per_image)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"TikTok slideshow created without audio: {output_path}")
                return output_path
            else:
                logger.error(f"FFmpeg failed (no audio): {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating slideshow without audio: {e}")
            return None
    
    def _get_audio_duration(self, audio_file: str) -> float:
        """Get audio duration using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', audio_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                duration = float(data.get('format', {}).get('duration', 0))
                return duration
            
        except Exception as e:
            logger.warning(f"Could not get audio duration: {e}")
        
        return 15.0  # Default fallback for TikTok (typical length)
    
    def _build_ffmpeg_command_with_audio(self, image_files: list, audio_file: str, output_path: str, duration_per_image: float) -> list:
        """Build ffmpeg command for high-quality slideshow with audio"""
        
        # Create input list for ffmpeg
        inputs = []
        filter_complex = []
        
        # Add each image as input with duration
        for i, img in enumerate(image_files):
            inputs.extend(['-loop', '1', '-t', str(duration_per_image), '-i', img])
        
        # Add audio input
        inputs.extend(['-i', audio_file])
        
        # Create filter complex for smooth transitions and TikTok-style format
        video_filters = []
        for i in range(len(image_files)):
            # Scale each image to TikTok format (9:16 aspect ratio, 1080x1920)
            video_filters.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30[v{i}]")
        
        # Add fade transitions between images
        if len(image_files) > 1:
            # Create fade transitions
            for i in range(len(image_files)):
                if i > 0:
                    video_filters.append(f"[v{i}]fade=t=in:st=0:d=0.5[v{i}fade]")
                    video_filters.append(f"[v{i}fade]fade=t=out:st={duration_per_image-0.5}:d=0.5[v{i}final]")
                else:
                    video_filters.append(f"[v{i}]fade=t=out:st={duration_per_image-0.5}:d=0.5[v{i}final]")
            
            # Concatenate all video streams with fade
            concat_inputs = ''.join([f"[v{i}final]" for i in range(len(image_files))])
        else:
            concat_inputs = '[v0]'
        
        video_filters.append(f"{concat_inputs}concat=n={len(image_files)}:v=1:a=0[outv]")
        
        filter_complex = ';'.join(video_filters)
        
        # Build complete command with TikTok-optimized settings and enhanced audio
        cmd = ['ffmpeg', '-y'] + inputs + [
            '-filter_complex', filter_complex,
            '-map', '[outv]',
            '-map', f'{len(image_files)}:a',  # Map audio from last input
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',  # Good quality for TikTok
            '-c:a', 'aac',
            '-b:a', '320k',  # High quality bitrate
            '-ar', '48000',  # High quality sample rate
            '-af', 'volume=3.0,equalizer=f=60:t=h:width=30:g=3,equalizer=f=200:t=h:width=100:g=2,equalizer=f=3000:t=h:width=1000:g=2,compand=attacks=0.05:decays=0.1:points=-80/-80|-40/-20|-20/-10|-10/-5|0/0,alimiter=level_in=2:level_out=0.9:limit=0.95,loudnorm=I=-14:TP=-1:LRA=7',  # Enhanced audio processing
            '-shortest',  # End when shortest stream ends
            '-movflags', '+faststart',  # Optimize for streaming
            '-pix_fmt', 'yuv420p',  # Ensure compatibility
            output_path
        ]
        
        return cmd
    
    def _build_ffmpeg_command_no_audio(self, image_files: list, output_path: str, duration_per_image: float) -> list:
        """Build ffmpeg command for slideshow without audio"""
        
        inputs = []
        for i, img in enumerate(image_files):
            inputs.extend(['-loop', '1', '-t', str(duration_per_image), '-i', img])
        
        filter_complex = []
        for i in range(len(image_files)):
            filter_complex.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30[v{i}]")
        
        concat_inputs = ''.join([f"[v{i}]" for i in range(len(image_files))])
        filter_complex.append(f"{concat_inputs}concat=n={len(image_files)}:v=1:a=0[outv]")
        
        cmd = ['ffmpeg', '-y'] + inputs + [
            '-filter_complex', ';'.join(filter_complex),
            '-map', '[outv]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            output_path
        ]
        
        return cmd
    
    def cleanup(self):
        """Clean up temporary files"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not clean up {file_path}: {e}")
        self.temp_files.clear()

class VideoDownloader:
    def __init__(self):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        # Initialize gallery-dl downloader for TikTok photos
        self.gallery_dl = GalleryDLDownloader()
        
        # Initialize audio enhancer
        self.audio_enhancer = AudioEnhancer()
        
        # Optimized yt-dlp options with high quality audio/video
        self.ydl_opts = {
            # Prioritize best video + best audio quality, merge if needed
            'format': 'bestvideo[filesize<2G]+bestaudio[ext=m4a]/bestvideo[filesize<2G]+bestaudio/best[filesize<2G]/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'socket_timeout': 60,
            'retries': 3,
            'fragment_retries': 3,
            # Audio quality settings
            'audio_quality': 0,  # Best audio quality (0 = best, 9 = worst)
            'prefer_ffmpeg': True,  # Use ffmpeg for better quality merging
            # Video quality settings
            'writeinfojson': False,  # Skip info files
            'writesubtitles': False,  # Skip subtitles for faster processing
            'writeautomaticsub': False,
            # Ensure good quality merging
            'merge_output_format': 'mp4',  # Ensure mp4 output for better compatibility
            # Post-processing to ensure quality
            'postprocessors': [
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                },
            ],
        }
        
    
    def _is_subpath(self, path: str, base: str) -> bool:
        """Return True if path is inside base directory."""
        try:
            path = os.path.realpath(path)
            base = os.path.realpath(base)
            return os.path.commonpath([path, base]) == base
        except Exception:
            return False

    def _get_top_temp_dir(self, any_path_inside: str) -> Optional[str]:
        """Ascend from a file/dir path to the immediate child directory under DOWNLOAD_DIR."""
        try:
            current = os.path.realpath(any_path_inside)
            if os.path.isfile(current):
                current = os.path.dirname(current)
            download_dir_real = os.path.realpath(DOWNLOAD_DIR)
            # If current is not under DOWNLOAD_DIR, do nothing
            if not self._is_subpath(current, download_dir_real):
                return None
            # Walk up until parent is DOWNLOAD_DIR
            while True:
                parent = os.path.dirname(current)
                if parent == download_dir_real or parent == current:
                    break
                current = parent
            # Ensure we don't return DOWNLOAD_DIR itself
            if os.path.realpath(current) == download_dir_real:
                return None
            return current
        except Exception:
            return None

    def _safe_rmtree(self, path: str):
        """Safely remove a directory tree if it's under DOWNLOAD_DIR and not the root itself."""
        try:
            if not path:
                return
            if self._is_subpath(path, DOWNLOAD_DIR) and os.path.realpath(path) != os.path.realpath(DOWNLOAD_DIR):
                shutil.rmtree(path, ignore_errors=True)
        except Exception:
            # Best-effort cleanup; ignore errors
            pass

    def download_video(self, url: str) -> Optional[str]:
        """Download video with specialized handling for TikTok photos"""
        temp_dir = tempfile.mkdtemp(dir=DOWNLOAD_DIR)
        
        # Enhanced TikTok photo detection and handling
        if self._is_tiktok_photo_url(url):
            logger.info("Detected TikTok photo URL, using gallery-dl for slideshow creation...")
            return self._download_tiktok_slideshow(url, temp_dir)
        
        # Regular video download methods
        # Method 1: Standard download
        file_path = self._try_standard_download(url, temp_dir)
        if file_path:
            # Enhance audio quality
            enhanced_path = self.audio_enhancer.enhance_video_audio(file_path)
            return enhanced_path if enhanced_path else file_path
        
        logger.error("Download failed")
        return None
    
    def _is_tiktok_photo_url(self, url: str) -> bool:
        """Enhanced detection for TikTok photo URLs with short URL resolution"""
        if 'tiktok.com' not in url:
            return False
        
        # Check if it's already a long URL with /photo/
        if '/photo/' in url or 'slideshow' in url.lower():
            return True
        
        # If it's a short URL (vt.tiktok.com or vm.tiktok.com), resolve it
        if 'vt.tiktok.com' in url or 'vm.tiktok.com' in url:
            try:
                import requests
                response = requests.head(url, allow_redirects=True, timeout=10)
                resolved_url = response.url
                logger.info(f"Resolved TikTok URL {url} -> {resolved_url}")
                return '/photo/' in resolved_url or 'slideshow' in resolved_url.lower()
            except Exception as e:
                logger.warning(f"Could not resolve TikTok URL {url}: {e}")
                return False
        
        return False
    
    def _download_tiktok_slideshow(self, url: str, temp_dir: str) -> Optional[str]:
        """Download TikTok slideshow using gallery-dl and create video"""
        try:
            # Try gallery-dl first for better photo extraction
            gallery_success = self.gallery_dl.download_tiktok_photos(url, temp_dir)
            
            if gallery_success:
                # Create slideshow from downloaded photos
                return self._create_slideshow_from_photos(temp_dir)
            else:
                logger.info("Gallery-dl failed, falling back to yt-dlp method...")
                # Fallback to modified yt-dlp approach
                return self._download_tiktok_photos_fallback(url, temp_dir)
                
        except Exception as e:
            logger.error(f"Error in TikTok slideshow download: {e}")
            return self._download_tiktok_photos_fallback(url, temp_dir)
    
    def _download_tiktok_photos_fallback(self, url: str, temp_dir: str) -> Optional[str]:
        """Fallback method for TikTok photos using yt-dlp"""
        try:
            # Convert /photo/ URLs to /video/ for yt-dlp compatibility
            video_url = url.replace('/photo/', '/video/')
            
            # Enhanced yt-dlp options for TikTok photos
            opts = self.ydl_opts.copy()
            opts['outtmpl'] = os.path.join(temp_dir, '%(title)s.%(ext)s')
            opts['writeinfojson'] = True
            opts['format'] = 'bestvideo[filesize<2G]+bestaudio[ext=m4a]/bestvideo[filesize<2G]+bestaudio/best[filesize<2G]/best'  # High quality audio priority
            opts['audio_quality'] = 0  # Ensure best audio quality for slideshow
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([video_url])
                
            return self._find_downloaded_file(temp_dir)
            
        except Exception as e:
            logger.error(f"Error downloading TikTok photos with yt-dlp fallback: {e}")
            return None
    
    def _try_standard_download(self, url: str, temp_dir: str) -> Optional[str]:
        """Try standard download with enhanced TikTok URL resolution"""
        try:
            # Resolve TikTok short URLs first
            resolved_url = url
            if 'vt.tiktok.com' in url or 'vm.tiktok.com' in url:
                logger.info(f"Resolving TikTok short URL for download: {url}")
                try:
                    import requests
                    response = requests.head(url, allow_redirects=True, timeout=15)
                    resolved_url = response.url
                    logger.info(f"Resolved TikTok URL for download: {url} -> {resolved_url}")
                except Exception as e:
                    logger.warning(f"Could not resolve TikTok short URL for download {url}: {e}")
                    # Continue with original URL as fallback
            
            opts = self.ydl_opts.copy()
            opts['outtmpl'] = os.path.join(temp_dir, '%(title)s.%(ext)s')
            # Add better timeout and retry settings for TikTok
            opts['socket_timeout'] = 60
            opts['retries'] = 3
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([resolved_url])
                return self._find_downloaded_file(temp_dir)
                
        except Exception as e:
            logger.warning(f"Standard download failed: {e}")
            return None
    
    
    
    
    def _find_downloaded_file(self, temp_dir: str) -> Optional[str]:
        """Find downloaded file or create slideshow if multiple images found"""
        try:
            all_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    all_files.append(os.path.join(root, file))
            
            # Separate images and audio files
            image_files = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            audio_files = [f for f in all_files if f.lower().endswith(('.mp3', '.m4a', '.wav', '.aac'))]
            video_files = [f for f in all_files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))]
            
            logger.info(f"Found in {temp_dir}: {len(image_files)} images, {len(audio_files)} audio, {len(video_files)} videos")
            
            # If we already have a video file, use it (yt-dlp may have created it)
            if video_files:
                # Enhance audio quality for regular videos
                enhanced_path = self.audio_enhancer.enhance_video_audio(video_files[0])
                return enhanced_path if enhanced_path else video_files[0]
            
            # Check if this is a TikTok photo download (multiple images + audio)
            if len(image_files) > 1:
                logger.info(f"Detected TikTok photo slideshow: {len(image_files)} images, {len(audio_files)} audio files")
                return self._create_slideshow_from_photos(temp_dir)
            
            # Regular single file download - return the first available file
            if all_files:
                return all_files[0]
                
            return None
            
        except Exception as e:
            logger.error(f"Error finding downloaded file: {e}")
            return None
    
    def _create_slideshow_from_photos(self, temp_dir: str) -> Optional[str]:
        """Create slideshow from TikTok photos"""
        try:
            creator = SlideshowCreator()
            slideshow_path = creator.create_slideshow(temp_dir)
            creator.cleanup()
            
            if slideshow_path and os.path.exists(slideshow_path):
                # Verify the created video is valid
                if self._verify_video_file(slideshow_path):
                    logger.info(f"TikTok slideshow created successfully: {slideshow_path}")
                    return slideshow_path
                else:
                    logger.error(f"Created slideshow is invalid: {slideshow_path}")
                    os.remove(slideshow_path)
            
            logger.error("Failed to create TikTok slideshow")
            # Fallback: look for any existing video file
            return self._find_any_video_file(temp_dir)
                
        except Exception as e:
            logger.error(f"Error creating TikTok slideshow: {e}")
            # Fallback: look for any existing video file
            return self._find_any_video_file(temp_dir)
    
    def _verify_video_file(self, video_path: str) -> bool:
        """Verify that a video file is valid and playable"""
        try:
            # Check file size (should be > 1KB for a valid video)
            if not os.path.exists(video_path):
                return False
                
            file_size = os.path.getsize(video_path)
            if file_size < 1024:  # Less than 1KB is likely invalid
                logger.warning(f"Video file too small: {file_size} bytes")
                return False
            
            # Use ffprobe to verify video structure
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', '-show_format', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                # Check if it has video stream
                video_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'video']
                
                if video_streams:
                    duration = float(data.get('format', {}).get('duration', 0))
                    if duration > 0:
                        logger.info(f"Video verified: {duration}s duration, {len(video_streams)} video streams")
                        return True
                    else:
                        logger.warning("Video has no duration")
                        return False
                else:
                    logger.warning("Video has no video streams")
                    return False
            else:
                logger.warning(f"ffprobe failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.warning(f"Could not verify video file: {e}")
            return False
    
    def _find_any_video_file(self, temp_dir: str) -> Optional[str]:
        """Find any valid video file in the directory as fallback"""
        try:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                        file_path = os.path.join(root, file)
                        if self._verify_video_file(file_path):
                            logger.info(f"Found valid fallback video: {file_path}")
                            return file_path
            
            logger.warning("No valid video files found in temp directory")
            return None
            
        except Exception as e:
            logger.error(f"Error finding fallback video: {e}")
            return None
    
    def download_tiktok_images(self, url: str) -> Optional[list]:
        """Download TikTok slideshow images and return their file paths (sorted).
        
        Returns a list of absolute image paths, or None on failure.
        """
        try:
            if not self._is_tiktok_photo_url(url):
                logger.info("download_tiktok_images called for non-TikTok-photo URL")
                return None
            
            temp_dir = tempfile.mkdtemp(dir=DOWNLOAD_DIR)
            logger.info(f"Created temp dir for TikTok images: {temp_dir}")
            
            # Prefer gallery-dl for robust image extraction
            gallery_success = self.gallery_dl.download_tiktok_photos(url, temp_dir)
            if not gallery_success:
                logger.info("Gallery-dl failed for images, trying yt-dlp fallback…")
                fallback = self._download_tiktok_photos_fallback(url, temp_dir)
                if not fallback:
                    logger.error("Both gallery-dl and yt-dlp fallback failed for TikTok images")
            
            # Collect images
            image_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        image_files.append(os.path.join(root, file))
            
            if not image_files:
                logger.error(f"No images found in {temp_dir} for TikTok slideshow")
                # Best effort cleanup of empty directory
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
                return None
            
            image_files.sort(key=lambda p: os.path.basename(p))
            logger.info(f"Downloaded {len(image_files)} TikTok slideshow images")
            return image_files
        except Exception as e:
            logger.error(f"Error downloading TikTok images: {e}")
            return None
    
    def cleanup_file(self, file_path: str):
        """Clean up downloaded file and its temp directory tree under downloads."""
        try:
            # Remove the file itself
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            # Remove the top-level temp directory created under DOWNLOAD_DIR
            top_temp_dir = self._get_top_temp_dir(file_path)
            if top_temp_dir and os.path.isdir(top_temp_dir):
                self._safe_rmtree(top_temp_dir)
            # Also attempt to remove now-empty direct parent directories up to DOWNLOAD_DIR
            parent = os.path.dirname(os.path.realpath(file_path)) if file_path else None
            download_dir_real = os.path.realpath(DOWNLOAD_DIR)
            while parent and parent != download_dir_real and parent != '/':
                try:
                    if os.path.isdir(parent) and not os.listdir(parent):
                        os.rmdir(parent)
                    else:
                        break
                except Exception:
                    break
                parent = os.path.dirname(parent)
            # Clean up audio enhancer temp files
            self.audio_enhancer.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up: {e}")
    
    def cleanup_files(self, file_paths: list):
        """Clean up multiple files and their temp directory tree under downloads."""
        try:
            if not file_paths:
                return
            # Remove files
            for path in file_paths:
                try:
                    if path and os.path.exists(path):
                        os.remove(path)
                except Exception as e:
                    logger.warning(f"Could not remove file {path}: {e}")

            # Determine the top-level temp directory from the first file
            top_temp_dir = self._get_top_temp_dir(file_paths[0])
            if top_temp_dir and os.path.isdir(top_temp_dir):
                self._safe_rmtree(top_temp_dir)

            # Clean up audio enhancer temp files
            self.audio_enhancer.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")

    def get_video_info(self, url: str) -> Optional[dict]:
        """Get video information with enhanced TikTok photo handling and robust error handling"""
        original_url = url
        
        try:
            # Step 1: Resolve TikTok short URLs first
            if 'vt.tiktok.com' in url or 'vm.tiktok.com' in url:
                logger.info(f"Resolving TikTok short URL: {url}")
                try:
                    import requests
                    response = requests.head(url, allow_redirects=True, timeout=15)
                    resolved_url = response.url
                    logger.info(f"Resolved TikTok URL: {url} -> {resolved_url}")
                    url = resolved_url
                except Exception as e:
                    logger.warning(f"Could not resolve TikTok short URL {url}: {e}")
                    # Continue with original URL as fallback
            
            # Step 2: Enhanced TikTok photo URL handling
            if self._is_tiktok_photo_url(url):
                logger.info("Detected TikTok photo URL for info extraction...")
                # Try to convert to video URL for yt-dlp compatibility
                url = url.replace('/photo/', '/video/')
            
            # Step 3: Try multiple methods for getting video info
            
            # Try standard extraction
            info = self._try_standard_info_extraction(url)
            if info:
                return self._format_video_info(info, original_url)
            
            # Fallback for TikTok - create basic info from URL
            if 'tiktok.com' in url:
                logger.info("Extraction failed, creating fallback info for TikTok...")
                return self._create_fallback_tiktok_info(original_url)
            
            logger.error(f"Failed to extract video info from: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            # For TikTok URLs, try to provide fallback info even on error
            if 'tiktok.com' in original_url:
                return self._create_fallback_tiktok_info(original_url)
            return None
    
    def _try_standard_info_extraction(self, url: str) -> Optional[dict]:
        """Try standard yt-dlp info extraction without cookies"""
        try:
            info_opts = {
                'quiet': True,
                'format': 'bestvideo[filesize<2G]+bestaudio[ext=m4a]/bestvideo[filesize<2G]+bestaudio/best[filesize<2G]/best',
                'socket_timeout': 30,
                'retries': 2
            }
            
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
                
        except Exception as e:
            logger.warning(f"Standard info extraction failed: {e}")
            return None
    
    
    def _create_fallback_tiktok_info(self, url: str) -> dict:
        """Create fallback info for TikTok URLs when extraction fails"""
        try:
            # Extract basic info from URL
            username = "Unknown"
            video_id = "Unknown"
            
            if '@' in url and '/video/' in url:
                try:
                    username = url.split('@')[1].split('/')[0]
                    video_id = url.split('/video/')[1].split('?')[0].split('/')[0]
                except:
                    pass
            elif '/photo/' in url:
                try:
                    username = url.split('@')[1].split('/')[0] if '@' in url else "Unknown"
                    video_id = url.split('/photo/')[1].split('?')[0].split('/')[0]
                except:
                    pass
            
            # Determine if it's a photo slideshow
            is_photo = self._is_tiktok_photo_url(url)
            
            title = f"📸 TikTok Slideshow by @{username}" if is_photo else f"🎵 TikTok Video by @{username}"
            
            logger.info(f"Created fallback TikTok info: {title}")
            
            return {
                'title': title,
                'uploader': f"@{username}",
                'duration': 15 if is_photo else 30,  # Estimate duration
                'filesize': 10 * 1024 * 1024,  # Estimate 10MB
                'description': f"TikTok content from @{username} (ID: {video_id})"
            }
            
        except Exception as e:
            logger.warning(f"Error creating fallback TikTok info: {e}")
            return {
                'title': '🎵 TikTok Video',
                'uploader': 'TikTok User',
                'duration': 30,
                'filesize': 10 * 1024 * 1024,
                'description': 'TikTok content'
            }
    
    def _format_video_info(self, info: dict, original_url: str) -> dict:
        """Format video info with enhanced title handling"""
        # Enhanced title handling for TikTok photos
        title = info.get('title', 'Unknown')
        if self._is_tiktok_photo_url(original_url):
            title = f"📸 TikTok Slideshow: {title}"
        elif 'tiktok.com' in original_url:
            title = f"🎵 {title}"
        
        # Get filesize from the selected format
        filesize = 0
        if 'requested_formats' in info:
            # Multiple formats (video + audio)
            for fmt in info['requested_formats']:
                if fmt.get('filesize'):
                    filesize += fmt['filesize']
        elif info.get('filesize'):
            # Single format
            filesize = info['filesize']
        
        # For TikTok photos, estimate slideshow filesize (typically larger due to processing)
        if self._is_tiktok_photo_url(original_url) and filesize > 0:
            filesize = int(filesize * 1.5)  # Estimate 50% larger for slideshow processing
        
        return {
            'title': title,
            'uploader': info.get('uploader', 'Unknown'),
            'duration': info.get('duration', 0),
            'filesize': filesize,
            'description': info.get('description', '')[:200] + '...' if info.get('description') else ''
        }