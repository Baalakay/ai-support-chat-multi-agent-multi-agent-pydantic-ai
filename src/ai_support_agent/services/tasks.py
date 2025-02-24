"""Background tasks for the application."""

import asyncio
from datetime import datetime

from .config import settings

class BackgroundTasks:
    """Manager for background tasks."""

    def __init__(self):
        """Initialize background tasks."""
        self.tasks = []
        self.running = False

    async def start(self):
        """Start all background tasks."""
        if self.running:
            return

        self.running = True
        self.tasks = []  # No background tasks for now

    async def stop(self):
        """Stop all background tasks."""
        if not self.running:
            return

        self.running = False
        for task in self.tasks:
            task.cancel()

        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks = []

# Global background tasks instance
background_tasks = BackgroundTasks() 