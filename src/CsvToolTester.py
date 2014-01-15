#!/usr/bin/env python
from CsvTool import CsvTool
import unittest
import csv
import os

# setup logger
import logging
logging.basicConfig(format='%(asctime)-15s %(message)s', filename='CsvToolTester.log')
logger = logging.getLogger(__name__)
       
       
class TestLoadCsvFile(unittest.TestCase):

    def setUp(self):
        logger.warning('Tester setUp')
        self.d=CsvTool()
        self.d.LoadFile('test/unittest.csv')

    def testHeader(self):
        """There should be a function to retrieve all header names"""
        hnames = self.d.GetHeaderNames()
        self.assertEqual(['Int', 'Float', 'String', 'Date', 'Empty'], hnames)
        
        # test col types
        expected = {}
        expected['Int'] = 'int'
        expected['Float'] = 'float'
        expected['String'] = 'str'
        expected['Date'] = 'str'
        expected['Empty'] = 'str'
        actual = self.d.colTypes
        self.assertEqual (expected ,actual)
        
    def testUnique(self):
        """The label 'Hallo' occurs multiple times. So if we get all unique Strings, it should only contain 'Hello' once."""
        unique = self.d.GetUnique('String')
        self.assertEqual(set(['Hallo','Zout','Goedemorgen','Doei!','Lol']), unique)

    def testType(self):
        """It should detect integers, floats, etc"""
        value = '4'
        self.assertEqual(True,self.d.IsInt(value))
        self.assertEqual(False,self.d.IsFloat(value))
        self.assertEqual(False,self.d.IsDate(value))
        
        value = '4.0'
        self.assertEqual(False,self.d.IsInt(value))
        self.assertEqual(True,self.d.IsFloat(value))
        self.assertEqual(False,self.d.IsDate(value))
        
        value = '0.4'
        self.assertEqual(False,self.d.IsInt(value))
        self.assertEqual(True,self.d.IsFloat(value))
        self.assertEqual(False,self.d.IsDate(value))
        
    def testOutindices(self):
        """The RunQeury function should return which rows were evaluated sucessful"""
        idx = self.d.GetHeaderNames().index('Int')
        
        query = 'Int == 1'
        result, ind = self.d.RunQuery(query)
        self.assertEqual([0], ind)
        
        query = 'Int == 1 or Int == 2 '
        result, ind = self.d.RunQuery(query)
        self.assertEqual([0, 1, 2], ind)
        
    def testInt(self):
        """It should be possible to do query operations on Integers"""
        idx = self.d.GetHeaderNames().index('Int')
        
        query = 'Int == 1'
        result, ind = self.d.RunQuery(query)
        self.assertEqual('1', result[0][idx])
        
        query = 'Int < 1'
        result, ind = self.d.RunQuery(query)
        self.assertEqual('-5', result[0][idx])
        
        query = 'Int > 1'
        result, ind = self.d.RunQuery(query)
        ints = []
        for i in range(len(result)):
            ints.append(result[i][idx])
        self.assertEqual(['2','2','4','6','6'], ints)
    
    def testFloat(self):
        """It should be possible to do query operations on Floats"""
        idx = self.d.GetHeaderNames().index('Float')
    
        query = 'Float == 0.10'
        result, ind = self.d.RunQuery(query)
        self.assertEqual('0.1', result[0][idx])
    
        query = 'Float == 1.0'
        result, ind = self.d.RunQuery(query)
        self.assertEqual('1.0', result[0][idx])
        
        query = 'Float < 0'
        result, ind = self.d.RunQuery(query)
        self.assertEqual('-1.5', result[0][idx])
    
        query = 'Float >= 4.3'
        result, ind = self.d.RunQuery(query)
        floats = []
        for i in range(len(result)):
            floats.append(result[i][idx])
        self.assertEqual(['4.3','7.1'], floats)
    
    def testString(self):
        """It should be possible to do query operations on Strings"""
        idx = self.d.GetHeaderNames().index('String')
        
        query = 'String == "Zout"'
        result, ind = self.d.RunQuery(query)
        self.assertEqual('Zout', result[0][idx])
    
        query = 'String == "Hallo"'
        result, ind = self.d.RunQuery(query)
        strings = []
        for i in range(len(result)):
            strings.append(result[i][idx])
        self.assertEqual(['Hallo','Hallo','Hallo'], strings)

        query = '"!" in String'
        result, ind = self.d.RunQuery(query)
        self.assertEqual('Doei!', result[0][idx])
        
        query = '("e" in String or "!" in String) and "D" in String'
        result, ind = self.d.RunQuery(query)
        self.assertEqual('Doei!', result[0][idx])
        
    
    #def testDate(self):
    #    """It should be possible to do query operations on Dates"""
    #    idx = self.d.GetHeaderNames().index('Date')
    #    
    #    query = 'Date == 20130621'
    #    result = self.d.RunQuery(query)
    #    self.assertEqual('20130621', result[0][idx])
    #
    #    query = 'Date <= 20130620'
    #    result = self.d.RunQuery(query)
    #    dates = []
    #    for i in range(len(result)):
    #        dates.append(result[i][idx])
    #    self.assertEqual(['20130615','20120628'], dates)

if __name__ == '__main__':
    unittest.main()

