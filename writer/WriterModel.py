from datetime import datetime

class WriterModel:

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
        self.file += self.__importAbstract() + '\n'
        self.file += self.__initClass() + '\n'
        self.file += self.__attributes() + '\n'
        self.file += self.__printParagraph('CONSTRUCTOR', 102) + '\n'
        self.file += self.__costructor() + '\n'
        self.file += self.__printParagraph('FUNCTIONS', 104) + '\n'
        self.file += self.__pkFunctions() + '\n'
        self.file += self.__findAll() + '\n'
        self.file += self.__createKeyArray() + '\n'
        self.file += self.__createObjKeyArray() + '\n'
        self.file += self.__getEmptyKeyArray() + '\n'
        self.file += self.__getListColumns() + '\n'
        self.file += self.__printParagraph('CREATE TABLE', 101) + '\n'
        self.file += self.__createTable() + '\n'
        self.file += self.__printParagraph('GETTER & SETTER', 98) + '\n'
        self.file += self.__getterANDsetter() + '\n'
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

    def __importAbstract(self):
        return "require_once 'AbstractModel.php';\n"

    # ------------------------------------------------------------------------------------------------------------------

    def __initClass(self):
        return 'class ' + self.table.title() + 'Model extends AbstractModel {\n'

    # ------------------------------------------------------------------------------------------------------------------

    def __attributes(self):
        app = ''
        for element in self.columns:
            type = self.__getAttributeTypeByElement(element)
            #signature
            app += '/** @var ' + type
            if element[3] == 'PRI':
                app += ' PrimaryKey'
            app += ' */\n'
            #attribute
            app += 'protected $' + element[0]
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
        app += 'function __construct($pdo){' + self.format
        app += '\tparent::__construct($pdo);' + self.format
        app += '\t$this->tableName = "' + self.table +'";' + self.format
        app += '}\n'
        return app

    # ------------------------------------------------------------------------------------------------------------------

    def __pkFunctions(self):
        #recupero la PK
        pk = '$id'
        for element in self.columns:
            if element[3] == 'PRI':
                pk = '$' + element[0]
                continue
        #find byPK
        find = '/** \n* find by PrimaryKey: \n* @return ' + self.table.title() + '|array|string|null\n**/'
        app = find + '\n'
        app += 'public function findByPk(' + pk + ', $typeResult = self::FETCH_OBJ){' + self.format
        app += '\t$query = "SELECT * FROM $this->tableName USE INDEX(PRIMARY) WHERE ID=?";' + self.format
        app += '\treturn $this->createResult($query, array(' + pk + '), $typeResult);' + self.format
        app += '}\n'
        # delete byPK
        delete = '\n/** \n* delete by PrimaryKey: \n**/'
        app += delete + '\n'
        app += 'public function deleteByPk(' + pk + '){' + self.format
        app += '\t$query = "DELETE FROM $this->tableName WHERE ID=?";' + self.format
        app += '\treturn $this->createResultValue($query, array(' + pk + '));' + self.format
        app += '}\n'
        return app

    # ------------------------------------------------------------------------------------------------------------------

    def __findAll(self):
        findAll = '/** \n* find all record of table \n* @return ' + self.table.title() + '[]|array|string\n**/'
        app = findAll + '\n'
        app += 'public function findAll($distinct = false, $typeResult = self::FETCH_OBJ, $limit = -1, $offset = -1){' + self.format
        app += '\t$distinctStr = ($distinct) ? "DISTINCT" : "";' + self.format
        app += '\t$query = "SELECT $distinctStr * FROM $this->tableName ";' + self.format
        app += '\tif ($this->whereBase) $query .= " WHERE $this->whereBase";' + self.format
        app += '\tif ($this->orderBase) $query .= " ORDER BY $this->orderBase";' + self.format
        app += '\t$query .= $this->createLimitQuery($limit, $offset);' + self.format
        app += '\treturn $this->createResultArray($query, null, $typeResult);' + self.format
        app += '}\n'
        return app

    # ------------------------------------------------------------------------------------------------------------------

    def __createKeyArray(self):
        keyArray = '/** \n* trasform the Object into a KeyArray \n* @return array\n**/'
        app = keyArray + '\n'
        app += 'public function createKeyArray(){\n'
        app += '\t$keyArray = array();' + self.format
        for element in self.columns:
            app += '\tif (isset($this->' + element[0] + ')) $keyArray["' + element[0] + '"] = $this->' + element[0] + ';' + self.format
        app += '\treturn $keyArray;' + self.format
        app += '}\n'
        return app

    # ------------------------------------------------------------------------------------------------------------------

    def __createObjKeyArray(self):
        ObjKeyArray = '/** \n* trasform the KeyArray into a Object \n* @param array $keyArray\n**/'
        app = ObjKeyArray + '\n'
        app += 'public function createObjKeyArray(array $keyArray){\n'
        for element in self.columns:
            type = self.__getAttributeTypeByElement(element)
            if type == 'DateTime':
                app += '\tif (isset($keyArray["' + element[0] + '"]) && $keyArray["' + element[0] + '"] != "") $this->' + element[0] + ' = date("Ymd", strtotime($keyArray["' + element[0] + '"]));' + self.format
            else:
                app += '\tif (isset($keyArray["' + element[0] + '"])) $this->' + element[0] + ' = $keyArray["' + element[0] + '"];' + self.format
        app += '}\n'
        return app

    # ------------------------------------------------------------------------------------------------------------------

    def __getEmptyKeyArray(self):
        emptyKeyArray = '/** \n* return the Object as an empty KeyArray \n* @return array\n**/'
        app = emptyKeyArray + '\n'
        app += 'public function getEmptyKeyArray(){\n'
        app += '\t$emptyKeyArray = array();' + self.format
        for element in self.columns:
            app += '\t$emptyKeyArray["' + element[0] + '"] = "";' + self.format
        app += '\treturn $emptyKeyArray;' + self.format
        app += '}\n'
        return app

    def __endClass(self):
        return '} //close Class ' + self.table.title() + 'Model'

    # ------------------------------------------------------------------------------------------------------------------

    def __getListColumns(self):
        listColumns = '/** \n* return columns\' list as string \n* @return string\n**/'
        app = listColumns + '\n'
        app += 'public function getListColumns(){\n'
        app += '\treturn "'
        for element in self.columns:
            if element == self.columns[-1]:
                app += element[0]
            else:
                app += element[0] + ', '
        app += '";\n}\n'
        return app

    # ------------------------------------------------------------------------------------------------------------------

    def __createTable(self):
        createTable = '/** \n* DDL create table query \n**/'
        app = createTable + '\n'
        app += 'public function createTable(){\n'
        app += 'return $this->pdo->exec(\n"' + self.creatTableSyntax + '"'
        app += '\n);\n}\n'
        return app

    # ------------------------------------------------------------------------------------------------------------------

    def __getterANDsetter(self):
        getterAndSetter = ''
        for element in self.columns:
            type = self.__getAttributeTypeByElement(element)
            #getter
            getter = ''
            app = '/** \n* @return ' + type + '\n**/\n'
            app += 'public function get' + element[0].title().replace("_", "") + '(){\n'
            app += '\t return $this->' + element[0] + ';\n'
            app += '}\n\n'
            getter += app
            getterAndSetter += getter
            #setter
            setter = ''
            if type == 'string':
                app = '/** \n* @param ' + type + ' $' + element[0] + '\n* @param int $encodeType\n **/\n'
                app += 'public function set' + element[0].title().replace("_", "") + '($' + element[0] + ', $encodeType = self::STR_DEFAULT){\n'
                app += '\t $this->' + element[0] + ' = $this->decodeString($' + element[0] + ', $encodeType);\n'
                app += '}\n\n'
                setter += app
            else:
                app = '/** \n* @param ' + type + ' $' + element[0] + '\n**/\n'
                app += 'public function set' + element[0].title().replace("_", "") + '($' + element[0] + '){\n'
                app += '\t $this->' + element[0] + ' = $' + element[0] + ';\n'
                app += '}\n\n'
                setter += app
            getterAndSetter += setter
        return getterAndSetter

    #===================================================================================================================
    # UTILITY
    #===================================================================================================================

    def __printParagraph(self, title, length = 100):
        p = '/* ' + title + ' '
        for x in range(length):
            p += '-'
        p += ' */\n'
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