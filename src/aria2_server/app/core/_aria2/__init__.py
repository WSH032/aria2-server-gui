import logging
import os
import shutil
import signal
import subprocess
import sys
import threading
from collections import deque
from contextlib import AbstractContextManager
from subprocess import Popen
from typing import List

from typing_extensions import Self

from aria2_server.config import GLOBAL_CONFIG

__all__ = ("Aria2Popen", "Aria2WatchdogLifespan", "Aria2WatchdogThread")


_DEFAULT_ARIA2_SHUTDOWN_TIMEOUT = 5


def _get_cmd_args() -> List[str]:
    aria2c_exec = shutil.which("aria2c")
    if aria2c_exec is None:
        raise RuntimeError("aria2c executable not found")

    # https://aria2.github.io/manual/en/html/aria2c.html
    logging.info(f"aria2c executable: {aria2c_exec}")
    assert (
        GLOBAL_CONFIG.aria2.enable_rpc == "true"
    ), "aria2.enable_rpc can only be set to 'ture'"
    cmd_args = [
        aria2c_exec,
        f"--rpc-listen-port={GLOBAL_CONFIG.aria2.rpc_listen_port}",
        f"--rpc-secret={GLOBAL_CONFIG.aria2.rpc_secret.get_secret_value()}",
        f"--enable-rpc={GLOBAL_CONFIG.aria2.enable_rpc}",
        f"--rpc-listen-all={GLOBAL_CONFIG.aria2.rpc_listen_all}",
        f"--rpc-secure={GLOBAL_CONFIG.aria2.rpc_secure}",
    ]

    if GLOBAL_CONFIG.aria2.conf_path is not None:
        cmd_args.append(f"--conf-path={GLOBAL_CONFIG.aria2.conf_path}")

    return cmd_args


class Aria2Popen(Popen[bytes]):
    """You don't need to instantiate this class directly, we expose this class for type hint."""

    # modified from: https://github.com/WSH032/aria2-wheel/blob/f11f10a4fc7c315a7432e26a3f17041945a8123e/README.md?plain=1#L92-L138

    def __init__(self) -> None:
        _cmd_args = _get_cmd_args()

        if sys.platform == "win32":
            super().__init__(
                args=_cmd_args,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            # TODO: prefer `process_group = value`, but the param is only available on Python 3.11+,
            # maybe we can use `preexec_fn = lambda: setpgid(0, value)`
            super().__init__(args=_cmd_args, start_new_session=True)

    def shutdown_gracefully(self) -> None:
        if sys.platform == "win32":
            # https://stackoverflow.com/questions/44124338/trying-to-implement-signal-ctrl-c-event-in-python3-6
            os.kill(self.pid, signal.CTRL_BREAK_EVENT)
        else:
            os.killpg(os.getpgid(self.pid), signal.SIGINT)


class Aria2WatchdogThread(threading.Thread):
    """You don't need to instantiate this class directly, we expose this class for type hint."""

    def __init__(self, subprocess_deque_maxlen: int) -> None:
        if subprocess_deque_maxlen < 1:
            raise ValueError("subprocess_deque_maxlen must be greater than 0")

        def watchdog_for_aria2_popen() -> None:
            _is_running_more_than_once = False
            while not self.should_stop_watchdog.is_set():
                if _is_running_more_than_once:
                    logging.warning(
                        "aria2c subprocess exited, perhaps the user closed it through the rpc interface, restarting..."
                    )

                with self._deque_read_write_lock:
                    # NOTE: make sure `Aria2Popen()` and `appendleft` are atomic
                    aria2_popen = Aria2Popen()
                    self._subprocess_deque.appendleft(aria2_popen)
                    # NOTE: set the event immediately after the first subprocess was put into the deque
                    if not self.started.is_set():
                        self.started.set()

                # NOTE: before starting a new subprocess,
                # must make sure the previous subprocess has been shutdown.
                # see https://docs.python.org/library/subprocess.html#subprocess.Popen.wait
                aria2_popen.communicate()  # Don't use timeout here, we expect it to shutdown normally
                returncode = aria2_popen.returncode
                if returncode != 0:
                    logging.warning(f"aria2c subprocess exited with code {returncode}")

                _is_running_more_than_once = True

        # If the subclass overrides the constructor,
        # it must make sure to invoke the base class constructor (Thread.__init__())
        # before doing anything else to the thread.
        # see https://docs.python.org/3/library/threading.html#threading.Thread
        super().__init__(target=watchdog_for_aria2_popen)

        self.should_stop_watchdog = threading.Event()
        self.started = threading.Event()
        """Set the event immediately after the first subprocess was put into the deque"""
        self._subprocess_deque: "deque[Aria2Popen]" = deque(
            maxlen=subprocess_deque_maxlen
        )
        """when read or write this deque, must hold the lock"""
        self._deque_read_write_lock = threading.RLock()

    def get_deque_copy(self) -> "deque[Aria2Popen]":
        with self._deque_read_write_lock:
            return self._subprocess_deque.copy()

    def get_current_subprocess(self) -> Aria2Popen:
        if not self.started.is_set():
            raise RuntimeError("The watchdog thread has not started yet")

        subprocess_deque = self.get_deque_copy()
        assert (
            len(subprocess_deque) > 0
        ), "after started, the subprocess deque should not be empty"
        return subprocess_deque[0]

    def shutdown_current_subprocess(self) -> int:
        current_subprocess = self.get_current_subprocess()

        # FIXME, TODO:
        # NOTE: we need use `while` loop to ensure the subprocess has been shutdown,
        # When subprocess is in the process of starting (i.e., not fully started yet),
        # it may not be possible to send a termination signal properly.
        while current_subprocess.poll() is None:
            current_subprocess.shutdown_gracefully()
            try:
                # see https://docs.python.org/library/subprocess.html#subprocess.Popen.wait
                current_subprocess.communicate(timeout=_DEFAULT_ARIA2_SHUTDOWN_TIMEOUT)
            except subprocess.TimeoutExpired:
                logging.warning(
                    "Timeout when shutdown aria2c subprocess, will retry again"
                )
        return current_subprocess.returncode

    def stop_and_shutdown(self) -> int:
        """Before call this method, make sure the first subprocess has been started.
        Check `self.started` event to ensure this.

        After call this method, had better call `join` to wait for the thread to exit."""
        # NOTE: stop watchdog first, then shutdown the current subprocess
        self.should_stop_watchdog.set()
        return self.shutdown_current_subprocess()


class Aria2WatchdogLifespan(AbstractContextManager["Aria2WatchdogLifespan"]):
    def __init__(self) -> None:
        # It is best not to set deque maxlen greater than 2 to avoid unexpected memory leaks
        self.aria2_watchdog_thread = Aria2WatchdogThread(2)

    def __enter__(self) -> Self:
        # TODO: check if aria2c is running before return, if not, raise an error.
        # maybe we can do it by trying to connect to aria2c rpc port by httpx.
        self.aria2_watchdog_thread.start()
        # NOTE: wait for the watchdog thread to start,
        # so that we can call `stop_and_shutdown` without RuntimeError
        # when exit immediately after enter.
        while not self.aria2_watchdog_thread.started.wait(timeout=1):
            if not self.aria2_watchdog_thread.is_alive():
                raise RuntimeError("The watchdog thread has exited unexpectedly")

        return self

    def __exit__(self, *_) -> None:
        self.aria2_watchdog_thread.stop_and_shutdown()
        self.aria2_watchdog_thread.join()
