import argparse


class Calculator:
    def __init__(self, num1, num2):
        self.num1 = num1
        self.num2 = num2

    def get_sum(self):
        return round(self.num1 + self.num2,3)

    def get_difference(self):
        return round(self.num1 - self.num2,3)

    def get_product(self):
        return round(self.num1 * self.num2,3)
    
    def get_quotient(self):
        return round(self.num1 / self.num2,3)


def main():
    parser = argparse.ArgumentParser(prog = "Calculator",
                                         description = "Calculates an operation on two floats")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--add', action='store_true', help="Add the two integers")
    group.add_argument('-s', '--subtract', action='store_true', help="Subtract the two integers")
    group.add_argument('-m', '--multiply', action='store_true', help="Multiply the two integers")
    group.add_argument('-d', '--divide', action='store_true', help="Divide the two integers")

    parser.add_argument('number1', type=float)
    parser.add_argument('number2', type=float)

    args = parser.parse_args()

    my_calc = Calculator(args.number1, args.number2)

    if args.add:
        print(my_calc.get_sum())
    elif args.subtract:
        print(my_calc.get_difference())
    elif args.multiply:
        print(my_calc.get_product())
    elif args.divide:
        if args.number2 == 0:
            print("Cannot divide by 0")
        else:
            print(my_calc.get_quotient())
    else:
        print("Invalid operation")

if __name__ == '__main__':
    main()