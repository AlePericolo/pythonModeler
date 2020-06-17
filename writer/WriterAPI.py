from datetime import datetime

class WriterAPI:

    def __init__(self, table, columns, creatTableSyntax, format):
        self.table = table
        self.columns = columns
        self.creatTableSyntax = creatTableSyntax
        if format:
            self.format = '\n'
        else:
            self.format = ''
        self.file = '<?php\n'

    def writeFile(self):
        self.file += self.__developedBy() + '\n'
        self.file += '\n'
        self.file += self.__initClass() + '\n'
        self.file += self.__attributes() + '\n'
        self.file += self.__printParagraph('CONSTRUCTOR', 102) + '\n'
        self.file += self.__costructor() + '\n'
        self.file += self.__printParagraph('FUNCTIONS', 104) + '\n'
        self.file += self.__read() + '\n'

        self.file += self.__endClass()
        return self.file

    #===================================================================================================================
    # PRIVATE FUNCTION
    #===================================================================================================================

    def __developedBy(self):
        signature = '/**\n'
        signature += '* Developed by: Alessandro Pericolo\n'
        signature += '* Date: ' + datetime.now().strftime('%d/%m/%Y') + '\n'
        signature += '* Time: ' + datetime.now().strftime('%H:%M') + '\n'
        signature += '* Version: 0.1\n'
        signature += '**/'
        return signature

    # ------------------------------------------------------------------------------------------------------------------

    def __initClass(self):
        return 'class ' + self.table.title() + ' {\n'

    # ------------------------------------------------------------------------------------------------------------------

    def __attributes(self):
        app = 'private $conn;\n'
        app += 'private $this->tableName = "' + self.table + '";\n\n'
        for element in self.columns:
            type = self.__getAttributeTypeByElement(element)
            #signature
            app += '/** @var ' + type
            if element[3] == 'PRI':
                app += ' PrimaryKey'
            app += '*/\n'
            #attribute
            app += 'public $' + element[0]
            #default value
            if element[4]:
                if type == 'integer':
                    app += ' = ' + element[4] + ';'
                else:
                    app += ' = "' + element[4] + '"; '
            else:
                app += ';'
            app += '\n'
        return app

    # ------------------------------------------------------------------------------------------------------------------

    def __costructor(self):
        app = '//constructor\n'
        app += 'function __construct($conn){' + self.format
        app += '\t$this->conn= $conn;' + self.format
        app += '}\n'
        return app

    # ------------------------------------------------------------------------------------------------------------------

    def __read(self):
        app = 'function read(){' + self.format
        app += self.__writeLogInit('read')
        app += '\n\t$query = "SELECT * " . "FROM " . $this->table_name;' + self.format
        app += '\tfwrite($logfile, "\\n\\nQUERY: ". $query."\\n\\n");' + self.format
        app += '\n\t$query_result = $this->conn->query($query);' + self.format
        app += '\n\t$response = [];' + self.format
        app += '\t$response = [\'query\'] = str_replace(["\'", \'"\'],"",$query);' + self.format
        app += '\t$response = ["data"] = [];' + self.format
        app += '\n\tif(!$query_result){'+ self.format
        app += '\t\t$response["status_code"] = 404;' + self.format
        app += '\t\t$response["status_text"] = "K0";' + self.format
        app += '\t\t$result["message"] = $this->conn->error;' + self.format
        app += '\t} else {' + self.format
        app += '\t\t$response["status_code"] = 200;' + self.format
        app += '\t\t$response["status_text"] = "0K";' + self.format
        app += '\t\t$result["message"] = "' + self.table + ' found "' + self.format
        app += '\t\tif(mysqli_num_rows($query_result) > 0){' + self.format
        app += '\t\t\twhile ($row = mysqli_fetch_assoc($query_result)){' + self.format
        app += '\t\t\t\t$element = array(' + self.format
        app += self.__writeObjectArray()
        app += '\t\t\t\t);' + self.format
        app += '\t\t\t\tarray_push($response["data"], $element);' + self.format
        app += '\t\t\t}' + self.format
        app += '\t\t}' + self.format
        app += '\t}\n'
        app += '\n\t$this->conn->close();' + self.format
        app += self.__writeLogEnd('read')
        app += '\n\treturn json_encode($response);' + self.format
        app += '}\n'
        return app

    # ------------------------------------------------------------------------------------------------------------------

    def __endClass(self):
        return '} //close Class ' + self.table.title()

    #===================================================================================================================
    # UTILITY
    #===================================================================================================================

    def __printParagraph(self, title, length = 100):
        p = '/* ' + title + ' '
        for x in range(length):
            p += '-'
        p += ' */\n'
        return p

    def __printLogSeparator(self, separator, length = 100):
        p = ' " '
        for x in range(length):
            p += separator
        p += ' "'
        return p

    def __writeLogInit(self,type):
        log = '\n\terror_log("'+type+'");' + self.format
        log += '\t$logfile = fopen("../log/' + self.table + '_'+type+'.txt", "w") or die("Unable to open file!");' + self.format
        log += '\tfwrite($logfile, "'+type+' LOG: ". date("d/m/yy h:i:s a") ' + self.__printLogSeparator('=', 50) + ' );' + self.format
        return log

    def __writeLogEnd(self,type):
        log = '\n\terror_log("'+type+' response => ". json_encode($response));' + self.format
        log += '\tfwrite($logfile, "response: ". json_encode($response)."\\n\\n");' + self.format
        log += '\tfclose($logfile);' + self.format
        return log

    def __writeObjectArray(self):
        arr = ''
        for element in self.columns:
            arr += '\t\t\t\t\t"' + element[0] + '" => $row["' + element[0] + '"],' + self.format
        return arr

    # ------------------------------------------------------------------------------------------------------------------

    def __getAttributeTypeByElement(self, element):
        if "(" in element[1]:
            check = element[1].split("(")[0]
        else:
            check = element[1]

        if check in ['int', 'tinyint', 'float', 'double', 'decimal']:
            return 'integer'
        elif check in ['varchar', 'blob', 'text', 'enum', 'tinytext']:
            return 'string'
        elif check in ['date', 'datetime', 'timestamp']:
            return 'DateTime'
        else:
            return ''