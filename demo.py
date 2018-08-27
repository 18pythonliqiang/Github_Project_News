
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