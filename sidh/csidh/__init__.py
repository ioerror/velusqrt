from struct import pack, unpack

from sidh.csidh.gae_df import Gae_df
from sidh.csidh.gae_wd1 import Gae_wd1
from sidh.csidh.gae_wd2 import Gae_wd2
from sidh.csidh.hvelu import Hvelu
from sidh.csidh.tvelu import Tvelu
from sidh.csidh.svelu import Svelu
from sidh.csidh.montgomery import MontgomeryCurve
from sidh.constants import parameters
from sidh.common import attrdict

default_parameters = dict(
    curvemodel='montgomery',
    prime='p512',
    formula='hvelu',
    style='df',
    exponent=10,
    tuned=False,
    multievaluation=False,
    verbose=False,
)


class CSIDH(object):
    """

    CSIDH

    Here is one group action test with random keys:

    >>> csidh_tvelu_wd1 = CSIDH('montgomery', 'p512', 'tvelu', 'wd1', 2, False, False, False)
    >>> sk_a, sk_b = csidh_tvelu_wd1.secret_key(), csidh_tvelu_wd1.secret_key()
    >>> pk_a, pk_b = csidh_tvelu_wd1.public_key(sk_a), csidh_tvelu_wd1.public_key(sk_b)
    >>> csidh_tvelu_wd1.dh(sk_a, pk_b) == csidh_tvelu_wd1.dh(sk_b, pk_a)
    True

    >>> from sidh.csidh import CSIDH, default_parameters
    >>> c = CSIDH(**default_parameters)
    >>> # alice generates a key
    >>> alice_secret_key = c.secret_key()
    >>> alice_public_key = c.public_key(alice_secret_key)
    >>> # bob generates a key
    >>> bob_secret_key = c.secret_key()
    >>> bob_public_key = c.public_key(bob_secret_key)
    >>> # if either alice or bob use their secret key with the other's respective
    >>> # public key, the resulting shared secrets are the same
    >>> shared_secret_alice = c.dh(alice_secret_key, bob_public_key)
    >>> shared_secret_bob = c.dh(bob_secret_key, alice_public_key)
    >>> # Alice and bob produce an identical shared secret
    >>> shared_secret_alice == shared_secret_bob
    True

    Other tests which were previously here are now in the test directory.

    """

    def __init__(
        self,
        curvemodel,
        prime,
        formula,
        style,
        tuned,
        exponent,
        multievaluation,
        verbose,
    ):
        self.curvemodel = curvemodel
        self.prime = prime
        self.style = style
        self._exponent = exponent
        self.tuned = tuned
        self.multievaluation = multievaluation
        self.fp = None
        self.params = attrdict(parameters['csidh'][prime])
        self.params.update(self.params[style])

        if self.curvemodel == 'montgomery':
            self.curve = MontgomeryCurve(prime, style)
            self.fp = self.curve.fp
        else:
            self.curve = None
            raise NotImplemented

        if formula == 'hvelu':
            self.formula = Hvelu(self.curve, self.tuned, self.multievaluation)
        elif formula == 'tvelu':
            self.formula = Tvelu(self.curve)
        elif formula == 'svelu':
            self.formula = Svelu(self.curve, self.tuned, self.multievaluation)

        if self.style == 'df':
            self.gae = Gae_df(prime, self.tuned, self.curve, self.formula)
        elif self.style == 'wd1':
            self.gae = Gae_wd1(prime, self.tuned, self.curve, self.formula)
        elif self.style == 'wd2':
            self.gae = Gae_wd2(prime, self.tuned, self.curve, self.formula)
        else:
            self.gae = NotImplemented

    def dh(self, sk, pk):
        sk = unpack('<{}b'.format(len(sk)), sk)
        pk = int.from_bytes(pk, 'little')
        pk = self.curve.affine_to_projective(pk)
        ss = self.curve.coeff(self.gae.dh(sk, pk)).to_bytes(
            length=(self.params.p_bits // 8), byteorder='little'
        )
        return ss

    def secret_key(self):
        k = self.gae.random_key()
        return pack('<{}b'.format(len(k)), *k)

    def public_key(self, sk):
        sk = unpack('<{}b'.format(len(sk)), sk)
        xy = self.gae.pubkey(sk)
        x = self.curve.coeff(xy)
        # this implies a y of 4 on the receiver side
        return x.to_bytes(length=(self.params.p_bits // 8), byteorder='little')


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
