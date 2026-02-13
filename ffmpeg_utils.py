"""
🔧 ffmpeg 유틸
- 시스템 PATH 에 ffmpeg 가 없어도 imageio-ffmpeg 바이너리를 자동 사용
- Windows 환경에서 설치/실행 실패를 줄이기 위한 보조 모듈
"""

import os
import subprocess
from shutil import which


def _is_working_ffmpeg(exe_path: str) -> bool:
    if not exe_path:
        return False
    try:
        subprocess.run(
            [exe_path, "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except Exception:
        return False


def ensure_ffmpeg():
    """사용 가능한 ffmpeg 경로를 찾아 반환합니다. 없으면 None."""
    # 1) 시스템 PATH 우선
    sys_ffmpeg = which("ffmpeg")
    if _is_working_ffmpeg(sys_ffmpeg):
        return sys_ffmpeg

    # 2) imageio-ffmpeg 번들 바이너리 시도
    try:
        import imageio_ffmpeg

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        if _is_working_ffmpeg(ffmpeg_exe):
            os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_exe
            return ffmpeg_exe
    except Exception:
        pass

    return None


def configure_pydub_ffmpeg():
    """pydub 가 ffmpeg 를 찾도록 converter 경로를 강제 설정합니다."""
    ffmpeg_exe = ensure_ffmpeg()
    if not ffmpeg_exe:
        return None

    try:
        from pydub import AudioSegment

        AudioSegment.converter = ffmpeg_exe
        AudioSegment.ffmpeg = ffmpeg_exe
        ffprobe = ffmpeg_exe.replace("ffmpeg", "ffprobe")
        if os.path.exists(ffprobe):
            AudioSegment.ffprobe = ffprobe
    except Exception:
        pass

    return ffmpeg_exe

