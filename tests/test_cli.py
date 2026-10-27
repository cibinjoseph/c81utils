import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import c81utils as c81
from c81utils.cli import main

TESTS = Path(__file__).resolve().parent
DATA = TESTS / 'data'


@pytest.fixture
def csv_file(tmp_path):
    p = tmp_path / 'airfoil.csv'
    shutil.copy(DATA / 'csv_c81_sample1.csv', p)
    return p


def test_help(capsys):
    with pytest.raises(SystemExit) as exc:
        main(['--help'])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert 'c81-convert' in out and '--plot' in out and '-o' in out


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(['--version'])
    assert exc.value.code == 0
    assert c81.__version__ in capsys.readouterr().out


def test_no_arguments_is_usage_error(capsys):
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_csv_to_c81(csv_file, capsys):
    assert main([str(csv_file)]) == 0
    out = csv_file.with_suffix('.c81')
    assert out.exists()
    assert capsys.readouterr().out.strip() == str(out)


def test_c81_to_csv(tmp_path, capsys):
    src = tmp_path / 'x.C81'
    shutil.copy(DATA / 'csv_c81_sample2.c81', src)
    assert main([str(src)]) == 0
    assert (tmp_path / 'x.csv').exists()
    assert str(tmp_path / 'x.csv') in capsys.readouterr().out


def test_explicit_output(csv_file, tmp_path, capsys):
    target = tmp_path / 'result.c81'
    assert main([str(csv_file), '-o', str(target)]) == 0
    assert target.exists() and not csv_file.with_suffix('.c81').exists()
    assert capsys.readouterr().out.strip() == str(target)


def test_multiple_files(csv_file, tmp_path, capsys):
    second = tmp_path / 'second.CSV'
    shutil.copy(csv_file, second)
    third = tmp_path / 'third.c81'
    shutil.copy(DATA / 'csv_c81_sample2.c81', third)
    assert main([str(csv_file), str(second), str(third)]) == 0
    lines = capsys.readouterr().out.split()
    assert lines == [str(csv_file.with_suffix('.c81')), str(tmp_path / 'second.c81'),
                     str(tmp_path / 'third.csv')]


def test_output_with_multiple_inputs_rejected(csv_file, tmp_path, capsys):
    second = tmp_path / 'second.csv'
    shutil.copy(csv_file, second)
    with pytest.raises(SystemExit) as exc:
        main([str(csv_file), str(second), '-o', str(tmp_path / 'out.c81')])
    assert exc.value.code == 2
    assert 'single input' in capsys.readouterr().err
    assert not (tmp_path / 'out.c81').exists()


def test_unsupported_extension(tmp_path, csv_file, capsys):
    bad = tmp_path / 'data.txt'
    bad.write_text('x')
    assert main([str(csv_file), str(bad)]) == 2
    err = capsys.readouterr().err
    assert 'unsupported file extension' in err and 'data.txt' in err
    # nothing converted when usage is invalid
    assert not csv_file.with_suffix('.c81').exists()


def test_missing_file(tmp_path, capsys):
    assert main([str(tmp_path / 'ghost.csv')]) == 1
    cap = capsys.readouterr()
    assert 'ghost.csv' in cap.err and 'Traceback' not in cap.err


def test_bad_content_reports_and_continues(tmp_path, csv_file, capsys):
    bad = tmp_path / 'bad.csv'
    bad.write_text('0,0,1\n1,2,x\n2,3,4\n')
    assert main([str(bad), str(csv_file)]) == 1
    cap = capsys.readouterr()
    assert 'cannot convert' in cap.err and 'Traceback' not in cap.err
    assert str(csv_file.with_suffix('.c81')) in cap.out


def test_input_never_overwritten(csv_file, capsys):
    before = csv_file.read_text()
    assert main([str(csv_file), '-o', str(csv_file)]) == 1
    assert csv_file.read_text() == before
    assert 'same file' in capsys.readouterr().err


def test_plot_output_conflicts(csv_file, capsys):
    with pytest.raises(SystemExit) as exc:
        main(['--plot', str(csv_file), '-o', 'x.png'])
    assert exc.value.code == 2


def test_plot_without_matplotlib(monkeypatch, tmp_path, capsys):
    src = tmp_path / 'x.c81'
    shutil.copy(DATA / 'csv_c81_sample2.c81', src)
    monkeypatch.setitem(sys.modules, 'matplotlib', None)
    monkeypatch.setitem(sys.modules, 'matplotlib.pyplot', None)
    assert main(['--plot', str(src)]) == 1
    err = capsys.readouterr().err
    assert 'pip install "c81utils[plot]"' in err and 'Traceback' not in err


def test_plot_cli(monkeypatch, tmp_path):
    plt = pytest.importorskip('matplotlib.pyplot')
    import matplotlib
    matplotlib.use('Agg')
    shown = []
    monkeypatch.setattr(plt, 'show', lambda *a, **k: shown.append(True))
    src = tmp_path / 'x.c81'
    shutil.copy(DATA / 'csv_c81_sample2.c81', src)
    assert main(['--plot', str(src)]) == 0
    assert shown == [True]
    plt.close('all')


def test_python_dash_m_help():
    res = subprocess.run([sys.executable, '-m', 'c81utils', '--help'],
                         capture_output=True, text=True)
    assert res.returncode == 0 and 'c81-convert' in res.stdout
