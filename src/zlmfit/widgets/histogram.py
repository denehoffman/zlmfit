from rich.console import RenderableType
from textual.geometry import Size
from textual.reactive import reactive
from textual.widget import Widget

import plotext as plt
import numpy as np
import laddu as ld
from rich.text import Text


class Histogram(Widget):
    bins: reactive[int] = reactive(20)
    lower: reactive[float] = reactive(1.0)
    upper: reactive[float] = reactive(2.0)
    data: reactive[ld.Dataset | None] = reactive(None)

    def __init__(
        self,
        data: ld.Dataset,
        bins: int = 40,
        lower: float = 1.0,
        upper: float = 2.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.data = data
        mass = ld.Mass([2, 3])
        self.mass = mass.value_on(self.data)
        self.weights = self.data.weights
        self.bins = bins
        self.lower = lower
        self.upper = upper
        self.text_width = 100
        self.plot = self.get_plot()

    def watch_data(self, new_data: ld.Dataset | None):
        if new_data:
            mass = ld.Mass([2, 3])
            self.mass = mass.value_on(new_data)
            self.weights = new_data.weights
            self.plot = self.get_plot()

    def get_plot(self) -> RenderableType:
        plt.clf()
        hist, bins = np.histogram(
            self.mass, self.bins, range=(self.lower, self.upper), weights=self.weights
        )
        centers = (bins[1:] + bins[:-1]) / 2
        plt.bar(centers, hist)
        term_width, term_height = plt.tw(), plt.th()
        if term_width and term_height:
            plt.plot_size(term_width - 3, int(term_height * 0.8) - 6)
        text = Text.from_ansi(plt.build())
        self.text_width = len(text.split()[0])
        return text

    def watch_lower(self, lower: float):
        self.plot = self.get_plot()

    def watch_upper(self, upper: float):
        self.plot = self.get_plot()

    def watch_bins(self, bins: int):
        self.plot = self.get_plot()

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return self.text_width

    def render(self) -> RenderableType:
        return self.plot
