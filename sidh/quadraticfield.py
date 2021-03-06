from random import SystemRandom
from sidh.math import bitlength, hamming_weight, is_prime
from sidh.primefield import PrimeField
from functools import wraps

def tostring(a):
	if a.re == 0 and a.im == 0: return '0'
	if a.re == 0:
		if a.im == 1:
			return 'i'
		else:
			return f'{a.im}*i'
	elif a.im == 0:
		return f'{a.re}'
	else:
		if a.im == 1:
			return f'{a.re} + i'
		else:
			return f'{a.re} + {a.im}*i'

def check(func):
	@wraps(func)
	def method(self, other):
		if type(self) is not type(other):
			other = self.__class__(other)
		else:
			if self.field.p != other.field.p:
				raise ValueError
		return func(self, other)

	return method

def doc(s):
	class __doc(object):
		def __init__(self,f):
			self.func = f
			self.desc = s
		def __call__(self,*args,**kwargs):
			return self.func(*args,**kwargs)
		def __repr__(self):
			return self.desc
	return __doc

def QuadraticField(p : int):
	"""
	Quadratic Field class constructor

	...
	Parameters
	----------
		- prime number p congruent with 3 modulo 4
	Returns
	-------
		- Quadratic Field class of characteristic p
	"""

	if not is_prime(p):
		# To remove the use of progress.bar in is_prime() ... and maybe to renamed as IsPrime()
		raise TypeError(f'The integer {p} is not a prime number, and thus it does not allow to construct a quadratic field')
	if p % 4 == 1:
		raise TypeError(f'The prime number {p} is congruent with 1 modulo 4, which is not implemented yet!')

	basefield = PrimeField(p)
	NAME = 'Quadratic Field GF(p²) of characteristic p = 0x%X' % (p)
	@doc(NAME)
	class FiniteField():

		def __init__(self, x):
			self.basefield = basefield
			if isinstance(x, int):
				self.re = basefield(x)
				self.im = basefield(0)
			elif isinstance(x, list):
				self.re = basefield(x[0])
				self.im = basefield(x[1])
			else:
				self.re = x.re
				self.im = x.im
			self.field = FiniteField

		def __invert__(self): return self.inverse()
		@check
		def __add__(self, other): self.field.fp2add += 1; return FiniteField([self.re + other.re, self.im + other.im])
		@check
		def __radd__(self, other): return self + other
		@check
		def __sub__(self, other): self.field.fp2add += 1; return FiniteField([self.re - other.re, self.im - other.im])
		@check
		def __rsub__(self, other): return -self + other
		@check
		def __mul__(self, other):
			self.field.fp2mul += 1;
			# --- additions
			z0 = (self.re + self.im)
			z1 = (other.re + other.im)
			# --- multiplications
			t  = (z0 * z1)
			z2 = (self.re * other.re)
			z3 = (self.im * other.im)
			# --- additions
			c_re = (z2 - z3)
			c_im = (t - z2)
			c_im = (c_im - z3)
			return FiniteField([c_re, c_im])
		@check
		def __rmul__(self, other): return self * other
		@check
		def __truediv__(self, other): return self * ~other
		@check
		def __rtruediv__(self, other): return ~self * other
		@check
		def __floordiv__(self, other): return self * ~other
		@check
		def __rfloordiv__(self, other): return ~self * other
		@check
		def __div__(self, other): return self * ~other
		@check
		def __rdiv__(self, other): return ~self * other

		def __neg__(self): return FiniteField([-self.re, -self.im])

		@check
		def __eq__(self, other): return isinstance(other, self.__class__) and self.re == other.re and self.im == other.im

		def __abs__(self):
			"""
			Euclidean 2-norm of quadratic field element

			...
			Parameters
			----------
				- self an element of a Prime Field
			Returns
			-------
				- an integer x corresponding with the euclidean 2-norm, which is (self.re + self.im)*(self.re - self.im) = self.re² + self.im²
			-----
			Usage: self.abs()

			"""
			return (self.re**2 + self.im**2).x

		def __str__(self): return tostring(self)
		def __repr__(self): return tostring(self)
 
		#def __divmod__(self, divisor):
		#	q,r = divmod(self.x, divisor.x)
		#	return (FiniteField(q), FiniteField(r))

		def __pow__(self, e):
			"""
			Exponentiation

			...
			Parameters
			----------
				- self, which is an element of a Prime Field
				- an integer e
			Returns
			-------
				- self raised to e
			-----
			Usage:
				- self.pow(e)
				- self ** e
			Notes
			-----
				- This is a constant-time implementation by using the left-to-right method
				- It allows negative exponents, but any exponent is expected to belong to |[ 0 .. p - 1 ]|
			"""
			if e == 0:
				return FiniteField(1)

			elif e < 0:
				return self.inverse() ** (-e)

			elif e == 2:
				self.field.fp2sqr += 1
				# --- additions
				z0 = (self.re + self.re)
				z1 = (self.re + self.im)
				z2 = (self.re - self.im)
				# --- multiplications
				b_re = (z1 * z2)
				b_im = (z0 * self.im)
				return FiniteField([b_re, b_im])

			else:
				bits_of_e = bitlength(e)
				bits_of_e -= 1
				tmp_a = FiniteField(self)
				# left-to-right method for computing a^e
				for j in range(1, bits_of_e + 1):
					tmp_a = (tmp_a ** 2)
					if ((e >> (bits_of_e - j)) & 1) != 0:
						tmp_a = (tmp_a * self)

				return tmp_a

		def issquare(self):
			"""
			Checking if a given element is a quadratic residue

			...
			Parameters
			----------
				- self, which is an element of a Prime Field
			Returns
			-------
				- True if self is a quadratic residue; otherwise, False
			-----
			Usage:
				- self.issquare()
			Notes
			-----
				- This is a constant-time implementation by rasing to (p - 1) / 2
				- In other words, this function determines if the input has square-root in the Prime Field
			"""
			a1 = (self ** ((self.field.p - 3) // 4))
			alpha = (a1 ** 2)
			alpha = (alpha * self)
			# ---
			alpha_conjugated = FiniteField(alpha)
			alpha_conjugated.im = (-alpha_conjugated.im)
			# ---
			a0 = (alpha * alpha_conjugated)
			return not (a0.im == 0 and a0.re == -1)
 
		def inverse(self):
			"""
			Multiplicative inverse computation

			...
			Parameters
			----------
				- self, which is an element of a Prime Field
			Returns
			-------
				- the multiplivative inverse of self
			-----
			Usage:
				- self.inverse()
				- self ** -1
				- 1 / self, which performs an extra field multiplication
			Notes
			-----
				- This is a constant-time implementation by raising to (p - 2)
			"""
			# --- squarings
			N0 = (self.re ** 2)
			N1 = (self.im ** 2)
			# --- additions
			S1 = (N0 + N1)
			# --- inversions
			S1 = (S1 ** -1)
			# --- additions
			S2 = (-self.im)
			b_re = (S1 * self.re)
			b_im = (S1 * S2)
			return FiniteField([b_re, b_im])

		def sqrt(self):
			"""
			Square-root computation by using the Tonelli-Shanks algorithm

			...
			Parameters
			----------
				- self, which is an element of a Prime Field
			Returns
			-------
				- a square-root of self
			-----
			Usage:
				- self.sqrt()
			Notes
			-----
				- This is a non-constant-time implementation but it is only used on public data
			"""
			
			a1 = (self ** ((self.field.p - 3) // 4))
			alpha = (a1 ** 2)
			alpha = (alpha * self)

			alpha_conjugated = FiniteField(alpha)
			alpha_conjugated.im = (-alpha_conjugated.im)

			a0 = (alpha * alpha_conjugated)
			if a0.im == 0 and a0.re == -1:
				raise TypeError(f'The element {self} does not have square-root in the {FiniteField.__name__}')

			x0 = (a1 * self)
			if alpha.im == 0 and alpha.re == -1:
				return FiniteField([-x0.im, x0.re])

			else:
				alpha.re = (alpha.re + 1)
				b = (alpha ** ((self.field.p - 1) // 2))
				b = (b * x0)
				return b
 
	FiniteField.fp2add = 0  # Number of field additions performed
	FiniteField.fp2sqr = 0  # Number of field squarings performed
	FiniteField.fp2mul = 0  # Number of field multiplications performed
	FiniteField.p = p
	FiniteField.i = FiniteField([0,1])
	FiniteField.basefield = basefield
	FiniteField.__name__ = NAME

	return FiniteField