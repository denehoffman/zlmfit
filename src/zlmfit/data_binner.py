from pathlib import Path
from textual import on
from textual.css.query import NoMatches
from textual.containers import (
    Container,
    Horizontal,
    ScrollableContainer,
)
from textual.screen import Screen
from textual.validation import Function, Number
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    RadioButton,
    RadioSet,
)

import laddu as ld

from zlmfit.fit_data import FitData
from zlmfit.wave_menu import WaveMenu
from zlmfit.widgets.histogram import Histogram


class DataBinner(Screen):
    CSS_PATH = 'data_binner.tcss'

    def __init__(self, data_path: Path, accmc_path: Path, genmc_path: Path, **kwargs):
        super().__init__(**kwargs)
        self.data_path = data_path
        self.accmc_path = accmc_path
        self.genmc_path = genmc_path
        self.data = ld.open(str(data_path))
        self.accmc = ld.open(str(accmc_path))
        self.genmc = ld.open(str(genmc_path))
        self.fit_data = FitData(self.data, self.accmc, self.genmc)

    def compose(self):
        yield Header()
        yield Footer()
        with RadioSet():
            yield RadioButton('Data', value=True)
            yield RadioButton('AccMC')
            yield RadioButton('GenMC')
        yield ScrollableContainer(Histogram(self.data))
        with Container(id='settings'):
            yield Label('# Bins', id='bin_label')
            yield Input(
                str(40),
                type='integer',
                id='bins',
                validators=[
                    Number(
                        minimum=1,
                        maximum=None,
                        failure_description='Number of bins must be > 0',
                    )
                ],
                validate_on=['submitted'],
            )
            yield Label('Lower bound', id='lower_label')
            yield Input(
                str(1.0),
                type='number',
                id='lower',
                validators=[
                    Number(
                        minimum=0.0,
                        failure_description='Lower bound must be non-negative',
                    ),
                    Function(
                        self.validate_lower,
                        'Lower bound must be smaller than upper bound',
                    ),
                ],
                validate_on=['submitted'],
            )
            yield Label('Upper bound', id='upper_label')
            yield Input(
                str(2.0),
                type='number',
                id='upper',
                validators=[
                    Function(
                        self.validate_upper,
                        'Upper bound must be larger than lower bound',
                    ),
                ],
                validate_on=['submitted'],
            )
        with Horizontal(id='navigation'):
            yield Button('Back', id='back')
            yield Button('Continue', id='continue')

    def validate_lower(self, lower: str) -> bool:
        try:
            return self.query_one(Histogram).upper > float(lower)
        except NoMatches:
            return False

    def validate_upper(self, upper: str) -> bool:
        try:
            return self.query_one(Histogram).lower < float(upper)
        except NoMatches:
            return False

    @on(Input.Submitted, '#bins')
    def set_bins(self, bins: Input.Submitted):
        if int(bins.value) > 0:
            self.query_one(Histogram).bins = int(bins.value)

    @on(Input.Submitted, '#lower')
    def set_lower(self, lower: Input.Submitted):
        if self.validate_lower(lower.value):
            self.query_one(Histogram).lower = float(lower.value)

    @on(Input.Submitted, '#upper')
    def set_upper(self, upper: Input.Submitted):
        if self.validate_upper(upper.value):
            self.query_one(Histogram).upper = float(upper.value)

    @on(RadioSet.Changed)
    def switch_dataset(self, event: RadioSet.Changed):
        histogram = self.query_one(Histogram)
        if event.index == 0:
            histogram.data = self.data
        elif event.index == 1:
            histogram.data = self.accmc
        else:
            histogram.data = self.genmc

    @on(Button.Pressed, '#back')
    def back_pressed(self):
        self.app.pop_screen()
        self.app.uninstall_screen(self)

    @on(Button.Pressed, '#continue')
    def continue_pressed(self):
        self.fit_data.bins = int(self.query_one('#bins', Input).value)
        self.fit_data.lower = float(self.query_one('#lower', Input).value)
        self.fit_data.upper = float(self.query_one('#upper', Input).value)
        self.app.push_screen(WaveMenu(self.fit_data))
