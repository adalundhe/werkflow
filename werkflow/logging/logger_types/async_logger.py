from __future__ import annotations
import os
import stat
import sys
import asyncio
import aiologger
from asyncio import Task
from typing import Any, Optional, TextIO
from aiologger.levels import LogLevel
from aiologger.formatters.base import Formatter
from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.records import LogRecord
from .logger_types import LoggerTypes


def _is_pipe_transport_supported(stream: Any) -> bool:
    if os.name == "nt":
        return False
    try:
        fd = stream.fileno()
    except (AttributeError, OSError, ValueError):
        return False
    try:
        mode = os.fstat(fd).st_mode
    except OSError:
        return False
    return stat.S_ISFIFO(mode) or stat.S_ISSOCK(mode) or stat.S_ISCHR(mode)


class AsyncSafeStreamHandler(AsyncStreamHandler):
    """Async stream handler that falls back to executor-backed writes for regular files and non-pipe streams."""

    def __init__(
        self,
        stream: Optional[Any] = None,
        level: LogLevel = LogLevel.NOTSET,
        formatter: Optional[Formatter] = None,
        owns_stream: bool = False,
        use_executor: bool = False,
    ) -> None:
        super().__init__(stream=stream, level=level, formatter=formatter)
        self._owns_stream = owns_stream
        self._use_executor = use_executor
        self._write_lock: Optional[asyncio.Lock] = None

    @property
    def initialized(self) -> bool:
        return self._use_executor or self.writer is not None

    def _sync_write(self, msg: str) -> None:
        target = self.stream
        if isinstance(target, TextIO) or hasattr(target, "encoding"):
            target.write(msg)
        else:
            target.write(msg.encode("utf-8"))
        target.flush()

    async def _emit_via_executor(self, msg: str) -> None:
        if self._write_lock is None:
            self._write_lock = asyncio.Lock()
        loop = asyncio.get_running_loop()
        async with self._write_lock:
            await loop.run_in_executor(None, self._sync_write, msg)

    async def emit(self, record: LogRecord) -> None:
        try:
            msg = self.formatter.format(record) + self.terminator
            if self._use_executor:
                await self._emit_via_executor(msg)
                return

            if self.writer is None:
                try:
                    self.writer = await self._init_writer()
                except (ValueError, OSError, NotImplementedError):
                    self._use_executor = True
                    await self._emit_via_executor(msg)
                    return

            self.writer.write(msg.encode("utf-8"))
            await self.writer.drain()
        except Exception as exc:
            await self.handle_error(record, exc)

    async def flush(self) -> None:
        if self._use_executor:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self.stream.flush)
            return
        if self.writer is not None:
            await self.writer.drain()

    async def close(self) -> None:
        if self._use_executor:
            try:
                self.stream.flush()
            except Exception:
                pass
            if self._owns_stream:
                try:
                    self.stream.close()
                except Exception:
                    pass
            return
        await super().close()
        if self._owns_stream:
            try:
                self.stream.close()
            except Exception:
                pass


class AsyncLogger(aiologger.Logger):

    def __init__(
        self, 
        logger_name: str=None, 
        logger_type: LoggerTypes=LoggerTypes.CONSOLE,
        log_level: LogLevel = LogLevel.INFO, 
        logger_enabled: bool=True
    ) -> None:
        super().__init__(name=logger_name, level=log_level)

        self.logger_name = logger_name
        self.logger_type = logger_type
        self.log_level = log_level
        self.logger_enabled = logger_enabled
        self.pattern = None
        self.datefmt_pattern = None

    def initialize(self, pattern: str, datefmt_pattern: str=None):

        self.pattern = pattern
        self.datefmt_pattern = datefmt_pattern

        target_stream = sys.stdout if sys.stdout is not None else sys.__stdout__
        use_pipe = _is_pipe_transport_supported(target_stream)
        owns_stream = False
        handler_stream: Any = target_stream

        if use_pipe:
            try:
                dup_fd = os.dup(target_stream.fileno())
                handler_stream = os.fdopen(dup_fd, "wb", buffering=0)
                owns_stream = True
            except OSError:
                use_pipe = False
                handler_stream = target_stream

        self.add_handler(
            AsyncSafeStreamHandler(
                stream=handler_stream,
                level=self.level,
                formatter=Formatter(pattern, datefmt=datefmt_pattern),
                owns_stream=owns_stream,
                use_executor=not use_pipe,
            )
        )

    def _make_log_task(self, level, msg, *args, **kwargs) -> Task:

        if self.logger_enabled:
            return super()._make_log_task(level, msg, *args, **kwargs)

        else:
            return asyncio.create_task(self._skip_task())

    async def _skip_task(self):
        return


