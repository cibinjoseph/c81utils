import io
import os
import textwrap

import numpy as np
import pytest

import c81utils as c81

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
TESTS = os.path.dirname(os.path.abspath(__file__))

CL_TABLE = """\
0,0.0,0.3,0.6,0.9
-10,-0.8,-0.7,-0.6,-0.5
-5,-0.4,-0.35,-0.3,-0.25
0,0.0,0.0,0.0,0.0
5,0.4,0.35,0.3,0.25
10,0.8,0.7,0.6,0.5
"""
CD_TABLE = """\
0,0.0,0.5
-5,0.02,0.03
0,0.01,0.02
5,0.02,0.03
"""
CM_TABLE = """\
0,0.0,0.2,0.4
-5,-0.1,-0.1,-0.1
5,0.1,0.1,0.1
"""


def parse(text, **kw):
    return c81.load_csv(io.StringIO(textwrap.dedent(text)), **kw)


# ---------------------------------------------------------------- reading --

def test_single_table_is_cl_with_zero_cd_cm():
    af = parse(CL_TABLE)
    np.testing.assert_array_equal(af.CL.mach, [0.0, 0.3, 0.6, 0.9])
    np.testing.assert_array_equal(af.CL.alpha, [-10, -5, 0, 5, 10])
    assert af.CL.val[0, 0] == -0.8
    for t in (af.CD, af.CM):
        np.testing.assert_array_equal(t.mach, af.CL.mach)
        np.testing.assert_array_equal(t.alpha, af.CL.alpha)
        assert t.val.shape == af.CL.val.shape
        assert not t.val.any()
    # zero tables are independent copies, not views of CL
    af.CD.val[0, 0] = 1.0
    assert af.CL.val[0, 0] == -0.8 and af.CM.val[0, 0] == 0.0


def test_two_tables_cm_zero():
    af = parse(CL_TABLE + '\n' + CD_TABLE)
    np.testing.assert_array_equal(af.CD.mach, [0.0, 0.5])
    assert af.CD.val.shape == (3, 2)
    assert af.CM.val.shape == af.CL.val.shape and not af.CM.val.any()


def test_three_tables_with_different_grids():
    af = parse(CL_TABLE + '\n' + CD_TABLE + '\n' + CM_TABLE)
    assert af.CL.val.shape == (5, 4)
    assert af.CD.val.shape == (3, 2)
    assert af.CM.val.shape == (2, 3)
    np.testing.assert_array_equal(af.CM.alpha, [-5, 5])
    assert af.getCM(0.0, 0.2) == pytest.approx(0.0)
    assert af.getCL(5.0, 0.3) == pytest.approx(0.35)


def test_comments_and_extra_blank_lines():
    text = ('# header comment\n\n\n' + CL_TABLE.replace('\n-5,', '\n# note\n-5,', 1)
            + '   \n\n\n# between tables\n\n' + CD_TABLE.replace('0.02,0.03\n0,', '0.02,0.03 # tail\n0,', 1)
            + '\n\n')
    af = parse(text)
    assert af.CL.val.shape == (5, 4)
    assert af.CD.val.shape == (3, 2)
    assert af.CD.val[0, 1] == 0.03


def test_whitespace_delimited():
    af = parse(CL_TABLE.replace(',', '  '))
    assert af.CL.val.shape == (5, 4)
    assert af.CL.val[1, 1] == -0.35


def test_delimiter_is_per_table():
    af = parse(CL_TABLE + '\n' + CD_TABLE.replace(',', ' ') + '\n' + CM_TABLE)
    assert af.CL.val.shape == (5, 4)
    assert af.CD.val.shape == (3, 2)
    assert af.CM.val.shape == (2, 3)


def test_comma_with_spaces_and_crlf():
    af = parse((CL_TABLE.replace(',', ' , ')).replace('\n', '\r\n'))
    assert af.CL.val.shape == (5, 4)


def test_order_is_preserved_not_sorted():
    # decreasing grid must be rejected, never silently sorted
    with pytest.raises(ValueError, match='strictly increasing'):
        parse('0,0,1\n5,1,1\n0,2,2\n')  # alpha 5 then 0
    with pytest.raises(ValueError, match='Mach numbers must be strictly increasing'):
        parse('0,1,0\n0,1,1\n5,2,2\n')


def test_name_defaults(tmp_path):
    p = tmp_path / 'NACA0012.csv'
    p.write_text(CL_TABLE)
    assert c81.load_csv(p).airfoilname == 'NACA0012'
    assert c81.load_csv(str(p)).airfoilname == 'NACA0012'
    assert c81.load_csv(p, name='mine').airfoilname == 'mine'
    with open(p) as f:
        assert c81.load_csv(f).airfoilname == 'NACA0012'
    assert parse(CL_TABLE).airfoilname == 'unnamed'


def test_file_like_and_bom(tmp_path):
    p = tmp_path / 'a.csv'
    p.write_bytes(b'\xef\xbb\xbf' + CL_TABLE.encode())
    assert c81.load_csv(p).CL.val.shape == (5, 4)
    assert c81.load_csv(io.BytesIO(b'\xef\xbb\xbf' + CL_TABLE.encode())).CL.val.shape == (5, 4)


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        c81.load_csv('/nonexistent/dir/file.csv')


