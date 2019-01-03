from datetime import datetime

class WriterClass:

    def __init__(self, table, format):
        self.table = table
        if format:
            self.format = '\n'
        else:
            self.format = ''
        self.file = '<?php\n'

    def writeFile(self):
        self.file += self.__developedBy() + '\n'
        self.file += '\n'
        self.file += self.__importModel() + '\n'
        self.file += self.__initClass() + '\n'
        self.file += self.__costructor() + '\n'
        self.file += self.__endClass()
        return self.file

    # ===================================================================================================================
    # PRIVATE FUNCTION
    # ===================================================================================================================

    def __developedBy(self):
        signature = '/**\n'
        signature += '* Developed by: Alessandro Pericolo\n'
        signature += '* Date: ' + datetime.now().strftime('%d/%m/%Y') + '\n'
        signature += '* Time: ' + datetime.now().strftime('%H:%M') + '\n'
        signature += '* Version: 0.1\n'
        signature += '**/'
        return signature

    # ------------------------------------------------------------------------------------------------------------------

    def __importModel(self):
        return "require_once '" + self.table.title() + "Model.php';\n"

    # ------------------------------------------------------------------------------------------------------------------

    def __initClass(self):
        return 'class ' + self.table.title() + ' extends ' + self.table.title() + 'Model {\n'

    # ------------------------------------------------------------------------------------------------------------------

    def __costructor(self):
        app = '/*CONSTRUCTOR*/\n'
        app += 'function __construct(PDO $pdo){' + self.format
        app += '\tparent::__construct($pdo);' + self.format
        app += '}\n'
        return app

    # ------------------------------------------------------------------------------------------------------------------

    def __endClass(self):
        return '} //close Class ' + self.table.title()