"""Tests for fault detection and exclusion methods.

"""

__authors__ = "D. Knowles"
__date__ = "11 Jul 2023"

import os

import pytest
import numpy as np

from gnss_lib_py.algorithms.fde import solve_fde
from gnss_lib_py.parsers.android import AndroidDerived2022

@pytest.fixture(name="root_path_2022")
def fixture_root_path_2022():
    """Location of measurements for unit test.

    Returns
    -------
    root_path_2022 : string
        Folder location containing measurements.

    """
    root_path = os.path.dirname(
                os.path.dirname(
                os.path.dirname(
                os.path.realpath(__file__))))
    root_path_2022 = os.path.join(root_path, 'data','unit_test','android_2022')
    return root_path_2022


@pytest.fixture(name="derived_2022_path")
def fixture_derived_2022_path(root_path_2022):
    """Filepath of Android Derived measurements.

    Parameters
    ----------
    root_path_2022 : string
        Folder location containing measurements.

    Returns
    -------
    derived_2022_path : string
        Location for the unit_test Android derived 2022 measurements.

    Notes
    -----
    Test data is a subset of the Android Raw Measurement Dataset [1]_,
    from the 2022 Decimeter Challenge. Particularly, the
    train/2021-04-29-MTV-2/SamsungGalaxyS20Ultra trace. The dataset
    was retrieved from
    https://www.kaggle.com/competitions/smartphone-decimeter-2022/data

    References
    ----------
    .. [1] Fu, Guoyu Michael, Mohammed Khider, and Frank van Diggelen.
        "Android Raw GNSS Measurement Datasets for Precise Positioning."
        Proceedings of the 33rd International Technical Meeting of the
        Satellite Division of The Institute of Navigation (ION GNSS+
        2020). 2020.

    """
    derived_2022_path = os.path.join(root_path_2022, 'device_gnss.csv')
    return derived_2022_path

@pytest.fixture(name="derived")
def fixture_load_derived(derived_2022_path):
    """Load instance of AndroidDerived2022.

    Parameters
    ----------
    derived_2022_path : pytest.fixture
        String with location of Android derived measurement file.

    Returns
    -------
    derived : AndroidDerived2022
        Instance of AndroidDerived2022 for testing.

    """
    derived = AndroidDerived2022(derived_2022_path)
    return derived

def test_fde_residual(derived):
    """Test residual-based FDE.

    Parameters
    ----------
    derived : AndroidDerived2022
        Instance of AndroidDerived2022 for testing.

    """

    # test without removing outliers
    navdata = derived.copy()
    navdata = solve_fde(navdata)
    assert "fault_residual" in navdata.rows

    # test with removing outliers
    navdata = derived.copy()
    navdata = solve_fde(navdata,remove_outliers=True)
    assert "fault_residual" in navdata.rows
    np.testing.assert_array_equal(np.unique(navdata["fault_residual"]),
                                  np.array([0]))

def test_fde_ss(derived):
    """Test solution separation FDE.

    Parameters
    ----------
    derived : AndroidDerived2022
        Instance of AndroidDerived2022 for testing.

    """


    # test without removing outliers
    navdata = derived.copy()
    navdata = solve_fde(navdata,"ss")
    assert "fault_ss" in navdata.rows

    # test with removing outliers
    navdata = derived.copy()
    navdata = solve_fde(navdata,"ss",remove_outliers=True)
    assert "fault_ss" in navdata.rows
    np.testing.assert_array_equal(np.unique(navdata["fault_ss"]),
                                  np.array([0]))

def test_fde_edm(derived):
    """Test Euclidean distance matrix-based FDE.

    Parameters
    ----------
    derived : AndroidDerived2022
        Instance of AndroidDerived2022 for testing.

    """


    # test without removing outliers
    navdata = derived.copy()
    navdata = solve_fde(navdata,"edm")
    assert "fault_edm" in navdata.rows

    # test with removing outliers
    navdata = derived.copy()
    navdata = solve_fde(navdata,"edm",remove_outliers=True)
    assert "fault_edm" in navdata.rows
    np.testing.assert_array_equal(np.unique(navdata["fault_edm"]),
                                  np.array([0]))

def test_fde_fails(derived):
    """Test that solve_fde fails when it should.

    Parameters
    ----------
    derived : AndroidDerived2022
        Instance of AndroidDerived2022 for testing.

    """

    with pytest.raises(ValueError) as excinfo:
        solve_fde(derived, method="perfect_method")
    assert "invalid method" in str(excinfo.value)
