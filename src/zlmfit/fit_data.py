from dataclasses import dataclass
from pathlib import Path
import laddu as ld
import re
import numpy as np
from rich.rule import Rule


@dataclass(eq=True, frozen=True)
class Wave:
    l: int  # noqa: E741
    m: int
    r: int

    def __str__(self) -> str:
        return f'{self.l}{self.m:+}{self.r:+}'

    @staticmethod
    def from_id(id: str) -> 'Wave':
        m = re.match(r'(wave_|anchor_)(\d+)([pn]\d?|0)([pn])', id)
        assert m is not None
        _, g_l, g_m, g_r = m.groups()

        def convert(value: str) -> int:
            if value == '0':
                return 0
            sign = 1 if value.startswith('p') else -1
            if len(value) > 1:
                return sign * int(value[1:])
            return sign

        return Wave(int(g_l), convert(g_m), convert(g_r))

    @staticmethod
    def get_model(
        pos_waves: list['Wave'] | None,
        pos_anchor: int | None,
        neg_waves: list['Wave'] | None,
        neg_anchor: int | None,
    ) -> ld.Model:
        angles = ld.Angles(0, [1], [2], [2, 3])
        polarization = ld.Polarization(0, [1])
        manager = ld.Manager()
        if pos_waves is not None and pos_anchor is not None:
            pos_out = 0
            for i, wave in enumerate(pos_waves):
                amp = manager.register(
                    ld.Scalar(str(wave), ld.parameter(f'{wave} real'))
                    if i == pos_anchor
                    else ld.ComplexScalar(
                        str(wave),
                        ld.parameter(f'{wave} real'),
                        ld.parameter(f'{wave} imag'),
                    )
                )
                zlm = manager.register(
                    ld.Zlm(
                        f'Z{wave}',
                        l=wave.l,  # type: ignore
                        m=wave.m,  # type: ignore
                        r='+' if wave.r > 0 else '-',
                        angles=angles,
                        polarization=polarization,
                    )
                )
                pos_out += amp * zlm
            if neg_waves is None:
                return manager.model(pos_out.norm_sqr())  # type: ignore

        if neg_waves is not None and neg_anchor is not None:
            neg_out = 0
            for i, wave in enumerate(neg_waves):
                amp = manager.register(
                    ld.Scalar(str(wave), ld.parameter(f'{wave} real'))
                    if i == neg_anchor
                    else ld.ComplexScalar(
                        str(wave),
                        ld.parameter(f'{wave} real'),
                        ld.parameter(f'{wave} imag'),
                    )
                )
                zlm = manager.register(
                    ld.Zlm(
                        f'Z{wave}',
                        l=wave.l,  # type: ignore
                        m=wave.m,  # type: ignore
                        r='+' if wave.r > 0 else '-',
                        angles=angles,
                        polarization=polarization,
                    )
                )
                neg_out += amp * zlm
            if pos_waves is None:
                return manager.model(pos_out.norm_sqr())  # type: ignore

        return manager.model(pos_out.norm_sqr() + neg_out.norm_sqr())  # type: ignore


class CustomMCMCObserver(ld.MCMCObserver):
    def __init__(
        self, nll: ld.NLL, waves: list[Wave], ntau: int, dtau: float, discard: float = 0.5
    ):
        self.nll = nll
        self.waves = waves
        self.ntau = ntau
        self.dtau = dtau
        self.discard = discard
        self.latest_tau = np.inf
        self.tot = []
        self.projections = {wave: [] for wave in waves}

    def callback(self, step: int, ensemble: ld.Ensemble) -> tuple[ld.Ensemble, bool]:
        print(f'MCMC step [red]{step}[/]')
        latest_step = ensemble.get_chain()[:, -1, :]
        tot = []
        projections = {wave: [] for wave in self.waves}
        for i_walker in range(ensemble.dimension[0]):
            tot.append(np.sum(self.nll.project(latest_step[i_walker])))
            for wave in self.waves:
                projections[wave].append(
                    np.sum(
                        self.nll.project_with(
                            latest_step[i_walker], [f'Z{wave}', f'{wave}']
                        )
                    )
                )
        self.tot.append(tot)
        for wave in self.waves:
            self.projections[wave].append(projections[wave])
        if step % self.ntau == 0:
            chain = np.array([self.projections[wave] for wave in self.waves]).transpose(
                2, 1, 0
            )  # (walkers, steps, parameters)
            chain = chain[
                :,
                min(
                    int(step * self.discard),
                    int(self.latest_tau * self.ntau)
                    if np.isfinite(self.latest_tau)
                    else int(step * self.discard),
                ) :,
            ]
            taus = ld.integrated_autocorrelation_times(chain)
            tau = np.mean(taus)
            dtau = abs(self.latest_tau - tau) / tau
            print(Rule('[blue]Checking Convergence[/]'))
            print(f"τ = [{', '.join([str(t) for t in taus])}]")
            print(f'τ̅ = {tau} (converges with τ̅ > {tau * self.ntau})')
            print(f'Δτ/τ = {dtau} (converges with Δτ/τ < {self.dtau})')
            converged = bool((tau * self.ntau < step) and (dtau < self.dtau))
            self.latest_tau = tau
            return (ensemble, converged)

        return (ensemble, False)


