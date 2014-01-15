import os
import re
import xml.etree.ElementTree as ElementTree
from CsvTool import CsvTool

# setup logger
import logging
logging.basicConfig(format='%(asctime)-15s %(message)s', filename='IngTool.log')

logger = logging.getLogger(__name__)
logger.setLevel (logging.INFO)

class IngTool ():
    """This tool converts the af- en bijschrijving of an ING account to nice looking stats.
    To get af- en bijschrijvingen from an ING account, do the following:
    1. Login @ ing.nl
       a. 'af- en bijschrijvingen'
       b. 'download'
       c. 'komma gescheiden'
       d. I do this for a whole year. The current year has to be refreshed everytime...
    2. In the CSV file
       a. rename 'Naam / Omschrijving' to 'Omschrijving'
       b. rename 'Bedrag (EUR)' to 'Bedrag'
       c. replace all ',' by '.' (in Column Bedrag)
       d. set data type of column 'Bedrag' to number with 2 decimals
       e. in column 'Tegenrekening' replace all 'M ' by ''
       f. in column 'Rekening' replace all ' ' by ''
       g. replace all '"' by ''
       """

    def __init__ (self):
        self.accounts ={}
        self.files = []
        self.csv = None
        
        self.coveredIDs = []
        self.forgottenIDs = []
        
        self.idxEUR = None
        self.allIndices = []
        
    
    def LoadAccountsFromFile (self, inXmlfile):
        """Read a XML file containing account information and store it in self.accounts (dict)
        The XML file has the following structure:
        <accounts>
            <account name="NAME" number="NUMBER"/>
            ...
        </accounts>
        """
        tree = ElementTree.parse (inXmlfile)
        accounts = tree.getroot ()
        for account in accounts:
            self.accounts [account.attrib['name']] = account.attrib['number']
            
    def LoadFilesFromFile (self, inXmlfile):
        """Read a XML file containing name of CSV files with af- en bijschrijvingen and store it in self.files (list)
        The XML file has the following structure:
        <files path="PATH">
            <file name="NAME"/>
            ...
        </files>
        """
        tree = ElementTree.parse (inXmlfile)
        files = tree.getroot ()
        path = files.attrib['path']
        for file in files:
            pathToFile = os.path.join (path, file.attrib['name'])
            self.files.append (pathToFile)
    
    def RunQueriesFromFile (self, inXmlfile):
        """Read a XML file containing the queries to run
        <queries>
            <query name="inkomsten" subname="private" subsubname="ashgard">
                <and AfBij="Af"/>
                <and Tegenrekening="ashagrd"/>
            </query>
            <query name="uitgaven" subname="overige" subsubname="klussen">
                <and AfBij="Af"/>
                <and>
                    <or Mededelingen="gamma"/>
                    <or Mededelingen="formido"/>
                    <or Mededelingen="provos"/>
                    <or Mededelingen="j.k. van den dool"/>
                    <or Mededelingen="barselaar"/>
                    <or Mededelingen="intratuin"/>
                    <or Mededelingen="de bosrand"/>
                </and>
            </query>
        </queries>"""
        if not self.csv:
            self.__LoadCsv (self.files)
        self.idxEUR = self.csv.headers.index ('BedragEUR')
        
        tree = ElementTree.parse (inXmlfile)
        queries = tree.getroot ()
        
        ret = {}
        for query in queries:
            hasSubname = False
            hasSubsubname = False
            
            name = query.attrib ['name']
            if name not in ret:
                ret [name] = {}
            
            if 'subname' in query.attrib:
                hasSubname = True
                subname = query.attrib ['subname']
                if subname not in ret [name]:
                    ret [name][subname] = {}
                
            if 'subsubname' in query.attrib:
                hasSubsubname = True
                subsubname = query.attrib ['subsubname']
                if subsubname not in ret [name][subname]:
                    ret [name][subname][subsubname] = {}
            
            query = self.ConvertQueryToStringRecursive (query)
            query = self.SubstituteAccounts (query)
            
            result, indices = self.csv.RunQuery (query)
            self.allIndices += indices
            
            total = 0.0
            for row in result:
                total += float (row [self.idxEUR])
            
            if hasSubsubname:
                ret [name][subname][subsubname] = total
            elif hasSubname:
                ret [name][subname] = total
            else:
                ret [name] = total
            
        if self.HasDuplicates (self.allIndices):
            duplicates = GetDuplicates (self.allIndices)
            logger.error ("Double indices, results cannot be thrusted! Doubles are: %s" % duplicates)
            raise AssertionError, "Duplicates found in all indices. See log file for more info"
            
        return ret
    
    def __LoadCsv (self, inCsvFiles):
        """Prepare CsvTool to run queries on CSV file(s)"""
        self.csv = CsvTool ()
        self.csv.LoadFile (inCsvFiles)
        
    def HasDuplicates (self, inList):
        lenList = len (inList)
        lenSet = len (set (inList))
        return lenList != lenSet
        
    def GetDuplicates (self, inIndices):
        ret = set()
        previousIndex = None
        for index in inIndices:
            if index is previousIndex:
                ret.add (index)
            previousIndex = index
        return ret
        
        
    def ConvertQueryToStringRecursive (self, inQuery):
        query = []
        for logic in inQuery:
            if logic.attrib:
                
                equal = True
                if "equal" in logic.attrib.keys ():
                    equal = (logic.attrib['equal'] == "True")
                    
                for key, value in logic.attrib.items():
                    if key != "equal":
                        if equal:
                            query.append (key + '=="' + value + '"')
                        else:
                            query.append ('"' + value + '" in ' + key)
            else:
                query.append (self.ConvertQueryToStringRecursive (logic))
                
        logicstring = " " + logic.tag + " "
        query = logicstring.join(query)
        query = "(" + query + ")"
        return query
        
    def SubstituteAccounts (self, inQuery):
        """Replace the account of someonw by its account,
        This function searches for the pattern Tegenrekening="NAME"
        It replaces NAME by the account if it is listed in the file accounts.xml"""
        pattern = 'Tegenrekening==\"[a-zA-z]+\"'
        results = re.findall (pattern, inQuery)
        
        outQuery = inQuery
        for result in results:
            pattern = '\"[a-zA-z]+\"'
            m = re.search (pattern, result)
            name = m.group(0)[1:-1]
            
            if name in self.accounts:
                account = self.accounts[name]
                outQuery = re.sub ('"' + name + '"', account, outQuery)
        return outQuery
        
        
if __name__ == '__main__':
    ing = IngTool ()
    ing.LoadAccountsFromFile ("accounts.xml")
    ing.LoadFilesFromFile ("files.xml")
    ing.RunQueriesFromFile ("queries.xml")
    
    