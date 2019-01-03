import os, json

class ReadConf:

    def __init__(self):
        #print 'ReadConf'
        with open(os.getcwd()+"/conf/conf.json") as conf:
            c = json.load(conf)
            self.database = c['connection']
            self.output = c['output']