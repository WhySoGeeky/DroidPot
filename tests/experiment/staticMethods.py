__author__ = 'droid'

class caller(object):
    global output
    def __init__(self):
        self.result = 0

        global output


    @staticmethod
    def calc(x, y):
        result = x + y
        global output
        output = result

        return output


if __name__ == '__main__':

    print caller.calc(1,2)
    print caller().output

    new = caller()
    new.output = 4
    print new.output
