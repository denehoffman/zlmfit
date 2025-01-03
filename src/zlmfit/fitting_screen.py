import pickle
from typing import Any
from textual import on
from textual.events import Print
from textual.screen import Screen
from textual.widgets import Footer, Header, ProgressBar, RichLog
import numpy as np
import asyncio

from textual.worker import Worker, WorkerState

from zlmfit.fit_data import FitData, FitResult, BootstrapResult, MCMCResult


class FittingScreen(Screen):
    CSS_PATH = 'fitting_screen.tcss'

    def __init__(self, fit_data: FitData):
        super().__init__()
        self.fit_data = fit_data
        self.fit_result: FitResult = {}
        self.bootstrap_result: BootstrapResult = {}
        self.mcmc_result: MCMCResult = {}

    def compose(self):
        yield Header()
        yield ProgressBar(self.fit_data.bins, id='fit')
        yield ProgressBar(self.fit_data.niters, id='iters')
        if self.fit_data.bootstrap:
            yield ProgressBar(self.fit_data.nboot * self.fit_data.bins, id='bootstrap')
        if self.fit_data.mcmc:
            yield ProgressBar(self.fit_data.bins, id='mcmc')
        yield RichLog(markup=True)
        yield Footer()

    def on_mount(self):
        self.begin_capture_print()
        self.fit_data.bin_datasets()
        self.run_worker(self.run_fit, name='run_fit', thread=True)

    @on(Print)
    def log_printed(self, event: Print):
        if not event.text:
            return
        self.query_one(RichLog).write(event.text)

    def on_worker_state_changed(self, event: Worker.StateChanged):
        if event.worker.name == 'run_fit' and event.state == WorkerState.SUCCESS:
            if self.fit_data.bootstrap:
                self.run_worker(self.run_bootstrap, name='run_bootstrap', thread=True)
            elif self.fit_data.mcmc:
                self.run_worker(self.run_mcmc, name='run_mcmc', thread=True)
        elif event.worker.name == 'run_bootstrap' and event.state == WorkerState.SUCCESS:
            if self.fit_data.mcmc:
                self.run_worker(self.run_mcmc, name='run_mcmc', thread=True)

    def update_output(self, key: str, data: Any):
        out_dict = {}
        if self.fit_data.output_path.exists():
            with self.fit_data.output_path.open('rb') as f:
                out_dict = pickle.load(f)
        out_dict[key] = data
        with self.fit_data.output_path.open('wb') as f:
            pickle.dump(out_dict, f)

    async def run_fit(self):
        rng = np.random.default_rng(0)

        for ibin in range(self.fit_data.bins):
            print(f'[red]Fitting bin {ibin}[/]')
            nll = self.fit_data.get_nll(ibin)
            best_fit = None
            best_nll = float('inf')
            self.query_one('#iters', ProgressBar).update(progress=0)
            await asyncio.sleep(0)

            for iiter in range(self.fit_data.niters):
                print(f'[blue]    Fitting iteration {iiter}[/]')

                p0 = rng.uniform(-100.0, 100.0, size=len(nll.parameters))
                fit_result = nll.minimize(p0)
                if fit_result.fx < best_nll:
                    best_fit = fit_result
                    best_nll = fit_result.fx
                self.query_one('#iters', ProgressBar).advance(1)
                await asyncio.sleep(0)

            assert best_fit is not None
            self.fit_result[ibin] = best_fit
            self.query_one('#fit', ProgressBar).advance(1)
            await asyncio.sleep(0)

        print('[green]Fitting complete![/]')
        self.update_output('fit_result', self.fit_result)

    async def run_bootstrap(self):
        out = {ibin: [] for ibin in self.fit_result.keys()}
        for ibin, fit_result in self.fit_result.items():
            print(f'[red]Fitting bin {ibin}[/]')
            for iboot in range(self.fit_data.nboot):
                print(f'[blue]    Fitting bootstrap {iboot}[/]')
                nll = self.fit_data.get_nll(ibin, bootstrap=iboot)
                bootstrap_result = nll.minimize(fit_result.x)
                out[ibin].append(bootstrap_result)
                self.query_one('#bootstrap', ProgressBar).advance(1)
                await asyncio.sleep(0)
        self.bootstrap_result = out
        self.update_output('bootstrap_result', self.bootstrap_result)

    async def run_mcmc(self):
        out = {}
        rng = np.random.default_rng(0)
        for ibin, fit_result in self.fit_result.items():
            print(f'[yellow]Running MCMC on bin {ibin}[/]')
            nll = self.fit_data.get_nll(ibin)
            p0 = rng.normal(
                fit_result.x,
                scale=self.fit_data.sigma,
                size=(self.fit_data.nwalkers, len(fit_result.x)),
            )
            obs = self.fit_data.get_mcmc_observer(ibin)
            ensemble = nll.mcmc(p0, 3000, observers=[obs])
            out[ibin] = (ensemble, obs.latest_tau)
            print(
                f'[yellow]Converged after {ensemble.dimension[1]} steps with tau = {obs.latest_tau}[/]'
            )
            self.query_one('#mcmc', ProgressBar).advance(1)
            await asyncio.sleep(0)
        self.mcmc_result = out
        self.update_output('mcmc_result', self.mcmc_result)
