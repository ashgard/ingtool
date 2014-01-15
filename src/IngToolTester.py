#!/usr/bin/env python
import unittest
import logging
import os
import xml.etree.ElementTree as ElementTree
from IngTool import IngTool

# setup logger
logging.basicConfig(format='%(asctime)-15s %(message)s', filename='IngToolTester.log')
logger = logging.getLogger(__name__)
       
       
class IngToolTester(unittest.TestCase):

    def setUp(self):
        self.ing=IngTool()
        
    def testLoadAccountsFromFile (self):
        """Loading accounts from an XML file should return a dict with accounts in the Tool"""
        self.ing.LoadAccountsFromFile ("test/test_accounts.xml")
        self.assertEqual ({'ashgard':'1234', 'gerdien':'4321'}, self.ing.accounts)
        
    def testLoadFilesFromFile (self):
        """Loading files from an XML file should return a list with files in the Tool"""
        self.ing.LoadFilesFromFile ("test/test_files.xml")
        self.assertEqual (["test/first.csv", "test/second.csv"], self.ing.files)
        
    def testConvertQueryToString (self):
        """It should be simple to define queries in XML file which are parsed easily"""
        query  = ElementTree.Element ("query")
        query.set ("name", "inkomsten")
        query.set ("subname", "private")
        query.set ("subsubname", "ashgard")
        logicand = ElementTree.SubElement(query, "and")
        logicand.set ("AfBij", "Bij")
        logicand = ElementTree.SubElement(query, "and")
        logicand.set ("Tegenrekening", "ashgard")
        
        expected = '(AfBij=="Bij" and Tegenrekening=="ashgard")'
        actual = self.ing.ConvertQueryToStringRecursive (query)
        self.assertEqual (expected, actual)
        
        query  = ElementTree.Element ("query")
        query.set ("name", "uitgaven")
        query.set ("subname", "overige")
        query.set ("subsubname", "klussen")
        logicand = ElementTree.SubElement(query, "and")
        logicand.set ("AfBij", "Af")
        logicand = ElementTree.SubElement(query, "and")
        logicor = ElementTree.SubElement(logicand, "or")
        logicor.set ("Mededelingen", "gamma")
        logicor.set ("NaamOmschrijving", "gamma")
        logicor.set ("equal", "True")
        logicor = ElementTree.SubElement(logicand, "or")
        logicor.set ("Mededelingen", "formido")
        logicor.set ("equal", "False")
        logicor = ElementTree.SubElement(logicand, "or")
        logicor.set ("Mededelingen", "intratuin")
        
        expected = '(AfBij=="Af" and (NaamOmschrijving=="gamma" or Mededelingen=="gamma" or "formido" in Mededelingen or Mededelingen=="intratuin"))'
        actual = self.ing.ConvertQueryToStringRecursive (query)
        self.assertEqual (expected, actual)
        
    def testSubstituteAccounts (self):
        """The tool should recognize if an account belongs to someone and replace the name by its account number"""
        self.ing.LoadAccountsFromFile ("test/test_accounts.xml")
        query = 'AfBij=="Af" and Tegenrekening=="ashgard" or Tegenrekening=="gerdien"'
        actual = self.ing.SubstituteAccounts (query)
        expected = 'AfBij=="Af" and Tegenrekening==1234 or Tegenrekening==4321'
        self.assertEqual (expected, actual)
        
    def testHasDuplicates (self):
        self.assertEqual (False, self.ing.HasDuplicates ([0,1,2,3,4,5]))
        self.assertEqual (True, self.ing.HasDuplicates ([0,1,1,2,2,2]))
        
    def testGetDuplicates (self):
        expected = set()
        actual = self.ing.GetDuplicates ([0,1,2,3,4,5])
        self.assertEqual (expected, actual)
        
        expected = set([1,2,3,8])
        actual = self.ing.GetDuplicates ([0,1,1,2,2,2,3,3,4,5,6,7,8,8])
        self.assertEqual (expected, actual)
        
        
    def testRunQueriesFromFile (self):
        """Test the whole function, get results from the ran queries"""
        self.ing.LoadAccountsFromFile ("test/test_accounts.xml")
        self.ing.LoadFilesFromFile ("test/test_files.xml")
        results = self.ing.RunQueriesFromFile ("test/test_queries.xml")
        
        
        ik wil graag de results naar een XML file gooien, dat is veel mooier dan wat ik nu heb...
        
        
if __name__ == '__main__':
    unittest.main()

