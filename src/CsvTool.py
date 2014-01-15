import csv
import datetime
import logging
logger = logging.getLogger(__name__)

class CsvTool:
    """ This tool allows you to read CSV file by python and easily apply queries on it"""
    def __init__(self):
        self.csvTable = []
        self.headers = []
        self.colTypes = []
        
    def LoadFile(self, inFilename):
        if isinstance (inFilename, list):
            headerprev = None
            for filename in inFilename:
                csvData = csv.reader (open (filename))
                self.__GetCsvTable (csvData)
                if headerprev:
                    if self.headers != headerprev:
                        print self.headers
                        print headerprev
                        logger.error ("Header of CSV file %s is not the same as the previous one!", filename)
                        assert (False)
                headerprev = self.headers
                
        else:
            csvData = csv.reader (open (inFilename))
            self.__GetCsvTable (csvData)
        
        self.__SetColType()

    def __GetCsvTable(self,inCsvData):
        isHeader = True
        count=0
        for row in inCsvData:
            if isHeader:
                isHeader = False
                self.headers = row
                for i in range(len(self.headers)):
                    # the following sympols are not allowed in header
                    self.headers[i] = self.headers[i].replace(' ', '')
                    self.headers[i] = self.headers[i].replace('/', '')
                    self.headers[i] = self.headers[i].replace('(', '')
                    self.headers[i] = self.headers[i].replace(')', '')
            else:
                # the following symbols are not allowed in data
                #row = [cell.replace(',', '.') for cell in row] # does not work! you have manually replace the ,-symbols by .-symbols in the csv file
                row = [cell.replace('\\', '') for cell in row]
                row = [cell.replace('"', '') for cell in row]
                # make sure row has correct length, otherwise fill with empty cells
                while len(row) < len(self.headers):
                    row.append(',')
                self.csvTable.append(row)
                count += 1

    def __SetColType (self):
        self.colTypes = {}
        tableTransposed = map(list, zip(*self.csvTable))
        for i, col in enumerate (tableTransposed):
            colType = []
            header = self.headers [i]
            
            for elem in col:
                colType.append (self.__GetColType (elem))
            
            self.colTypes [header] = self.__GetColTypeFromList (colType)
            
    def __GetColType (self, inValue):
        ret = 'str'
        if inValue is not "":
            if self.IsFloat(inValue):
                ret = 'float'
            elif self.IsInt(inValue):
                ret = 'int'
            #if self.IsDate(value):
            #    self.csvTable[j][i] = self.__ConvertDateToInt(value)
            #    colT = 'int'
            #else (isFloat is False and isInt is False):
                # remove new lines
                #self.csvTable[j][i] = value.replace('\n', '. ')
        return ret
        
    def __GetColTypeFromList (self, inList):
        mydict = {
            'str': inList.count ('str'),
            'int': inList.count ('int'),
            'float': inList.count ('float')
        }
        return max (mydict, key=mydict.get)
        
    
    
    def __SetColType2(self):
        # determine column types: string/int/float
        for i in range(len(self.headers)):
            isInt = False
            isFloat = False
            for j in range(len(self.csvTable)):
                #should i do a check to see if all are equal?
                value = self.csvTable[j][i]
                if value is not "":
                    isFloat = self.IsFloat(value)
                    isInt = self.IsInt(value)
                    if self.IsDate(value):
                        self.csvTable[j][i] = self.__ConvertDateToInt(value)
                        isInt = True
                    if (isFloat is False and isInt is False):
                        # remove new lines
                        self.csvTable[j][i] = value.replace('\n', '. ')

            colT = ''
            if isInt:
                colT = 'int'
            elif isFloat:
                colT = 'float'
            else:
                colT = 'str'
            self.colType.append(colT)
          
    def RunQuery(self, inQuery):
        outList = []
        outIndices = []
        for j in range(len(self.csvTable)):
            # assign the column variables
            for i in range(len(self.headers)):
                header = self.headers [i]
                value  = self.csvTable[j][i]
                type  = self.colTypes[header]
                forceFalseResult = False
                
                if value is '':
                    # if no value is supplied while the other values in the same column are identified as float or int, then force a False result
                    if type == 'float' or type == 'int':
                        forceFalseResult = True
                    else:
                        type = 'str'
                        value = str (value)
                elif type == 'float':
                    # make sure it is a float
                    try:
                        value = str (float (value))
                    except ValueError:
                        logger.error ("Could not convert to float: %s. You have to correct the value in the CSV file yourself!", str (value))
                        print self.csvTable[j]
                        assert (False)
                elif type == 'int':
                    # make sure it is an int:
                    # first convert possible string to float, this prevents invalid literals
                    # then convert float to int
                    try:
                        value = str (int (float (value)))
                    except ValueError:
                        logger.error ("Could not convert to integer: %s. You have to correct the value in the CSV file yourself!", str (value))
                        print self.csvTable[j]
                        assert (False)
                else:
                    # Everything else should be string
                    value = str (value)
                
                # run statement to see if it is true
                if not forceFalseResult:
                    exec (header + '=' + type + '("' + value + '")')
                else:
                    exec ('False')
                
                # write back changes
                self.csvTable[j][i] = value    
                        
            # output the rows matching the query
            if eval(inQuery):
                outList.append (self.csvTable[j])
                outIndices.append (j)
    
        return outList, outIndices

    def IsFloat(self, inValue):
        ret = False
        if not self.IsInt(inValue):
            try:
                if isinstance(float(inValue), float):
                    ret = True
            except ValueError:
                pass
        return ret
    
    def IsInt(self, inValue):
        ret = False
        try:
            if isinstance(int(inValue), int):
                ret = True
        except ValueError:
            pass
        return ret
        
    def IsDate(self, inValue):
        try:
            datetime.datetime.strptime(inValue, '%b %d, %Y')
            return True
        except ValueError:
            return False

    def __ConvertDateToInt(self, inValue):
        d = datetime.datetime.strptime(inValue, '%b %d, %Y')
        d = '%4d%2d%2d' % (d.year, d.month, d.day)
        return d.replace(' ','0')
        
    def GetHeaderNames(self):
        return self.headers

    def GetUnique(self,inString):
        index=self.headers.index(inString)
        labels=set()
        for j in range(len(self.csvTable)):
            label=self.csvTable[j][index]
            if label not in labels and "," not in label and label is not "":
                labels.add(label)
        return labels
