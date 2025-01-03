from pathlib import Path
from typing import Iterable
from textual import on
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DirectoryTree,
)


class ParquetDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.is_dir() or path.suffix == '.parquet']


class FileMenu(ModalScreen[Path]):
    def compose(self):
        yield Button('Parent Directory', id='parent')
        yield ParquetDirectoryTree(Path.cwd().resolve())
        yield Button('Back', id='back')

    @on(Button.Pressed, '#parent')
    def parent_pressed(self):
        tree = self.query_one(ParquetDirectoryTree)
        current_path = Path(tree.path)
        tree.path = current_path.parent.resolve()
        tree.reload()

    @on(Button.Pressed, '#back')
    def back_pressed(self):
        self.dismiss(None)

    @on(DirectoryTree.FileSelected)
    def file_selected(self, file: DirectoryTree.FileSelected):
        self.dismiss(file.path)
