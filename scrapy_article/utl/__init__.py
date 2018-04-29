
if __name__ == '__main__':
    def tr(x):
        try:
            2 / x
        except Exception:
            print('error')
            return 'except return'
        else:
            print('correct')
            return 'else return'
        finally:
            print('finally')
            # return 'finally return'


    print(tr(2))