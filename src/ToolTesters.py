from xmlrunner import XMLTestRunner
import CsvToolTester
import unittest

def run_tests ():
    suite = unittest.TestSuite ()
    loader = unittest.TestLoader ()

    suite.addTest (loader.loadTestsFromModule (CsvToolTester))

    runner = XMLTestRunner(file('testoutput.xml', "w"))
    result = runner.run(suite)

if __name__=="__main__":
    run_tests ()
