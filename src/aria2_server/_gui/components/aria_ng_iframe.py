import base64
from typing import Optional

from nicegui import ui
from typing_extensions import Self

__all__ = ("AriaNgIframe",)


class AriaNgIframe(ui.element, component="aria_ng_iframe.vue"):
    def __init__(
        self, *, aria_ng_src: str, interface: str, secret: Optional[str] = None
    ) -> None:
        """The iframe will automatically set `src` prop to `AriaNg set rpc setting command-api`.
            e.g. `${aria_ng_src}/#!/settings/rpc/set?protocol=${protocol}&host=${rpcHost}&port=${rpcPort}&interface=${rpcInterface}&secret=${secret}`
            see https://ariang.mayswind.net/command-api.html

        Args:
            aria_ng_src: AriaNg static files path, should not end with `/`, e.g. `/static/AriaNg`
            interface: aria2c interface, should not start or end with `/`, e.g. `api/aria2/jsonrpc`
            secret: aria2c rpc-secret, a utf-8 string, will be encoded to url-safe base64
        """
        super().__init__()
        self.aria_ng_src(aria_ng_src)
        self.interface(interface)
        if secret is not None:
            self.secret(secret)

    def aria_ng_src(self, aria_ng_src: str, /) -> Self:
        if aria_ng_src.endswith("/"):
            raise ValueError("aria_ng_src should not end with `/`")
        self.props(f"aria-ng-src={aria_ng_src}")
        return self

    def interface(self, interface: str, /) -> Self:
        if interface.startswith("/") or interface.endswith("/"):
            raise ValueError("interface should not start or end with `/`")
        self.props(f"interface={interface}")
        return self

    def secret(self, secret: str, /) -> Self:
        # NOTE: base64 encode is cpu bound, but usually secret is short,
        # so we don't need to use thread pool to do this.
        base64_secret = base64.urlsafe_b64encode(secret.encode("utf-8")).decode("utf-8")

        # NOTE: a example of `base64_secret` is `Vi12VWhPaDdDdHh6R3hSZm91TjlPd2lpYlBjSmUwS2NYWE1HYlB0a3k2Zw==`,
        # notice it ends with `==`, which is confilict syntax of `self.props`,
        # so we need use quote to wrap it.
        self.props(f"secret='{base64_secret}'")
        return self
