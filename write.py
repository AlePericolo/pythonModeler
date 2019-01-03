from conf import ReadConf
from connection import Connection
from writer import WriterClass, WriterModel

conf = ReadConf.ReadConf()
#print conf
conn = Connection.Connection(conf.database, 'ale_test')

if conn.connection is False:
    print 'SUKA'
else:
    print 'CONNESSO'
    if conf.output['formatted']:
        print '- output Formattato'
    print 'Sto scrivendo:'


    tables = conn.getAllTables()

    for (table,) in tables:

        if conf.output['class']:
            print '- class: ' + table
            try:
                with open('writtenClasses/' + table.title() + '.php', 'w') as outfile:

                    columns = conn.getColumnsByTable(table)
                    c = WriterClass.WriterClass(table, conf.output['formatted'])
                    outfile.write(c.writeFile())

            except IOError:
                print 'Errore Scrittura Classi'

        if conf.output['model']:
            print '- model: ' + table
            try:
                with open('writtenClasses/' + table.title() + 'Model.php', 'w') as outfile:

                    columns = conn.getColumnsByTable(table)
                    creatTableSyntax = conn.getCreateTableSyntax(table)
                    m = WriterModel.WriterModel(table, columns, creatTableSyntax, conf.output['formatted'])
                    outfile.write(m.writeFile())

            except IOError:
                print 'Errore Scrittura Model'

    print 'Finito!'