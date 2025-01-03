from textual.app import App


from zlmfit.main_menu import MainMenu


class ZlmFitApp(App):
    BINDINGS = [
        ('d', 'toggle_dark', 'Toggle dark mode'),
    ]

    def on_mount(self):
        self.install_screen(MainMenu(), name='main_menu')
        self.push_screen('main_menu')


def main():
    ZlmFitApp().run()


if __name__ == '__main__':
    main()
