import logging
import os
import shutil
import signal
import subprocess
import sys
from contextlib import contextmanager
from subprocess import Popen
from typing import Generator, List

from aria2_server.config import GLOBAL_CONFIG

__all__ = ("lifespan",)


def _get_cmd_args() -> List[str]:
    aria2c_exec = shutil.which("aria2c")
    if aria2c_exec is None:
        raise RuntimeError("aria2c executable not found")

    # https://aria2.github.io/manual/en/html/aria2c.html
    logging.info(f"aria2c executable: {aria2c_exec}")
    cmd_args = [
        aria2c_exec,
        "--enable-rpc",
        f"--rpc-listen-port={GLOBAL_CONFIG.server.aria2.rpc_listen_port}",
        f"--rpc-secret={GLOBAL_CONFIG.server.aria2.rpc_secret.get_secret_value()}",
    ]
    if GLOBAL_CONFIG.server.aria2.rpc_listen_all:
        cmd_args.append("--rpc-listen-all")
    if GLOBAL_CONFIG.server.aria2.conf_path is not None:
        cmd_args.append(f"--conf-path={GLOBAL_CONFIG.server.aria2.conf_path}")
    return cmd_args


@contextmanager
def lifespan() -> Generator[Popen[bytes], None, None]:
    # modified from: https://github.com/WSH032/aria2-wheel/blob/f11f10a4fc7c315a7432e26a3f17041945a8123e/README.md?plain=1#L92-L138
    _cmd_args = _get_cmd_args()

    if sys.platform == "win32":
        aria2_subprocess = Popen(
            args=_cmd_args,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        # TODO: prefer `process_group = value`, but the param is only available on Python 3.11+,
        # maybe we can use `preexec_fn = lambda: setpgid(0, value)`
        aria2_subprocess = Popen(args=_cmd_args, start_new_session=True)

    with aria2_subprocess:
        try:
            # TODO: check if aria2c is running before yield, if not, raise an error.
            # we can use `sleep(1)` and `aria2c_subprocess.poll() is None` to check;
            # or try to connect to aria2c rpc port by httpx.
            # TODO: create a background task to check if aria2c keep running,
            # if not, raise an error to shutdown the server.
            yield aria2_subprocess
        finally:
            # following code can shutdown the subprocess gracefully.
            if sys.platform == "win32":
                # https://stackoverflow.com/questions/44124338/trying-to-implement-signal-ctrl-c-event-in-python3-6
                os.kill(aria2_subprocess.pid, signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(aria2_subprocess.pid), signal.SIGINT)

            # we don't need to call `Popen.wait()`, because we use `with` statement.
