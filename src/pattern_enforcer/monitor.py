"""Active monitoring of pattern violations."""
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .validator import PatternValidator
from .errors import ValidationError


class FileChange:
    """Represents a file change event."""
    
    def __init__(self, path: str, event_type: str):
        self.path = path
        self.event_type = event_type
        self._original_content: str = None
    
    def backup(self) -> None:
        """Backup original file content."""
        try:
            with open(self.path, 'r') as f:
                self._original_content = f.read()
        except Exception:
            self._original_content = None
    
    def revert(self) -> None:
        """Revert file to original content."""
        if self._original_content is not None:
            try:
                with open(self.path, 'w') as f:
                    f.write(self._original_content)
            except Exception:
                pass


class FileSystemWatcher(FileSystemEventHandler):
    """Watches for file system changes."""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.observer = Observer()
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification event."""
        if event.is_directory:
            return
            
        if event.src_path.endswith('.py'):
            change = FileChange(event.src_path, 'modified')
            change.backup()
            asyncio.create_task(self.queue.put(change))
    
    def start(self, path: str) -> None:
        """Start watching directory."""
        self.observer.schedule(self, path, recursive=True)
        self.observer.start()
    
    def stop(self) -> None:
        """Stop watching directory."""
        self.observer.stop()
        self.observer.join()
    
    async def changes(self) -> AsyncGenerator[FileChange, None]:
        """Get stream of file changes."""
        while True:
            change = await self.queue.get()
            yield change
            self.queue.task_done()


class PatternMonitor:
    """Actively monitors for pattern violations."""
    
    def __init__(self, rules_file: str):
        """Initialize monitor with rules file."""
        self.validator = PatternValidator(rules_file)
        self.file_watcher = FileSystemWatcher()
        self._watching = False
        self._stats: Dict[str, Any] = {
            'violations_detected': 0,
            'files_reverted': 0,
            'files_validated': 0
        }
    
    async def watch_files(self, path: str) -> None:
        """Watch for file changes and validate patterns.
        
        Args:
            path: Directory to watch
            
        This method will:
        1. Start watching the directory
        2. Validate any changed files
        3. Revert invalid changes
        4. Track statistics
        """
        if self._watching:
            return
            
        self._watching = True
        self.file_watcher.start(path)
        
        try:
            async for file_change in self.file_watcher.changes():
                try:
                    # Validate file
                    result = self.validator.validate_file(file_change.path)
                    self._stats['files_validated'] += 1
                    
                    if not result.valid:
                        # Invalid changes detected
                        self._stats['violations_detected'] += 1
                        
                        # Revert changes
                        file_change.revert()
                        self._stats['files_reverted'] += 1
                        
                        print(f"Pattern violation in {file_change.path}")
                        print("Changes reverted")
                        for violation in result.violations:
                            print(f"- {violation}")
                    
                except ValidationError as e:
                    print(f"Validation error: {e}")
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    
        finally:
            self._watching = False
            self.file_watcher.stop()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return self._stats.copy()
    
    def is_watching(self) -> bool:
        """Check if monitor is active."""
        return self._watching 