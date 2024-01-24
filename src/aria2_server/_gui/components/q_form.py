from typing import Literal, Optional

from nicegui import ui
from typing_extensions import Self

__all__ = (
    "EmailInput",
    "PasswordInput",
    "QForm",
    "StyledForm",
    "StyledInput",
    "StyledLabel",
    "SubmitButton",
)


class QForm(ui.element, component="q_form.vue"):
    def __init__(self) -> None:
        super().__init__()

    def action(self, action: str, /) -> Self:
        self.props(f"action={action}")
        return self

    def redirect_url(self, redirect_url: str, /) -> Self:
        self.props(f"redirect-url={redirect_url}")
        return self

    def method(self, method: Literal["POST", "PATCH"], /) -> Self:
        self.props(f"method={method}")
        return self

    def enctype(
        self,
        enctype: Literal["application/json", "application/x-www-form-urlencoded"],
        /,
    ) -> Self:
        self.props(f"enctype={enctype}")
        return self


class StyledForm(QForm):
    pass


StyledForm.default_classes("q-gutter-md")


class StyledInput(ui.input):
    pass


StyledInput.default_props("required lazy-rules")
StyledInput.default_classes("w-full")


class EmailInput(StyledInput):
    def __init__(self, *, label: str = "Email", name: str) -> None:
        super().__init__(label)
        # NOTE name of input is `username`, not `email
        # ref: https://fastapi-users.github.io/fastapi-users/12.1/usage/routes/
        #      https://developer.mozilla.org/en-US/docs/Learn/Forms/Your_first_form#sending_form_data_to_your_web_server
        self.props(f"type=email autocomplete=email name={name}")


_PwdAutocompleteType = Literal["current-password", "new-password", "on", "off"]


class PasswordInput(StyledInput):
    def __init__(
        self,
        *,
        label: str = "Password",
        name: str,
        pwd_autocomplete: _PwdAutocompleteType = "on",
    ) -> None:
        super().__init__(label, password=True, password_toggle_button=True)
        self.props(f"type=password autocomplete={pwd_autocomplete} name={name}")


class SubmitButton(ui.button):
    def __init__(
        self,
        text: str = "",
        color: Optional[str] = "primary",
        icon: Optional[str] = None,
    ) -> None:
        super().__init__(text=text, color=color, icon=icon)
        self.props("type=submit")


class StyledLabel(ui.label):
    pass


StyledLabel.default_classes("text-xl font-semibold")