@pytest.mark.parametrize('text, message', [
    ('', 'empty'),
    ('\n\n  \n', 'empty'),
    ('# only a comment\n', 'empty'),
    ('0,0,1\n1,2,3\n', 'at least two angle rows'),          # too few rows
    ('0,0\n1,2\n2,3\n3,4\n', 'at least two angle rows'),    # one Mach column
    ('0,0,1\n1,2,3\n2,3\n', 'line 3: expected 3 values'),   # ragged
    ('0,0,1\n1,2,abc\n2,3,4\n', "cannot convert 'abc'"),
    ('0,0,1\n1,2,\n2,3,4\n', 'empty cell'),
    ('0,0,1\n1,2,3\n2 3 4\n', 'mixed delimiters'),
    ('0,0,1\n1,2,nan\n2,3,4\n', 'non-finite'),
    ('0,0,1\n1,2,inf\n2,3,4\n', 'non-finite'),
    ('0,0,1\n1,2,-Infinity\n2,3,4\n', 'non-finite'),
    ('0,0,1\n1,1_0,3\n2,3,4\n', 'invalid value'),
    ('0,0,1\n1,2,3\n1,3,4\n', 'angles of attack must be strictly increasing'),
    ('0,0,0\n1,2,3\n2,3,4\n', 'Mach numbers must be strictly increasing'),
])
def test_invalid_input(text, message):
    with pytest.raises(ValueError, match=message):
        parse(text)


def test_error_names_the_table():
    with pytest.raises(ValueError, match='CD table'):
        parse(CL_TABLE + '\n0,0,1\n1,x,3\n2,3,4\n')


def test_too_many_tables():
    with pytest.raises(ValueError, match='found 4 tables'):
        parse('\n'.join([CL_TABLE] * 4))


def test_bad_name_type():
    with pytest.raises(TypeError):
        parse(CL_TABLE, name=3)


def test_csv_c81_sample_fixture():
    af = c81.load_csv(os.path.join(DATA, 'csv_c81_sample1.csv'))
    assert af.airfoilname == 'csv_c81_sample1'
    np.testing.assert_array_equal(af.CL.alpha, [-180, -45, -5, 0, 5, 45, 180])
    np.testing.assert_array_equal(af.CL.mach, [0, 0.5, 1])
    assert af.CL.val[1].tolist() == [1, 1.1, 1.2]
    assert not af.CD.val.any() and not af.CM.val.any()


# ---------------------------------------------------------------- writing --

def assert_same_data(a, b, rtol=0.0, atol=0.0):
    for label in ('CL', 'CD', 'CM'):
        ta, tb = getattr(a, label), getattr(b, label)
        np.testing.assert_allclose(ta.alpha, tb.alpha, rtol=rtol, atol=atol)
        np.testing.assert_allclose(ta.mach, tb.mach, rtol=rtol, atol=atol)
        np.testing.assert_allclose(ta.val, tb.val, rtol=rtol, atol=atol)
        assert ta.val.shape == tb.val.shape


def test_dump_three_tables_layout():
    af = parse(CL_TABLE + '\n' + CD_TABLE + '\n' + CM_TABLE)
    out = io.StringIO()
    c81.dump_csv(af, out)
    text = out.getvalue()
    assert text.endswith('\n') and not text.endswith('\n\n')
    blocks = text.split('\n\n')
    assert len(blocks) == 3
    assert blocks[0].splitlines()[0] == '0,0.0,0.3,0.6,0.9'
    assert len(blocks[0].splitlines()) == 6
    assert len(blocks[1].splitlines()) == 4
    assert len(blocks[2].splitlines()) == 3


def test_roundtrip_different_grids_exact():
    af = parse(CL_TABLE + '\n' + CD_TABLE + '\n' + CM_TABLE)
    buf = io.StringIO()
    c81.dump_csv(af, buf)
    buf.seek(0)
    assert_same_data(af, c81.load_csv(buf))


def test_roundtrip_full_precision(tmp_path):
    rng = np.random.default_rng(1)
    alpha = np.linspace(-3.3, 7.7, 7) + 1 / 3
    mach = np.array([0.0, 0.1 + 1e-9, 1 / 3, 0.9])
    cl = rng.normal(size=(7, 4)) * 1e-5
    cl[0, 0] = 1.0 / 7.0
    af = c81.C81('x', alpha, mach, cl, alpha, mach, cl * 2, alpha, mach, cl * 3)
    p = tmp_path / 'x.csv'
    c81.dump_csv(af, p)
    assert_same_data(af, c81.load_csv(p))      # bit-exact


def test_dump_to_path_and_str_and_file_object(tmp_path):
    af = parse(CL_TABLE)
    c81.dump_csv(af, tmp_path / 'a.csv')
    c81.dump_csv(af, str(tmp_path / 'b.csv'))
    with open(tmp_path / 'c.csv', 'w') as f:
        c81.dump_csv(af, f)
    texts = {(tmp_path / n).read_text() for n in ('a.csv', 'b.csv', 'c.csv')}
    assert len(texts) == 1
    with open(tmp_path / 'c.csv') as f:
        assert_same_data(af, c81.load_csv(f))


def test_c81_to_csv_to_load_roundtrip(tmp_path):
    with open(os.path.join(TESTS, 'sample1.C81')) as f:
        original = c81.load(f)       # 12 Mach columns for CL, other sizes for CD/CM
    p = tmp_path / 'converted.csv'
    c81.dump_csv(original, p)
    restored = c81.load_csv(p)
    assert_same_data(original, restored)
    assert original.getCL(10.0, 0.42) == pytest.approx(restored.getCL(10.0, 0.42))
    assert restored.getCD(3.0, 0.2) == pytest.approx(original.getCD(3.0, 0.2))


def test_load_csv_object_is_interpolatable():
    af = parse(CL_TABLE)
    # bilinear: row alpha=0 is 0; row alpha=5 at M=0.15 is (0.4+0.35)/2
    assert af.getCL(2.5, 0.15) == pytest.approx(0.1875)
    assert af.getCD(2.5, 0.15) == 0.0
