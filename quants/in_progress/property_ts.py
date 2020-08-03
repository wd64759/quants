class A(object):
    def __init__(self):
        self.__age = 1
    
    @property
    def me(self):
        return self.__age

    @me.setter
    def me(self, v):
        self.__age = v

if __name__ == '__main__':
    a = A()
    print(a.me)
    a.me =10
    print(a.me)