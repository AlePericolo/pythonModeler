from conf import ReadConf
from connection import Connection
from writer import WriterClass, WriterModel, WriterAPI

conf = ReadConf.ReadConf()
#print conf
conn = Connection.Connection(conf.database, 'test')

if conn.connection is False:
    print ('SUKA')
else:
    print ('CONNESSO')
    if conf.output['formatted']:
        print ('- output Formattato')
    print ('Sto scrivendo:')


    tables = conn.getAllTables()

    for (table,) in tables:

        dirOutput = 'writtenFiles/'

        if conf.output['class']:
            print ('- class: ' + table)

            if conf.output['separaClassModel']:
                dirOutput = 'writtenFiles/class/'

            try:
                with open(dirOutput + table.title() + '.php', 'w') as outfile:

                    columns = conn.getColumnsByTable(table)
                    c = WriterClass.WriterClass(table, conf.output['formatted'])
                    outfile.write(c.writeFile())

            except IOError:
                print ('Errore Scrittura Classi')

        if conf.output['model']:
            print ('- model: ' + table)

            if conf.output['separaClassModel']:
                dirOutput = 'writtenFiles/model/'

            try:
                with open(dirOutput + table.title() + 'Model.php', 'w') as outfile:

                    columns = conn.getColumnsByTable(table)
                    creatTableSyntax = conn.getCreateTableSyntax(table)
                    m = WriterModel.WriterModel(table, columns, creatTableSyntax, conf.output['formatted'])
                    outfile.write(m.writeFile())

            except IOError:
                print ('Errore Scrittura Model')

        if conf.output['apiclass']:
            print ('- apiclass: ' + table)

            if conf.output['separaClassModel']:
                dirOutput = 'writtenFiles/apiclass/'

            try:
                with open(dirOutput + table.title() + '.php', 'w') as outfile:

                    columns = conn.getColumnsByTable(table)
                    creatTableSyntax = conn.getCreateTableSyntax(table)
                    a = WriterAPI.WriterAPI(table, columns, creatTableSyntax, conf.output['formatted'])
                    outfile.write(a.writeFile())

            except IOError:
                print ('Errore Scrittura APIClassi')

    print ('Finito!')