type FitResult = dict[int, ld.Status]
type BootstrapResult = dict[int, list[ld.Status]]
type MCMCResult = dict[int, tuple[ld.Ensemble, float]]


class FitData:
    def __init__(
        self,
        data: ld.Dataset,
        accmc: ld.Dataset,
        genmc: ld.Dataset,
    ):
        self.data: ld.Dataset = data
        self.accmc: ld.Dataset = accmc
        self.genmc: ld.Dataset = genmc
        self._binned_data: ld.BinnedDataset | None = None
        self._binned_accmc: ld.BinnedDataset | None = None
        self._binned_genmc: ld.BinnedDataset | None = None
        self._output_path: Path | None = None
        self._bins: int | None = None
        self._lower: float | None = None
        self._upper: float | None = None
        self.pos_waves: list[Wave] | None = None
        self.pos_anchor: int | None = None
        self.neg_waves: list[Wave] | None = None
        self.neg_anchor: int | None = None
        self._niters: int | None = None
        self.bootstrap: bool = False
        self._nboot: int | None = None
        self.mcmc: bool = False
        self._nwalkers: int | None = None
        self._sigma: float | None = None
        self._ntau: int | None = None
        self._dtau: float | None = None

    @property
    def binned_data(self) -> ld.BinnedDataset:
        if self._binned_data is not None:
            return self._binned_data
        raise AttributeError('Data has not been binned yet!')

    @property
    def binned_accmc(self) -> ld.BinnedDataset:
        if self._binned_accmc is not None:
            return self._binned_accmc
        raise AttributeError('Accepted MC has not been binned yet!')

    @property
    def binned_genmc(self) -> ld.BinnedDataset:
        if self._binned_genmc is not None:
            return self._binned_genmc
        raise AttributeError('Generated MC has not been binned yet!')

    @property
    def output_path(self) -> Path:
        if self._output_path is not None:
            return self._output_path
        raise AttributeError('Output path is not set!')

    @output_path.setter
    def output_path(self, new_output_path: Path):
        self._output_path = new_output_path

    @property
    def bins(self) -> int:
        if self._bins is not None:
            return self._bins
        raise AttributeError('Number of bins has not been set!')

    @bins.setter
    def bins(self, new_bins: int):
        self._bins = new_bins

    @property
    def lower(self) -> float:
        if self._lower is not None:
            return self._lower
        raise AttributeError('Lower bin edge has not been set!')

    @lower.setter
    def lower(self, new_lower: float):
        self._lower = new_lower

    @property
    def upper(self) -> float:
        if self._upper is not None:
            return self._upper
        raise AttributeError('Upper bin edge has not been set!')

    @upper.setter
    def upper(self, new_upper: float):
        self._upper = new_upper

    @property
    def niters(self) -> int:
        if self._niters is not None:
            return self._niters
        raise AttributeError('Number of iterations has not been set!')

    @niters.setter
    def niters(self, new_niters: int):
        self._niters = new_niters

    @property
    def nboot(self) -> int:
        if self._nboot is not None:
            return self._nboot
        raise AttributeError('Number of bootstraps has not been set!')

    @nboot.setter
    def nboot(self, new_nboot: int):
        self._nboot = new_nboot

    @property
    def nwalkers(self) -> int:
        if self._nwalkers is not None:
            return self._nwalkers
        raise AttributeError('Number of walkers has not been set!')

    @nwalkers.setter
    def nwalkers(self, new_nwalkers: int):
        self._nwalkers = new_nwalkers

    @property
    def sigma(self) -> float:
        if self._sigma is not None:
            return self._sigma
        raise AttributeError('Sigma has not been set!')

    @sigma.setter
    def sigma(self, new_sigma: float):
        self._sigma = new_sigma

    @property
    def ntau(self) -> int:
        if self._ntau is not None:
            return self._ntau
        raise AttributeError('Number of autocorrelation times has not been set!')

    @ntau.setter
    def ntau(self, new_ntau: int):
        self._ntau = new_ntau

    @property
    def dtau(self) -> float:
        if self._dtau is not None:
            return self._dtau
        raise AttributeError('Absolute change in τ has not been set!')

    @dtau.setter
    def dtau(self, new_dtau: float):
        self._dtau = new_dtau

    def get_nll(self, ibin: int, *, bootstrap: int | None = None) -> ld.NLL:
        assert self.binned_data is not None
        assert self.binned_accmc is not None
        model = Wave.get_model(
            self.pos_waves, self.pos_anchor, self.neg_waves, self.neg_anchor
        )
        if bootstrap is not None:
            return ld.NLL(
                model,
                self.binned_data[ibin].bootstrap(bootstrap),
                self.binned_accmc[ibin],
            )
        return ld.NLL(model, self.binned_data[ibin], self.binned_accmc[ibin])

    def get_mcmc_observer(self, ibin: int) -> CustomMCMCObserver:
        waves = (
            self.pos_waves + self.neg_waves
            if self.pos_waves and self.neg_waves
            else self.pos_waves
            if self.pos_waves
            else self.neg_waves
        )
        assert waves is not None
        assert self.ntau is not None
        assert self.dtau is not None
        return CustomMCMCObserver(
            self.get_nll(ibin),
            waves,
            self.ntau,
            self.dtau,
        )

    def bin_datasets(self, *, bin_generated: bool = False):
        assert self.bins is not None
        assert self.lower is not None
        assert self.upper is not None
        mass = ld.Mass([2, 3])
        self._binned_data = self.data.bin_by(mass, self.bins, (self.lower, self.upper))
        self._binned_accmc = self.accmc.bin_by(mass, self.bins, (self.lower, self.upper))
        if bin_generated:
            self._binned_genmc = self.genmc.bin_by(
                mass, self.bins, (self.lower, self.upper)
            )

    def run_fit(self) -> FitResult:
        out = {}
        assert self.bins is not None
        assert self.niters is not None
        rng = np.random.default_rng(0)
        for ibin in range(self.bins):
            nll = self.get_nll(ibin)
            best_fit = None
            best_nll = np.inf
            for _ in range(self.niters):
                p0 = rng.uniform(-100.0, 100.0, size=len(nll.parameters))
                fit_result = nll.minimize(p0)
                if fit_result.fx < best_nll:
                    best_fit = fit_result
                    best_nll = fit_result.fx
            assert best_fit is not None
            out[ibin] = best_fit
        return out

    def run_bootstrap(self, fit_results: FitResult) -> BootstrapResult:
        out = {ibin: [] for ibin in fit_results.keys()}
        assert self.nboot is not None
        for ibin, fit_result in fit_results.items():
            for iboot in range(self.nboot):
                nll = self.get_nll(ibin, bootstrap=iboot)
                bootstrap_result = nll.minimize(fit_result.x)
                out[ibin].append(bootstrap_result)
        return out

    def run_mcmc(self, fit_results: FitResult) -> MCMCResult:
        out = {}
        assert self.sigma is not None
        assert self.nwalkers is not None
        rng = np.random.default_rng(0)
        for ibin, fit_result in fit_results.items():
            nll = self.get_nll(ibin)
            p0 = rng.normal(
                fit_result.x,
                scale=self.sigma,
                size=(self.nwalkers, len(fit_result.x)),
            )
            obs = self.get_mcmc_observer(ibin)
            ensemble = nll.mcmc(p0, 3000, observers=[obs])
            out[ibin] = (ensemble, obs.latest_tau)
        return out
