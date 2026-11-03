"""Portable cross-process advisory lock for project writes and rate-limited workers."""
from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
import os
import time

@contextmanager
def file_lock(path: Path, timeout: float = 20.0):
    """Serialize Forge processes on Windows and POSIX; no lockless fallback."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    os.lseek(fd, 0, os.SEEK_SET)
    if os.fstat(fd).st_size == 0:
        os.write(fd, b"0")
    start = time.monotonic()
    locked = False
    try:
        while not locked:
            try:
                os.lseek(fd, 0, os.SEEK_SET)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
            except (BlockingIOError, OSError):
                if time.monotonic() - start >= timeout:
                    raise TimeoutError(f"Timed out obtaining local file lock: {path.name}")
                time.sleep(0.05)
        yield
    finally:
        if locked:
            os.lseek(fd, 0, os.SEEK_SET)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
