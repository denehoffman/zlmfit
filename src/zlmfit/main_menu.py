from textual import on
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
)


from zlmfit.new_menu import NewMenu


class MainMenu(Screen):
    CSS_PATH = 'main_menu.tcss'

    def compose(self):
        yield Header()
        yield Footer()
        yield Button('New', variant='primary', id='new')
        yield Button('Open')
        yield Button('Help')
        yield Button('Options')
        yield Button('Exit', variant='error', id='exit')

    @on(Button.Pressed, '#new')
    def new_menu(self):
        self.app.install_screen(NewMenu(), 'new_menu')
        self.app.push_screen('new_menu')

    @on(Button.Pressed, '#exit')
    def exit_main_menu(self):
        self.app.exit()
