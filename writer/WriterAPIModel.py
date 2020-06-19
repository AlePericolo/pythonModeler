from datetime import datetime

class WriterAPIModel:

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
        self.file += self.__delete() + '\n'
        self.file += self.__create() + '\n'
        self.file += self.__update() + '\n'

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
        return 'class ' + self.table.title() + '_Model {\n'

    # ------------------------------------------------------------------------------------------------------------------

    def __attributes(self):
        app = 'protected $conn;\n'
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
        app += '\t$this->table_name = "' + self.table + '";'
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
        app += '\t$response[\'query\'] = str_replace(["\'", \'"\'],"",$query);' + self.format
        app += '\t$response["data"] = [];' + self.format
        app += '\n\tif(!$query_result){'+ self.format
        app += '\t\t$response["status_code"] = 404;' + self.format
        app += '\t\t$response["status_text"] = "K0";' + self.format
        app += '\t\t$response["message"] = json_encode($this->conn->error);' + self.format
        app += '\t} else {' + self.format
        app += '\t\t$response["status_code"] = 200;' + self.format
        app += '\t\t$response["status_text"] = "0K";' + self.format
        app += '\t\t$response["message"] = "' + self.table + ' found ";' + self.format
        app += '\t\tif(mysqli_num_rows($query_result) > 0){' + self.format
        app += '\t\t\twhile ($row = mysqli_fetch_assoc($query_result)){' + self.format
        app += '\t\t\t\t$element = array(' + self.format
        app += self.__writeFetchReadQuery()
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

    def __delete(self):
        app = 'function delete(){' + self.format
        app += self.__writeLogInit('delete')
        app += '\n\t$query = "DELETE FROM " . $this->table_name . " WHERE id = " . $this->id ;' + self.format
        app += '\tfwrite($logfile, "\\n\\nQUERY: ". $query."\\n\\n");' + self.format
        app += '\n\t$query_result = $this->conn->query($query);' + self.format
        app += '\n\t$response = [];' + self.format
        app += '\t$response[\'query\'] = str_replace(["\'", \'"\'],"",$query);' + self.format
        app += '\n\tif(!$query_result){'+ self.format
        app += '\t\t$response["status_code"] = 503;' + self.format
        app += '\t\t$response["status_text"] = "K0";' + self.format
        app += '\t\t$response["message"] = json_encode($this->conn->error);' + self.format
        app += '\t} else {' + self.format
        app += '\t\t$response["status_code"] = 200;' + self.format
        app += '\t\t$response["status_text"] = "0K";' + self.format
        app += '\t\t$response["message"] = "' + self.table + ' deleted ";' + self.format
        app += '\t}' + self.format
        app += '\n\t$this->conn->close();' + self.format
        app += self.__writeLogEnd('delete')
        app += '\n\treturn json_encode($response);' + self.format
        app += '}\n'
        return app

    def __create(self):
        app = 'function create(){' + self.format
        app += self.__writeLogInit('create')
        app += self.__writeCreateQuery()
        app += '\tfwrite($logfile, "\\n\\nQUERY: ". $query."\\n\\n");' + self.format
        app += '\n\t$query_result = $this->conn->query($query);' + self.format
        app += '\n\t$response = [];' + self.format
        app += '\t$response[\'query\'] = str_replace(["\'", \'"\'],"",$query);' + self.format
        app += '\n\tif(!$query_result){'+ self.format
        app += '\t\t$response["status_code"] = 503;' + self.format
        app += '\t\t$response["status_text"] = "K0";' + self.format
        app += '\t\t$response["message"] = json_encode($this->conn->error);' + self.format
        app += '\t} else {' + self.format
        app += '\t\t$response["status_code"] = 200;' + self.format
        app += '\t\t$response["status_text"] = "0K";' + self.format
        app += '\t\t$response["message"] = "' + self.table + ' created ";' + self.format
        app += '\t\t$result["id"] = $this->conn->insert_id;' + self.format
        app += '\t}' + self.format
        app += '\n\t$this->conn->close();' + self.format
        app += self.__writeLogEnd('create')
        app += '\n\treturn json_encode($response);' + self.format
        app += '}\n'
        return app

    def __update(self):
        app = 'function update(){' + self.format
        app += self.__writeLogInit('update')
        app += self.__writeUpdateQuery()
        app += '\tfwrite($logfile, "\\n\\nQUERY: ". $query."\\n\\n");' + self.format
        app += '\n\t$query_result = $this->conn->query($query);' + self.format
        app += '\n\t$response = [];' + self.format
        app += '\t$response[\'query\'] = str_replace(["\'", \'"\'],"",$query);' + self.format
        app += '\n\tif(!$query_result){'+ self.format
        app += '\t\t$response["status_code"] = 503;' + self.format
        app += '\t\t$response["status_text"] = "K0";' + self.format
        app += '\t\t$response["message"] = json_encode($this->conn->error);' + self.format
        app += '\t} else {' + self.format
        app += '\t\t$response["status_code"] = 200;' + self.format
        app += '\t\t$response["status_text"] = "0K";' + self.format
        app += '\t\t$response["message"] = "' + self.table + ' updated ";' + self.format
        app += '\t}' + self.format
        app += '\n\t$this->conn->close();' + self.format
        app += self.__writeLogEnd('update')
        app += '\n\treturn json_encode($response);' + self.format
        app += '}\n'
        return app

    # ------------------------------------------------------------------------------------------------------------------

    def __endClass(self):
        return '} //close Class ' + self.table.title() + '_Model'

    #===================================================================================================================
    # UTILITY
    #===================================================================================================================

    # query ------------------------------------------------------------------------------------------------------------

    def __writeFetchReadQuery(self):
        arr = ''
        for element in self.columns:
            arr += '\t\t\t\t\t"' + element[0] + '" => $row["' + element[0] + '"],' + self.format
        return arr

    def __writeCreateQuery(self):
        query = "\n\t$query = "
        query += "'INSERT INTO' . $this->table_name .\n"
        query += "\t\t\t'("

        for idx, element in enumerate(self.columns):
            #salto il 1 che è l'id
            if idx > 0:
                query += element[0]
                #fino al penultimo separo gli elementi con la ','
                if idx < len(self.columns)-1:
                    query += ', '

        query += ")' .\n\t\t\t' VALUES ' . \n \t\t\t'("

        for idx, element in enumerate(self.columns):
            #salto il 1 che è l'id
            if idx > 0:
                query += '\"\' . ' + '$this->' + element[0] + ' . \'\"'
                #fino al penultimo separo gli elementi con la ','
                if idx < len(self.columns)-1:
                    query += ', '

        query += ")';\n\n"
        return query


    def __writeUpdateQuery(self):
        query = "\n\t$query = "
        query += "'UPDATE ' . $this->table_name . ' SET' . "

        for idx, element in enumerate(self.columns):
            #salto il 1 che è l'id
            if idx > 0:
                query += "\n\t\t\t' " + element[0] + " = \" ' . $this->" + element[0] + " . '\",\' . "

        query += "\n\t\t\t' WHERE id = ' . $this->id;\n\n"

        return query

    # log --------------------------------------------------------------------------------------------------------------

    def __writeLogInit(self,type):
        log = '\n\terror_log("'+type+'");' + self.format
        log += '\t$logfile = fopen("../log/' + self.table + '_'+type+'.txt", "w") or die("Unable to open file!");' + self.format
        log += '\tfwrite($logfile, "'+type+' LOG: ". date("d/m/yy h:i:s a") .' + self.__printLogSeparator('=', 50) + ' );' + self.format
        return log

    def __writeLogEnd(self,type):
        log = '\n\terror_log("'+type+' response => ". json_encode($response));' + self.format
        log += '\tfwrite($logfile, "response: ". json_encode($response)."\\n\\n");' + self.format
        log += '\tfclose($logfile);' + self.format
        return log

    # separator --------------------------------------------------------------------------------------------------------

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