
import logging
import unittest.mock as mock
import unittest
import bayesianpy.network
import iris
import pandas as pd
import dask.dataframe as dd
import bayesianpy.dask.cross_validation as cross_validation

def create_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    return logger

class CrossValidationTestCase(unittest.TestCase):

    def test_build_indices(self):
        ds = dd.from_pandas(iris.create_iris_dataset(), npartitions=2)
        total_length = len(ds)
        kf = cross_validation.KFold(4)
        ds['unique_index'] = 1
        ds['unique_index'] = ds['unique_index'].cumsum()
        folds = 0
        for (training, testset) in kf.split(ds):
            train_indices = set(training.unique_index.compute().tolist())
            test_indices = set(testset.unique_index.compute().tolist())

            self.assertEqual(len(train_indices.intersection(test_indices)), 0)
            self.assertEqual(len(train_indices) + len(test_indices), total_length)

            self.assertTrue(((total_length / 4) * 3) - 10< len(training) <= ((total_length / 4) * 3) + 10, "{} is more or less than expected value {}".format(len(training), (len(ds) / 4) * 3))
            self.assertTrue(((total_length / 4) - 10) < len(testset) <= ((total_length / 4) + 10))
            folds += 1

        self.assertEqual(4, folds)