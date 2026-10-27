"""Plotting of C81 coefficient tables (requires the optional Matplotlib)."""

from typing import Tuple

from .core import C81

MATPLOTLIB_HINT = ('Plotting requires Matplotlib, which is not installed. '
                   'Install it with: pip install "c81utils[plot]"')


def plot(c81Data: C81, show: bool = False) -> Tuple['object', 'object']:
    """Plot CL, CD and CM against angle of attack, one curve per Mach number.

    Parameters
    ----------
    c81Data
        The airfoil data.
    show
        Call ``matplotlib.pyplot.show()`` before returning. Off by default so
        that the figure can be customised or saved first.

    Returns
    -------
    (fig, axes)
        The Matplotlib figure and an array of its three axes (CL, CD, CM).

    Raises
    ------
    ImportError
        If Matplotlib is not installed.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as err:
        raise ImportError(MATPLOTLIB_HINT) from err

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, label in zip(axes, ('CL', 'CD', 'CM')):
        table = getattr(c81Data, label)
        for i, mach in enumerate(table.mach):
            ax.plot(table.alpha, table.val[:, i], label='M {:g}'.format(mach))
        ax.set_xlabel('alpha [deg]')
        ax.set_title(label)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize='small')
    fig.suptitle(c81Data.airfoilname.strip())
    fig.tight_layout()
    if show:
        plt.show()
    return fig, axes
