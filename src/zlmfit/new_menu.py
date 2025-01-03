from pathlib import Path
from textual import on
from textual.containers import (
    Horizontal,
    HorizontalScroll,
)
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
)


from zlmfit.data_binner import DataBinner
from zlmfit.widgets.file_selector import FileSelector


class NewMenu(Screen):
    any_missing = reactive(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_path: Path | None = None
        self.accmc_path: Path | None = None
        self.genmc_path: Path | None = None

    CSS_PATH = 'new_menu.tcss'

    def compose(self):
        yield Header()
        yield Footer()
        yield FileSelector('DATA  = ', id='data')
        yield FileSelector('ACCMC = ', id='accmc')
        yield FileSelector('GENMC = ', id='genmc')
        with Horizontal():
            yield Button('Back', id='back')
            yield Button('Continue', id='continue', disabled=True)

    def update_any_missing(self):
        self.any_missing = not (self.data_path and self.accmc_path and self.genmc_path)

    @on(FileSelector.FileSelected, '#data')
    def data_selected(self, event: FileSelector.FileSelected):
        self.data_path = event.path
        self.update_any_missing()

    @on(FileSelector.FileSelected, '#accmc')
    def accmc_selected(self, event: FileSelector.FileSelected):
        self.accmc_path = event.path
        self.update_any_missing()

    @on(FileSelector.FileSelected, '#genmc')
    def genmc_selected(self, event: FileSelector.FileSelected):
        self.genmc_path = event.path
        self.update_any_missing()

    def watch_any_missing(self, any_missing: bool):
        if not any_missing:
            self.query_one('#continue', Button).disabled = False

    @on(Button.Pressed, '#back')
    def back_pressed(self):
        self.app.pop_screen()
        self.app.uninstall_screen(self)

    @on(Button.Pressed, '#continue')
    def continue_pressed(self):
        file_selectors = self.query(FileSelector)
        data_path = file_selectors[0].filepath
        accmc_path = file_selectors[1].filepath
        genmc_path = file_selectors[2].filepath
        assert isinstance(data_path, Path)
        assert isinstance(accmc_path, Path)
        assert isinstance(genmc_path, Path)
        self.app.push_screen(DataBinner(data_path, accmc_path, genmc_path))
