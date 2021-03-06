from functools import reduce
from .constants import sop_data, parameters
from .math import bitlength


class F_p(object):
    def __init__(self, p):
        # counters for field operations performed
        self.fpadd = 0
        self.fpsqr = 0
        self.fpmul = 0
        self.p = p

    def set_zero_ops(self):

        self.fpadd -= self.fpadd
        self.fpsqr -= self.fpsqr
        self.fpmul -= self.fpmul

    def show_ops(self, label, a, b, flag):

        print(
            "| %s: %7dM + %7dS + %7da"
            % (label, self.fpmul, self.fpsqr, self.fpadd),
            end="\t",
        )

        return None

    def get_ops(self):
        return [self.fpmul, self.fpsqr, self.fpadd]

    # Modular inverse
    def fp_inv(self, a):
        g, x, y = xgcd(a, self.p)
        # if g != 1:
        # 	raise ValueError
        return x % self.p

    # Modular addition
    def fp_add(self, a, b):
        self.fpadd += 1
        return (a + b) % self.p

    # Modular substraction
    def fp_sub(self, a, b):
        self.fpadd += 1
        return (a - b) % self.p

    # Modular multiplication
    def fp_mul(self, a, b):
        self.fpmul += 1
        return (a * b) % self.p

    # Modular squaring
    def fp_sqr(self, a):
        self.fpsqr += 1
        # print(fpsqr)
        return (a ** 2) % self.p

    # constant-time swap
    def fp_cswap(self, x, y, b):

        z = list([x, y])
        z = list(z[:: (1 - 2 * b)])
        return z[0], z[1]

    # Modular exponentiation
    def fp_exp(self, a, e):

        bits_of_e = bitlength(e)
        bits_of_e -= 1
        tmp_a = a
        # left-to-right method for computing a^e
        for j in range(1, bits_of_e + 1):

            tmp_a = self.fp_sqr(tmp_a)
            if ((e >> (bits_of_e - j)) & 1) != 0:
                tmp_a = self.fp_mul(tmp_a, a)

        return tmp_a


# Jacobi symbol used for checking if an integer has square-root in fp
def jacobi(a, n):

    assert n > a > 0 and n % 2 == 1
    t = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            r = n % 8
            if r == 3 or r == 5:
                t = -t
        a, n = n, a
        if a % 4 == n % 4 == 3:
            t = -t
        a %= n
    if n == 1:
        return t
    else:
        return 0


# Extended GCD
def xgcd(aa, bb):
    lastremainder, remainder = abs(aa), abs(bb)
    x, lastx, y, lasty = 0, 1, 1, 0
    while remainder:
        lastremainder, (quotient, remainder) = (
            remainder,
            divmod(lastremainder, remainder),
        )
        x, lastx = lastx - quotient * x, x
        y, lasty = lasty - quotient * y, y

    return (
        lastremainder,
        lastx * (-1 if aa < 0 else 1),
        lasty * (-1 if bb < 0 else 1),
    )


# --------------------------------------------------------------------------------------------------------------------------------
'''
    chunks()
    inputs: a string, a list, and the maximum  number of elements in each chunk
    -----
    NOTE: This function divide the input list into len(L) / k chunks.
'''
chunks = (
    lambda NAME, L, n: [NAME + ' =\t{']
    + [
        '\t' + ','.join(list(map(format, L[i * n : (i + 1) * n], ['3d'] * n)))
        for i in range((len(L) + n - 1) // n)
    ]
    + ['\t};']
)
'''
    printl()
    inputs: a string, a list, and the maximum number k of elements in each chunk
    -----
    NOTE: this function prints a given list by chunks of size k.
'''


def printl(NAME, L, k):

    to_print = chunks(NAME, L, k)
    print(to_print[0])
    for i in range(1, len(to_print) - 2):
        print(to_print[i] + ",")

    print(to_print[len(to_print) - 2])
    print(to_print[len(to_print) - 1])
