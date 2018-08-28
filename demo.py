
class Person(object):

    def __init__(self):

        self.password_hash = ""

    @property

    def password(self):

        print("get方法触发")


    @password.setter

    def password(self, value):

        # 加密
        print("setter方法触发：%s"%value)

if __name__ == '__main__':

    p = Person()

    p.password = "1234"

    print(p.password)

import functools

def login_user_data(a):

    @functools.wraps(a)
    def wrapper(*args,**kwargs):


        return a(*args,**kwargs)

    return wrapper

@login_user_data
def index():

    print("index")

@login_user_data
def hello():

    print("hello")

if __name__ == '__main__':

    print(index.__name__)

    print(hello.__name__)