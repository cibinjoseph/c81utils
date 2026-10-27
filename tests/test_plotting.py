import sys
from pathlib import Path

import pytest

import c81utils as c81

DATA = Path(__file__).resolve().parent / 'data'


@pytest.fixture
def airfoil():
    return c81.load_csv(DATA / 'csv_c81_sample1.csv')


def test_plot_returns_figure_and_axes_without_showing(airfoil, monkeypatch):
    plt = pytest.importorskip('matplotlib.pyplot')
    import matplotlib
    matplotlib.use('Agg')
    monkeypatch.setattr(plt, 'show', lambda *a, **k: pytest.fail('show() called'))
    fig, axes = c81.plot(airfoil)
    assert len(axes) == 3
    assert [ax.get_title() for ax in axes] == ['CL', 'CD', 'CM']
    assert all(len(ax.lines) == 3 for ax in axes)   # one curve per Mach number
    assert axes[0].lines[0].get_xdata().tolist() == airfoil.CL.alpha.tolist()
    plt.close(fig)


def test_plot_different_grids(monkeypatch):
    plt = pytest.importorskip('matplotlib.pyplot')
    import matplotlib
    matplotlib.use('Agg')
    af = c81.load_csv(DATA / 'csv_c81_sample1.csv')
    af = c81.C81('x', af.CL.alpha, af.CL.mach, af.CL.val,
                 af.CL.alpha[:3], af.CL.mach[:2], af.CL.val[:3, :2],
                 af.CL.alpha, af.CL.mach, af.CL.val)
    fig, axes = c81.plot(af)
    assert [len(ax.lines) for ax in axes] == [3, 2, 3]
    plt.close(fig)


def test_plot_without_matplotlib_message(airfoil, monkeypatch):
    monkeypatch.setitem(sys.modules, 'matplotlib', None)
    monkeypatch.setitem(sys.modules, 'matplotlib.pyplot', None)
    with pytest.raises(ImportError, match=r'c81utils\[plot\]'):
        c81.plot(airfoil)


def test_importing_package_does_not_import_matplotlib():
    import subprocess
    code = 'import sys, c81utils; sys.exit("matplotlib" in sys.modules)'
    assert subprocess.run([sys.executable, '-c', code]).returncode == 0
