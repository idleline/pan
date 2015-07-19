class opcmds(object):
    def __getitem__(self, **kwargs):
        xpath = ''
        for arg, value in kwargs.items():
            print arg, value
            xpath = xpath + '<' + str(arg) + '>'

        return xpath


