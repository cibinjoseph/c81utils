import os
import shutil
from pathlib import Path

import numpy as np
import pytest

import c81utils as c81

TESTS = Path(__file__).resolve().parent
DATA = TESTS / 'data'

# C81 files store 3 decimals for coefficients/Mach and 2 for angles
C81_ATOL = 5e-3 + 1e-9


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / 'Airfoil.csv'
    shutil.copy(DATA / 'csv_c81_sample1.csv', p)
    return p


def same_data(a, b, atol):
    for label in ('CL', 'CD', 'CM'):
        ta, tb = getattr(a, label), getattr(b, label)
        np.testing.assert_allclose(ta.alpha, tb.alpha, atol=atol)
        np.testing.assert_allclose(ta.mach, tb.mach, atol=atol)
        np.testing.assert_allclose(ta.val, tb.val, atol=atol)


def test_csv_to_c81_default_output(sample_csv):
    out = c81.csv_to_c81(sample_csv)
    assert isinstance(out, Path)
    assert out == sample_csv.with_suffix('.c81')
    with open(out) as f:
        af = c81.load(f)
    assert af.airfoilname.strip() == 'Airfoil'
    # reference output from the csv-c81 README: same numbers, 3 decimals
    ref = c81.load_csv(sample_csv)
    same_data(af, ref, C81_ATOL)


def test_csv_to_c81_str_input_and_explicit_output(sample_csv, tmp_path):
    out = c81.csv_to_c81(str(sample_csv), str(tmp_path / 'sub_result.C81'))
    assert out == tmp_path / 'sub_result.C81' and out.exists()
    assert not sample_csv.with_suffix('.c81').exists()


def test_csv_to_c81_name_override(sample_csv):
    out = c81.csv_to_c81(sample_csv, name='MYFOIL')
    assert out.read_text().startswith('MYFOIL')


def test_csv_to_c81_matches_csv_c81_reference_output(tmp_path):
    shutil.copy(DATA / 'csv_c81_sample1.csv', tmp_path / 'check.csv')
    out = c81.csv_to_c81(tmp_path / 'check.csv')
    # csv-c81 wrote negative zeros ("-0.000") for the zero-filled tables
    # (0 * negative value); here they are plain zeros. Otherwise identical.
    reference = (DATA / 'csv_c81_sample2.c81').read_text().replace('-0.000', ' 0.000')
    assert out.read_text() == reference


@pytest.mark.parametrize('ext', ['.CSV', '.Csv', '.cSV'])
def test_mixed_case_csv_extension(tmp_path, ext):
    p = tmp_path / ('foil' + ext)
    shutil.copy(DATA / 'csv_c81_sample1.csv', p)
    out = c81.csv_to_c81(p)
    assert out == tmp_path / 'foil.c81'


@pytest.mark.parametrize('ext', ['.C81', '.c81', '.C81'.swapcase(), '.c81'.title()])
def test_mixed_case_c81_extension(tmp_path, ext):
    p = tmp_path / ('foil' + ext)
    shutil.copy(DATA / 'csv_c81_sample2.c81', p)
    out = c81.c81_to_csv(p)
    assert out == tmp_path / 'foil.csv'
    assert out.exists()


def test_c81_to_csv_default_and_explicit(tmp_path):
    src = tmp_path / 'sample1.C81'
    shutil.copy(TESTS / 'sample1.C81', src)
    out = c81.c81_to_csv(src)
    assert out == tmp_path / 'sample1.csv'
    explicit = c81.c81_to_csv(src, tmp_path / 'edited.txt')
    assert explicit.read_text() == out.read_text()
    with open(src) as f:
        original = c81.load(f)
    same_data(original, c81.load_csv(out), 0.0)


def test_c81_csv_c81_roundtrip(tmp_path):
    src = tmp_path / 'sample1.C81'
    shutil.copy(TESTS / 'sample1.C81', src)
    csv_path = c81.c81_to_csv(src)
    back = c81.csv_to_c81(csv_path, tmp_path / 'back.c81', name='sample1')
    with open(src) as f:
        a = c81.load(f)
    with open(back) as f:
        b = c81.load(f)
    same_data(a, b, C81_ATOL)
    # the C81 writer is idempotent once values are 3-decimal rounded
    csv2 = c81.c81_to_csv(back, tmp_path / 'again.csv')
    back2 = c81.csv_to_c81(csv2, tmp_path / 'back2.c81', name='sample1')
    assert back2.read_text() == back.read_text()


def test_csv_to_c81_to_csv_roundtrip_values(tmp_path):
    p = tmp_path / 'f.csv'
    p.write_text('0,0.0,0.5\n-5,0.125,0.25\n5,0.5,0.75\n\n0,0,0.5\n-5,0.01,0.02\n5,0.03,0.04\n')
    c = c81.csv_to_c81(p)
    out = c81.c81_to_csv(c, tmp_path / 'g.csv')
    same_data(c81.load_csv(p), c81.load_csv(out), C81_ATOL)


def test_refuses_to_overwrite_input(sample_csv, tmp_path):
    before = sample_csv.read_text()
    with pytest.raises(ValueError, match='same file'):
        c81.csv_to_c81(sample_csv, sample_csv)
    link = tmp_path / 'link.csv'
    os.symlink(sample_csv, link)
    with pytest.raises(ValueError, match='same file'):
        c81.csv_to_c81(sample_csv, link)
    with pytest.raises(ValueError, match='same file'):
        c81.csv_to_c81(sample_csv, tmp_path / '.' / 'Airfoil.csv')
    assert sample_csv.read_text() == before

    c = tmp_path / 'z.c81'
    shutil.copy(DATA / 'csv_c81_sample2.c81', c)
    with pytest.raises(ValueError, match='same file'):
        c81.c81_to_csv(c, c)


def test_wrong_extension(tmp_path):
    p = tmp_path / 'a.txt'
    p.write_text('x')
    with pytest.raises(ValueError, match=r'expected a \.csv'):
        c81.csv_to_c81(p)
    with pytest.raises(ValueError, match=r'expected a \.c81'):
        c81.c81_to_csv(p)
    with pytest.raises(ValueError):
        c81.csv_to_c81(tmp_path / 'noext')


def test_missing_input(tmp_path):
    with pytest.raises(FileNotFoundError):
        c81.csv_to_c81(tmp_path / 'nope.csv')
    with pytest.raises(FileNotFoundError):
        c81.c81_to_csv(tmp_path / 'nope.c81')


def test_invalid_content_leaves_no_output(tmp_path):
    bad = tmp_path / 'bad.csv'
    bad.write_text('0,0,1\n1,2,x\n2,3,4\n')
    with pytest.raises(ValueError):
        c81.csv_to_c81(bad)
    assert not (tmp_path / 'bad.c81').exists()

    junk = tmp_path / 'junk.c81'
    junk.write_text('not a c81 file\n')
    with pytest.raises(ValueError, match='not a valid C81 file'):
        c81.c81_to_csv(junk)
    assert not (tmp_path / 'junk.csv').exists()


def test_existing_output_is_replaced(sample_csv):
    out = sample_csv.with_suffix('.c81')
    out.write_text('old')
    c81.csv_to_c81(sample_csv)
    assert out.read_text() != 'old'
