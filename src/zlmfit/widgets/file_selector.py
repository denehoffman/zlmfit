from pathlib import Path
from textual import on
from textual.message import Message
from textual.reactive import reactive
from textual.containers import (
    HorizontalScroll,
)
from textual.widgets import (
    Button,
    Label,
    Static,
)


from zlmfit.popups.file_menu import FileMenu


class FileSelector(Static):
    filepath: reactive[Path | None] = reactive(None)

    class FileSelected(Message):
        def __init__(self, file_selector: 'FileSelector', path: Path):
            self.file_selector = file_selector
            self.path = path
            super().__init__()

        @property
        def control(self) -> 'FileSelector':
            return self.file_selector

    def __init__(self, label: str, **kwargs):
        self.label = label
        super().__init__(**kwargs)

    def compose(self):
        yield Button('Open')
        yield Label(self.label, id='label')
        yield HorizontalScroll(Label(' ', id='path'), id='pathfield')

    def update_path(self, path: Path | None):
        if path:
            self.query_one('#path', Label).update(str(path))
            self.filepath = path

    def watch_filepath(self, path: Path | None):
        if path:
            self.post_message(FileSelector.FileSelected(self, path))

    @on(Button.Pressed)
    def open_pressed(self):
        self.app.push_screen(FileMenu(), self.update_path)
