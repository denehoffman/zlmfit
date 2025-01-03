from pathlib import Path
from textual import on
from textual.containers import Container, Horizontal
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.screen import Screen
from textual.validation import Number
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label

from zlmfit.fit_data import FitData
from zlmfit.fitting_screen import FittingScreen

INVALID_NITERS = 0b00000001
INVALID_PATH = 0b00000010
INVALID_NBOOT = 0b00000100
INVALID_NWALKERS = 0b00001000
INVALID_SIGMA = 0b00010000
INVALID_NTAU = 0b00100000
INVALID_DTAU = 0b01000000
INVALID_EXTN = 0b10000000


class FitMenu(Screen):
    CSS_PATH = 'fit_menu.tcss'

    niters = reactive(20)
    nboot = reactive(20)
    nwalkers = reactive(20)
    sigma = reactive(0.1)
    ntau = reactive(20)
    dtau = reactive(0.05)
    output_name = reactive('fit.zlmfit')
    invalid = reactive(0)

    def __init__(self, fit_data: FitData, **kwargs):
        self.fit_data = fit_data
        super().__init__(**kwargs)

    def on_mount(self):
        self.invalid

    def compose(self):
        yield Header()
        yield Footer()
        with Container(id='iter_info'):
            yield Label('Run')
            yield Input(
                str(self.niters),
                validators=[Number(minimum=1)],
                id='niters',
                type='integer',
            )
            yield Label('randomly initialized fits per bin')
        with Container(id='bootstrap_info'):
            yield Checkbox('Bootstrap', id='bootstrap')
            with Container(id='bootstrap_settings', classes='hidden'):
                yield Input(
                    str(self.nboot),
                    validators=[Number(minimum=1)],
                    id='nboot',
                    type='integer',
                )
                yield Label('bootstrapped fits', id='bootstrap_label')
        with Container(id='mcmc_info'):
            yield Checkbox('Run MCMC', id='mcmc')
            with Container(id='mcmc_settings', classes='hidden'):
                with Container(id='walker_settings'):
                    yield Input(
                        str(self.nwalkers),
                        validators=[Number(minimum=1)],
                        id='nwalkers',
                        type='integer',
                    )
                    yield Label('walkers, distributed normally with σ = ')
                    yield Input(
                        str(self.sigma),
                        validators=[Number(minimum=0)],
                        id='sigma',
                        type='number',
                    )
                with Container(id='converge_settings'):
                    yield Label('Converge with steps > ', id='converge_label')
                    yield Input(
                        str(self.ntau),
                        validators=[Number(minimum=1)],
                        id='ntau',
                        type='integer',
                    )
                    yield Label('τ and Δτ/τ < ', id='tau_label')
                    yield Input(
                        str(self.dtau),
                        validators=[Number(minimum=0.0)],
                        id='dtau',
                        type='number',
                    )
        with Container(id='output_info'):
            yield Label('Output Name:')
            yield Input('fit.zlmfit', id='fit_path')
            with Container(id='pathcheck'):
                yield Label(
                    '(file already exists)', id='file_exists', classes='hidden error'
                )
                yield Label(
                    '(must end in .zlmfit)',
                    id='wrong_extension',
                    classes='hidden error',
                )
        with Horizontal(id='navigation'):
            yield Button('Back', id='back')
            yield Button('Fit', id='fit', variant='success')

    def watch_invalid(self, invalid: int):
        try:
            self.query_one('#fit', Button).disabled = bool(invalid)
            if invalid & INVALID_EXTN != 0:
                self.query_one('#wrong_extension').remove_class('hidden')
            else:
                self.query_one('#wrong_extension').add_class('hidden')
            if invalid & INVALID_PATH != 0:
                self.query_one('#file_exists').remove_class('hidden')
            else:
                self.query_one('#file_exists').add_class('hidden')
        except NoMatches:
            pass

    def compute_invalid(self) -> int:
        invalid = 0
        if not self.output_name.endswith('.zlmfit'):
            invalid |= INVALID_EXTN
        if (Path.cwd() / self.output_name).exists():
            invalid |= INVALID_PATH
        if self.niters <= 0:
            invalid |= INVALID_NITERS
        if self.query_one('#bootstrap', Checkbox).value:
            if self.nboot <= 0:
                invalid |= INVALID_NBOOT
        if self.query_one('#mcmc', Checkbox).value:
            if self.nwalkers <= 0:
                invalid |= INVALID_NWALKERS
            if self.sigma <= 0.0:
                invalid |= INVALID_SIGMA
            if self.ntau <= 0:
                invalid |= INVALID_NTAU
            if self.dtau <= 0.0:
                invalid |= INVALID_DTAU
        return invalid

    @on(Checkbox.Changed, '#bootstrap')
    def change_bootstrap(self, event: Checkbox.Changed):
        self.query_one('#bootstrap_info').set_class(event.value, 'active')
        self.query_one('#bootstrap_settings').set_class(not event.value, 'hidden')
        self.invalid

    @on(Checkbox.Changed, '#mcmc')
    def change_mcmc(self, event: Checkbox.Changed):
        self.query_one('#mcmc_info').set_class(event.value, 'active')
        self.query_one('#mcmc_settings').set_class(not event.value, 'hidden')
        self.invalid

    @on(Input.Changed, '#niters')
    def change_niters(self, event: Input.Changed):
        self.niters = int(event.value) if event.value != '' else 0

    @on(Input.Changed, '#nboot')
    def change_nboot(self, event: Input.Changed):
        self.nboot = int(event.value) if event.value != '' else 0

    @on(Input.Changed, '#nwalkers')
    def change_nwalkers(self, event: Input.Changed):
        self.nwalkers = int(event.value) if event.value != '' else 0

    @on(Input.Changed, '#sigma')
    def change_sigma(self, event: Input.Changed):
        self.sigma = float(event.value) if event.value != '' else 0.0

    @on(Input.Changed, '#ntau')
    def change_ntau(self, event: Input.Changed):
        self.ntau = int(event.value) if event.value != '' else 0

    @on(Input.Changed, '#dtau')
    def change_dtau(self, event: Input.Changed):
        self.dtau = float(event.value) if event.value != '' else 0.0

    @on(Input.Changed, '#fit_path')
    def change_fit_path(self, event: Input.Changed):
        self.output_name = event.value

    @on(Button.Pressed, '#back')
    def back_pressed(self):
        self.app.pop_screen()
        self.app.uninstall_screen(self)

    @on(Button.Pressed, '#fit')
    def fit(self):
        output_file_name = self.query_one('#fit_path', Input).value
        self.fit_data.output_path = Path.cwd() / output_file_name
        self.fit_data.niters = self.niters
        if self.query_one('#bootstrap', Checkbox).value:
            self.fit_data.bootstrap = True
            self.fit_data.nboot = self.nboot
        if self.query_one('#mcmc', Checkbox).value:
            self.fit_data.mcmc = True
            self.fit_data.nwalkers = self.nwalkers
            self.fit_data.sigma = self.sigma
            self.fit_data.ntau = self.ntau
            self.fit_data.dtau = self.dtau
        self.app.push_screen(FittingScreen(self.fit_data))
