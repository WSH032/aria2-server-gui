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
from typing import List, Union

from typing_extensions import Self

from aria2_server.config import GLOBAL_CONFIG

__all__ = ("Aria2Popen", "Aria2WatchdogLifespan", "Aria2WatchdogThread")


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
            is_running_more_than_once = False
            while not self._should_stop_watchdog:
                if is_running_more_than_once:
                    logging.warning(
                        "aria2c subprocess exited, perhaps the user closed it through the rpc interface, restarting..."
                    )
                aria2_popen = Aria2Popen()
                self.subprocess_deque.appendleft(aria2_popen)
                # NOTE: before starting a new subprocess,
                # must make sure the previous subprocess has been shutdown.
                returncode = aria2_popen.wait()
                if returncode != 0:
                    logging.warning(f"aria2c subprocess exited with code {returncode}")
                is_running_more_than_once = True

        # If the subclass overrides the constructor,
        # it must make sure to invoke the base class constructor (Thread.__init__())
        # before doing anything else to the thread.
        # see https://docs.python.org/3/library/threading.html#threading.Thread
        super().__init__(target=watchdog_for_aria2_popen)
        self._should_stop_watchdog = False
        self.subprocess_deque: "deque[Aria2Popen]" = deque(
            maxlen=subprocess_deque_maxlen
        )

    def stop_watchdog_only(self) -> None:
        self._should_stop_watchdog = True

    def get_current_subprocess(self) -> Union[Aria2Popen, None]:
        try:
            return self.subprocess_deque[0]
        except IndexError:
            return None

    def shutdown_current_subprocess(self) -> int:
        current_subprocess = self.get_current_subprocess()
        if current_subprocess is None:
            raise RuntimeError("No subprocess to shutdown")

        current_subprocess.shutdown_gracefully()
        return current_subprocess.wait()

    def stop_and_shutdown(self) -> None:
        """After call this method, had better call `join` to wait for the thread to exit."""
        self.stop_watchdog_only()
        self.shutdown_current_subprocess()


class Aria2WatchdogLifespan(AbstractContextManager["Aria2WatchdogLifespan"]):
    def __init__(self) -> None:
        # It is best not to set deque maxlen greater than 2 to avoid unexpected memory leaks
        self.aria2_watchdog_thread = Aria2WatchdogThread(2)

    def __enter__(self) -> Self:
        # TODO: check if aria2c is running before return, if not, raise an error.
        # maybe we can do it by trying to connect to aria2c rpc port by httpx.
        self.aria2_watchdog_thread.start()
        return self

    def __exit__(self, *_) -> None:
        self.aria2_watchdog_thread.stop_and_shutdown()
        self.aria2_watchdog_thread.join()
