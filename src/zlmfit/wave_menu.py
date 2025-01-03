from textual import on
from textual.containers import Container, Horizontal, VerticalScroll
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Footer, Header, Label, RadioButton, RadioSet

from zlmfit.fit_data import FitData, Wave
from zlmfit.fit_menu import FitMenu


class WaveMenu(Screen):
    CSS_PATH = 'wave_menu.tcss'

    num_positive = reactive(int)
    num_negative = reactive(int)

    def __init__(self, fit_data: FitData):
        super().__init__()
        self.fit_data = fit_data

    def compose(self):
        yield Header()
        yield Footer()
        with Container(id='toplevel'):
            with VerticalScroll():
                yield Label('Positive Reflectivity', classes='toplabel')
                yield Label('Negative Reflectivity', classes='toplabel')
                yield Label('Waves', classes='selectedwavelabel')
                yield Label('Anchor', classes='anchorwavelabel')
                yield Label('Waves', classes='selectedwavelabel')
                yield Label('Anchor', classes='anchorwavelabel')
                with Container(id='pos_waves'):
                    yield Checkbox('L=0 M=0', id='wave_00p', classes='swave pos')
                    yield Checkbox('L=1 M=+1', id='wave_1p1p', classes='pwave pos')
                    yield Checkbox('L=1 M=0', id='wave_10p', classes='pwave pos')
                    yield Checkbox('L=1 M=-1', id='wave_1n1p', classes='pwave pos')
                    yield Checkbox('L=2 M=+2', id='wave_2p2p', classes='dwave pos')
                    yield Checkbox('L=2 M=+1', id='wave_2p1p', classes='dwave pos')
                    yield Checkbox('L=2 M=0', id='wave_20p', classes='dwave pos')
                    yield Checkbox('L=2 M=-1', id='wave_2n1p', classes='dwave pos')
                    yield Checkbox('L=2 M=-2', id='wave_2n2p', classes='dwave pos')
                    yield Checkbox('L=3 M=+2', id='wave_3p3p', classes='fwave pos')
                    yield Checkbox('L=3 M=+2', id='wave_3p2p', classes='fwave pos')
                    yield Checkbox('L=3 M=+1', id='wave_3p1p', classes='fwave pos')
                    yield Checkbox('L=3 M=0', id='wave_30p', classes='fwave pos')
                    yield Checkbox('L=3 M=-1', id='wave_3n1p', classes='fwave pos')
                    yield Checkbox('L=3 M=-2', id='wave_3n2p', classes='fwave pos')
                    yield Checkbox('L=3 M=-2', id='wave_3n3p', classes='fwave pos')
                with RadioSet(id='pos_anchor', disabled=True):
                    yield RadioButton(id='anchor_00p', classes='swave')
                    yield RadioButton(id='anchor_1p1p', classes='pwave', disabled=True)
                    yield RadioButton(id='anchor_10p', classes='pwave', disabled=True)
                    yield RadioButton(id='anchor_1n1p', classes='pwave', disabled=True)
                    yield RadioButton(id='anchor_2p2p', classes='dwave', disabled=True)
                    yield RadioButton(id='anchor_2p1p', classes='dwave', disabled=True)
                    yield RadioButton(id='anchor_20p', classes='dwave', disabled=True)
                    yield RadioButton(id='anchor_2n1p', classes='dwave', disabled=True)
                    yield RadioButton(id='anchor_2n2p', classes='dwave', disabled=True)
                    yield RadioButton(id='anchor_3p3p', classes='fwave', disabled=True)
                    yield RadioButton(id='anchor_3p2p', classes='fwave', disabled=True)
                    yield RadioButton(id='anchor_3p1p', classes='fwave', disabled=True)
                    yield RadioButton(id='anchor_30p', classes='fwave', disabled=True)
                    yield RadioButton(id='anchor_3n1p', classes='fwave', disabled=True)
                    yield RadioButton(id='anchor_3n2p', classes='fwave', disabled=True)
                    yield RadioButton(id='anchor_3n3p', classes='fwave', disabled=True)
                with Container(id='neg_waves'):
                    yield Checkbox('L=0 M=0', id='wave_00n', classes='swave neg')
                    yield Checkbox('L=1 M=+1', id='wave_1p1n', classes='pwave neg')
                    yield Checkbox('L=1 M=0', id='wave_10n', classes='pwave neg')
                    yield Checkbox('L=1 M=-1', id='wave_1n1n', classes='pwave neg')
                    yield Checkbox('L=2 M=+2', id='wave_2p2n', classes='dwave neg')
                    yield Checkbox('L=2 M=+1', id='wave_2p1n', classes='dwave neg')
                    yield Checkbox('L=2 M=0', id='wave_20n', classes='dwave neg')
                    yield Checkbox('L=2 M=-1', id='wave_2n1n', classes='dwave neg')
                    yield Checkbox('L=2 M=-2', id='wave_2n2n', classes='dwave neg')
                    yield Checkbox('L=3 M=+2', id='wave_3p3n', classes='fwave neg')
                    yield Checkbox('L=3 M=+2', id='wave_3p2n', classes='fwave neg')
                    yield Checkbox('L=3 M=+1', id='wave_3p1n', classes='fwave neg')
                    yield Checkbox('L=3 M=0', id='wave_30n', classes='fwave neg')
                    yield Checkbox('L=3 M=-1', id='wave_3n1n', classes='fwave neg')
                    yield Checkbox('L=3 M=-2', id='wave_3n2n', classes='fwave neg')
                    yield Checkbox('L=3 M=-2', id='wave_3n3n', classes='fwave neg')
                with RadioSet(id='neg_anchor', disabled=True):
                    yield RadioButton(id='anchor_00n', classes='swave')
                    yield RadioButton(id='anchor_1p1n', classes='pwave', disabled=True)
                    yield RadioButton(id='anchor_10n', classes='pwave', disabled=True)
                    yield RadioButton(id='anchor_1n1n', classes='pwave', disabled=True)
                    yield RadioButton(id='anchor_2p2n', classes='dwave', disabled=True)
                    yield RadioButton(id='anchor_2p1n', classes='dwave', disabled=True)
                    yield RadioButton(id='anchor_20n', classes='dwave', disabled=True)
                    yield RadioButton(id='anchor_2n1n', classes='dwave', disabled=True)
                    yield RadioButton(id='anchor_2n2n', classes='dwave', disabled=True)
                    yield RadioButton(id='anchor_3p3n', classes='fwave', disabled=True)
                    yield RadioButton(id='anchor_3p2n', classes='fwave', disabled=True)
                    yield RadioButton(id='anchor_3p1n', classes='fwave', disabled=True)
                    yield RadioButton(id='anchor_30n', classes='fwave', disabled=True)
                    yield RadioButton(id='anchor_3n1n', classes='fwave', disabled=True)
                    yield RadioButton(id='anchor_3n2n', classes='fwave', disabled=True)
                    yield RadioButton(id='anchor_3n3n', classes='fwave', disabled=True)
        with Horizontal():
            yield Button('Back', id='back')
            yield Button('Continue', id='continue', disabled=True)

    @on(Checkbox.Changed)
    def wave_selected(self, event: Checkbox.Changed):
        wave_id = event.checkbox.id
        if wave_id:
            anchor_id = wave_id.replace('wave', 'anchor')
            if event.value:
                radio_button = self.query_one(f'#{anchor_id}', RadioButton)
                radio_button.disabled = False
                if anchor_id.endswith('p'):
                    radioset = self.query_one('#pos_anchor', RadioSet)
                    if radioset.disabled:
                        radioset.disabled = False
                        radio_button.value = True
                else:
                    radioset = self.query_one('#neg_anchor', RadioSet)
                    if radioset.disabled:
                        radioset.disabled = False
                        radio_button.value = True
            else:
                radio_button = self.query_one(f'#{anchor_id}', RadioButton)
                if anchor_id.endswith('p') and radio_button.value:
                    radio_button.value = False
                    radio_button.disabled = True
                    pos_checkboxes = [
                        box for box in self.query('.pos') if isinstance(box, Checkbox)
                    ]
                    enabled_checkboxes = [box for box in pos_checkboxes if box.value]
                    if enabled_checkboxes:
                        first_enabled_checkbox_id = enabled_checkboxes[0].id
                        if first_enabled_checkbox_id:
                            first_enabled_radiobutton_id = (
                                first_enabled_checkbox_id.replace('wave', 'anchor')
                            )
                            self.query_one(
                                f'#{first_enabled_radiobutton_id}', RadioButton
                            ).value = True
                elif anchor_id.endswith('n') and radio_button.value:
                    radio_button.value = False
                    radio_button.disabled = True
                    neg_checkboxes = [
                        box for box in self.query('.neg') if isinstance(box, Checkbox)
                    ]
                    enabled_checkboxes = [box for box in neg_checkboxes if box.value]
                    if enabled_checkboxes:
                        first_enabled_checkbox_id = enabled_checkboxes[0].id
                        if first_enabled_checkbox_id:
                            first_enabled_radiobutton_id = (
                                first_enabled_checkbox_id.replace('wave', 'anchor')
                            )
                            self.query_one(
                                f'#{first_enabled_radiobutton_id}', RadioButton
                            ).value = True

        self.num_positive = len(
            [box for box in self.query('.pos') if isinstance(box, Checkbox) and box.value]
        )
        self.num_negative = len(
            [box for box in self.query('.neg') if isinstance(box, Checkbox) and box.value]
        )

    def watch_num_positive(self, num: int):
        if num == 0:
            radioset = self.query_one('#pos_anchor', RadioSet)
            radioset.disabled = True
            if self.num_negative == 0:
                self.query_one('#continue').disabled = True
        else:
            self.query_one('#continue').disabled = False

    def watch_num_negative(self, num: int):
        if num == 0:
            radioset = self.query_one('#neg_anchor', RadioSet)
            radioset.disabled = True
            if self.num_positive == 0:
                self.query_one('#continue').disabled = True
        else:
            self.query_one('#continue').disabled = False

    @on(Button.Pressed, '#back')
    def back_pressed(self):
        self.app.pop_screen()
        self.app.uninstall_screen(self)

    @on(Button.Pressed, '#continue')
    def continue_pressed(self):
        pos_waves = [
            Wave.from_id(box.id)
            for box in self.query('.pos')
            if isinstance(box, Checkbox) and box.value and box.id
        ]
        pos_anchor_index = None
        if pos_waves:
            pos_anchor_button = self.query_one('#pos_anchor', RadioSet).pressed_button
            assert pos_anchor_button is not None and pos_anchor_button.id is not None
            pos_anchor_wave = Wave.from_id(pos_anchor_button.id)
            pos_anchor_index = pos_waves.index(pos_anchor_wave)
        neg_waves = [
            Wave.from_id(box.id)
            for box in self.query('.neg')
            if isinstance(box, Checkbox) and box.value and box.id
        ]
        neg_anchor_index = None
        if neg_waves:
            neg_anchor_button = self.query_one('#neg_anchor', RadioSet).pressed_button
            assert neg_anchor_button is not None and neg_anchor_button.id is not None
            neg_anchor_wave = Wave.from_id(neg_anchor_button.id)
            neg_anchor_index = neg_waves.index(neg_anchor_wave)
        self.fit_data.pos_waves = pos_waves if pos_waves else None
        self.fit_data.pos_anchor = pos_anchor_index
        self.fit_data.neg_waves = neg_waves if neg_waves else None
        self.fit_data.neg_anchor = neg_anchor_index
        self.app.push_screen(FitMenu(self.fit_data))
