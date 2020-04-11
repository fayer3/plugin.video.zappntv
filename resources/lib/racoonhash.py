# usage create -> update() -> hex()
try:
    class Long64(long):
        def __init__(self, num=long(0)): # initialising
            self.num = self.cap(num)
        def __str__(self):
            return str(self.num)
        def __repr__(self):
            return "Long6464(" + self.__str__() + ")"

        def __lt__(self, other):
            return self.num < self.val(other)
        def __le__(self, other):
            return self.num <= self.val(other)
        def __eq__(self, other):
            return self.num == self.val(other)
        def __ne__(self, other):
            return self.num != self.val(other)
        def __gt__(self, other):
            return self.num > self.val(other)
        def __ge__(self, other):
            return self.num >= self.val(other)

        def __add__(self, other):
            return Long64(self.cap(self.num + self.val(other)))
        def __sub__(self, other):
            return Long64(self.cap(self.num - self.val(other)))
        def __mul__(self, other):
            return Long64(self.cap(self.num * self.val(other)))
        def __floordiv__(self, other):
            return Long64(self.cap(self.num // self.val(other)))
        def __mod__(self, other):
            return Long64(self.cap(self.num % self.val(other)))
        def __divmod__(self, other):
            return NotImplemented
        def __pow__(self, other):
            return Long64(self.cap(self.num ** self.val(other)))
        def __lshift__(self, other):
            return Long64(self.cap(self.num << self.val(other)))
        def __rshift__(self, other):
            if self.num < 0:
                return Long64(self.cap(((self.num & 9223372036854775807)+9223372036854775808) >> self.val(other)))
            else:
                return Long64(self.cap(self.num >> self.val(other)))
        def __and__(self, other):
            return Long64(self.cap(self.num & self.val(other)))
        def __xor__(self, other):
            return Long64(self.cap(self.num ^ self.val(other)))
        def __or__(self, other):
            return Long64(self.cap(self.num | self.val(other)))
        @staticmethod
        def cap(num): # a method that handles an overflow/underflow
            if num > 9223372036854775807 or num < -9223372036854775808:
                if (num & 9223372036854775808) == 9223372036854775808:
                    #negative
                    leftover = num & 9223372036854775807
                    return -9223372036854775808 + leftover#~(9223372036854775808)
                else:
                    #positv
                    return num & 9223372036854775807
            return num
        @staticmethod
        def val(other):
            if isinstance(other, Long64) or isinstance(other, Int32):
                return other.num
            return other

    class Int32(long):
        def __init__(self, num=long(0)): # initialising
            self.num = self.cap(num)
        def __str__(self):
            return str(self.num)
        def __repr__(self):
            return "Int32(" + self.__str__() + ")"

        def __lt__(self, other):
            return self.num < self.val(other)
        def __le__(self, other):
            return self.num <= self.val(other)
        def __eq__(self, other):
            return self.num == self.val(other)
        def __ne__(self, other):
            return self.num != self.val(other)
        def __gt__(self, other):
            return self.num > self.val(other)
        def __ge__(self, other):
            return self.num >= self.val(other)

        def __add__(self, other):
            return Int32(self.cap(self.num + self.val(other)))
        def __sub__(self, other):
            return Int32(self.cap(self.num - self.val(other)))
        def __mul__(self, other):
            return Int32(self.cap(self.num * self.val(other)))
        def __floordiv__(self, other):
            return Int32(self.cap(self.num // self.val(other)))
        def __mod__(self, other):
            return Int32(self.cap(self.num % self.val(other)))
        def __divmod__(self, other):
            return NotImplemented
        def __pow__(self, other):
            return Int32(self.cap(self.num ** self.val(other)))
        def __lshift__(self, other):
            return Int32(self.cap(self.num << self.val(other)))
        def __rshift__(self, other):
            if self.num < 0:
                return Int32(self.cap(((self.num & 2147483647)+2147483648) >> self.val(other)))
            else:
                return Int32(self.cap(self.num >> self.val(other)))
        def __and__(self, other):
            return Int32(self.cap(self.num & self.val(other)))
        def __xor__(self, other):
            return Int32(self.cap(self.num ^ self.val(other)))
        def __or__(self, other):
            return Int32(self.cap(self.num | self.val(other)))
        @staticmethod
        def cap(num): # a method that handles an overflow/underflow
            if num > 2147483647 or num < -2147483648:
                if (num & 2147483648) == 2147483648:
                    #negative
                    leftover = num & 2147483647
                    return -2147483648 + leftover#~(2147483648)
                else:
                    #positv
                    return num & 2147483647
            return num
        @staticmethod
        def val(other):
            if isinstance(other, Long64) or isinstance(other, Int32):
                return other.num
            return other
except NameError:
    class Long64(int):
        def __init__(self, num=int(0)): # initialising
            self.num = self.cap(num)
        def __str__(self):
            return str(self.num)
        def __repr__(self):
            return "Long64(" + self.__str__() + ")"

        def __lt__(self, other):
            return self.num < self.val(other)
        def __le__(self, other):
            return self.num <= self.val(other)
        def __eq__(self, other):
            return self.num == self.val(other)
        def __ne__(self, other):
            return self.num != self.val(other)
        def __gt__(self, other):
            return self.num > self.val(other)
        def __ge__(self, other):
            return self.num >= self.val(other)

        def __add__(self, other):
            return Long64(self.cap(self.num + self.val(other)))
        def __sub__(self, other):
            return Long64(self.cap(self.num - self.val(other)))
        def __mul__(self, other):
            return Long64(self.cap(self.num * self.val(other)))
        def __floordiv__(self, other):
            return Long64(self.cap(self.num // self.val(other)))
        def __mod__(self, other):
            return Long64(self.cap(self.num % self.val(other)))
        def __divmod__(self, other):
            return NotImplemented
        def __pow__(self, other):
            return Long64(self.cap(self.num ** self.val(other)))
        def __lshift__(self, other):
            return Long64(self.cap(self.num << self.val(other)))
        def __rshift__(self, other):
            if self.num < 0:
                return Long64(self.cap(((self.num & 9223372036854775807)+9223372036854775808) >> self.val(other)))
            else:
                return Long64(self.cap(self.num >> self.val(other)))
        def __and__(self, other):
            return Long64(self.cap(self.num & self.val(other)))
        def __xor__(self, other):
            return Long64(self.cap(self.num ^ self.val(other)))
        def __or__(self, other):
            return Long64(self.cap(self.num | self.val(other)))
        @staticmethod
        def cap(num): # a method that handles an overflow/underflow
            if num > 9223372036854775807 or num < -9223372036854775808:
                if (num & 9223372036854775808) == 9223372036854775808:
                    #negative
                    leftover = num & 9223372036854775807
                    return -9223372036854775808 + leftover#~(9223372036854775808)
                else:
                    #positv
                    return num & 9223372036854775807
            return num
        @staticmethod
        def val(other):
            if isinstance(other, Long64) or isinstance(other, Int32):
                return other.num
            return other

    class Int32(int):
        def __init__(self, num=int(0)): # initialising
            self.num = self.cap(num)
        def __str__(self):
            return str(self.num)
        def __repr__(self):
            return "Int32(" + self.__str__() + ")"

        def __lt__(self, other):
            return self.num < self.val(other)
        def __le__(self, other):
            return self.num <= self.val(other)
        def __eq__(self, other):
            return self.num == self.val(other)
        def __ne__(self, other):
            return self.num != self.val(other)
        def __gt__(self, other):
            return self.num > self.val(other)
        def __ge__(self, other):
            return self.num >= self.val(other)

        def __add__(self, other):
            return Int32(self.cap(self.num + self.val(other)))
        def __sub__(self, other):
            return Int32(self.cap(self.num - self.val(other)))
        def __mul__(self, other):
            return Int32(self.cap(self.num * self.val(other)))
        def __floordiv__(self, other):
            return Int32(self.cap(self.num // self.val(other)))
        def __mod__(self, other):
            return Int32(self.cap(self.num % self.val(other)))
        def __divmod__(self, other):
            return NotImplemented
        def __pow__(self, other):
            return Int32(self.cap(self.num ** self.val(other)))
        def __lshift__(self, other):
            return Int32(self.cap(self.num << self.val(other)))
        def __rshift__(self, other):
            if self.num < 0:
                return Int32(self.cap(((self.num & 2147483647)+2147483648) >> self.val(other)))
            else:
                return Int32(self.cap(self.num >> self.val(other)))
        def __and__(self, other):
            return Int32(self.cap(self.num & self.val(other)))
        def __xor__(self, other):
            return Int32(self.cap(self.num ^ self.val(other)))
        def __or__(self, other):
            return Int32(self.cap(self.num | self.val(other)))
        @staticmethod
        def cap(num): # a method that handles an overflow/underflow
            if num > 2147483647 or num < -2147483648:
                if (num & 2147483648) == 2147483648:
                    #negative
                    leftover = num & 2147483647
                    return -2147483648 + leftover#~(2147483648)
                else:
                    #positv
                    return num & 2147483647
            return num
        @staticmethod
        def val(other):
            if isinstance(other, Long64) or isinstance(other, Int32):
                return other.num
            return other


class RacoonHash:

    h0 = Long64(0)
    h1 = Long64(0)
    h2 = Long64(0)
    h3 = Long64(0)
    h4 = Long64(0)

    finalized = False

    block = Long64(0)
    blocks = []
    _0x90a0de = [Long64(-2147483648), Long64(8388608), Long64(32768), Long64(128)]
    _0x4b6ca9 = [Int32(24), Int32(16), Int32(8), Int32(0)]
    _0x29b497 = ["0" ,"1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
    lastByteIndex = Int32(0)
    hBytes = Long64(0)
    bytes = Long64(0)
    start = Int32(0)

    hashed = False

    def __init__(self): # _0x4ba53c
        self.reset()

    def update(self, x): # x = String
        if not self.finalized:
            e = Int32(0)
            t = Int32(0)
            cur = Int32(0)
            r = Int32(len(x))
            n = self.blocks

            while (cur < r):
                if self.hashed:
                    self.hashed = False
                    n[0] = self.block
                    n[16] = n[1] = n[2] = n[3] = n[4] = n[5] = n[6] = n[7] = n[8] = n[9] = n[10] = n[11] = n[12] = n[13] = n[14] = n[15] = Long64(0)
                    t = self.start
                    while (cur < r and t < 64):
                        #todo
                        n[t >> 2] |= ord(x[cur]) << self._0x4b6ca9[3 & t]
                        t += 1
                        cur += 1
                else:
                    t = self.start
                    while (cur < r and t < 64):
                        e = ord(x[cur])
                        if (e < 128):
                            #todo
                            n[t >> 2] |= e << self._0x4b6ca9[3 & t]
                            t += 1
                        else:
                            if (e < 2048):
                                #todo
                                n[t >> 2] |= (192 | e >> 6) << self._0x4b6ca9[3 & t]
                                t += 1
                            else:
                                if (e < 55296 or 57344 <= e):
                                    #todo
                                    n[t >> 2] |= (224 | e >> 12) << self._0x4b6ca9[3 & t]
                                    t += 1
                                else:
                                    cur += 1
                                    e = 65536 + ((1023 & e) << 10 | 1023 & ord(x[cur]))
                                    #todo
                                    n[t >> 2] |= (240 | e >> 18) << self._0x4b6ca9[3 & t]
                                    t += 1
                                    #todo
                                    n[t >> 2] |= (128 | e >> 12 & 63) << self._0x4b6ca9[3 & t]
                                    t += 1
                                #todo
                                n[t >> 2] |= (128 | e >> 6 & 63) << self._0x4b6ca9[3 & t]
                                t += 1
                            #todo
                            n[t >> 2] |= (128 | 63 & e) << self._0x4b6ca9[3 & t]
                            t += 1
                        cur += 1
                
                self.lastByteIndex = t
                self.bytes += t - self.start
                if (64 <= t):
                    self.block = n[16]
                    self.start = t - 64
                    self.hash()
                    self.hashed = True
                else:
                    self.start = t
            if (Long64(4294967295) < self.bytes):
                self.hBytes += self.bytes / Long64(4294967296)
                self.bytes = self.bytes % Long64(4294967296)

    def finalizeHash(self): #0x8f
        if not self.finalized:
            self.finalized = True;
            x = self.blocks
            a = self.lastByteIndex
            x[16] = self.block
            x[a >> 2] |= self._0x90a0de[3 & a]
            self.block = x[16]
            if (56 <= a and (self.hashed or self.hash())):
                    x[0] = self.block
                    x[16] = x[1] = x[2] = x[3] = x[4] = x[5] = x[6] = x[7] = x[8] = x[9] = x[10] = x[11] = x[12] = x[13] = x[14] = x[15] = 0
            x[14] = self.hBytes << 3 | self.bytes >> 29;
            x[15] = self.bytes << 3;
            self.hash()

    def hash(self): # returns boolean // 0x8e
        temp = Long64(0) # a
        var0 = Int32(self.h0) # e
        var1 = Int32(self.h1) # t
        var2 = Int32(self.h2) # _
        var3 = Int32(self.h3) # r
        var4 = Int32(self.h4) # n
        i = []
        for index in range(0, len(self.blocks)):
            i.append(Int32(self.blocks[index]))

        for x in range(16, 80):
            temp = Long64(i[x - 3] ^ i[x - 8] ^ i[x - 14] ^ i[x - 16])
            i.insert(x, (Int32(temp) << 1 | Int32(temp) >> 31))
        
        for x in range(0, 20, 5):
            var4 = (var0 << 5 | var0 >> 27) + (var1 & var2 | ~var1 & var3) + var4 + Int32(1518500249) + i[x]
            var1 = var1 << 30 | var1 >> 2
            var3 = ((var4) << 5 | var4 >> 27) + (var0 & (var1) | ~var0 & var2) + var3 + Int32(1518500249) + i[x + 1]
            var0 = var0 << 30 | var0 >> 2
            var2 = ((var3) << 5 | var3 >> 27) + (var4 & (var0) | ~var4 & var1) + var2 + Int32(1518500249) + i[x + 2]
            var4 = var4 << 30 | var4 >> 2
            var1 = ((var2) << 5 | var2 >> 27) + (var3 & (var4) | ~var3 & var0) + var1 + Int32(1518500249) + i[x + 3]
            var3 = var3 << 30 | var3 >> 2
            var0 = ((var1) << 5 | var1 >> 27) + (var2 & (var3) | ~var2 & var4) + var0 + Int32(1518500249) + i[x + 4]
            var2 = var2 << 30 | var2 >> 2
        
        for x in range(20, 40, 5):
            var4 = (var0 << 5 | var0 >> 27) + (var1 ^ var2 ^ var3) + var4 + Int32(1859775393) + i[x]
            var1 = var1 << 30 | var1 >> 2
            var3 = ((var4) << 5 | var4 >> 27) + (var0 ^ (var1) ^ var2) + var3 + Int32(1859775393) + i[x + 1]
            var0 = var0 << 30 | var0 >> 2
            var2 = ((var3) << 5 | var3 >> 27) + (var4 ^ (var0) ^ var1) + var2 + Int32(1859775393) + i[x + 2]
            var4 = var4 << 30 | var4 >> 2
            var1 = ((var2) << 5 | var2 >> 27) + (var3 ^ (var4) ^ var0) + var1 + Int32(1859775393) + i[x + 3]
            var3 = var3 << 30 | var3 >> 2
            var0 = ((var1) << 5 | var1 >> 27) + (var2 ^ (var3) ^ var4) + var0 + Int32(1859775393) + i[x + 4]
            var2 = var2 << 30 | var2 >> 2
        
        for x in range(40, 60, 5):
            var4 = (var0 << 5 | var0 >> 27) + (var1 & var2 | var1 & var3 | var2 & var3) + var4 - Int32(1894007588) + i[x]
            var1 = var1 << 30 | var1 >> 2
            var3 = ((var4) << 5 | var4 >> 27) + (var0 & (var1) | var0 & var2 | var1 & var2) + var3 - Int32(1894007588) + i[x + 1]
            var0 = var0 << 30 | var0 >> 2
            var2 = ((var3) << 5 | var3 >> 27) + (var4 & (var0) | var4 & var1 | var0 & var1) + var2 - Int32(1894007588) + i[x + 2]
            var4 = var4 << 30 | var4 >> 2
            var1 = ((var2) << 5 | var2 >> 27) + (var3 & (var4) | var3 & var0 | var4 & var0) + var1 - Int32(1894007588) + i[x + 3]
            var3 = var3 << 30 | var3 >> 2
            var0 = ((var1) << 5 | var1 >> 27) + (var2 & (var3) | var2 & var4 | var3 & var4) + var0 - Int32(1894007588) + i[x + 4]
            var2 = var2 << 30 | var2 >> 2
        
        for x in range(60, 80, 5):
            var4 = (var0 << 5 | var0 >> 27) + (var1 ^ var2 ^ var3) + var4 - Int32(899497514) + i[x]
            var1 = var1 << 30 | var1 >> 2
            var3 = ((var4) << 5 | var4 >> 27) + (var0 ^ (var1) ^ var2) + var3 - Int32(899497514) + i[x + 1]
            var0 = var0 << 30 | var0 >> 2
            var2 = ((var3) << 5 | var3 >> 27) + (var4 ^ (var0) ^ var1) + var2 - Int32(899497514) + i[x + 2]
            var4 = var4 << 30 | var4 >> 2
            var1 = ((var2) << 5 | var2 >> 27) + (var3 ^ (var4) ^ var0) + var1 - Int32(899497514) + i[x + 3]
            var3 = var3 << 30 | var3 >> 2
            var0 = ((var1) << 5 | var1 >> 27) + (var2 ^ (var3) ^ var4) + var0 - Int32(899497514) + i[x + 4]
            var2 = var2 << 30 | var2 >> 2

        self.h0 = Long64(Int32(self.h0 + var0))
        self.h1 = Long64(Int32(self.h1 + var1))
        self.h2 = Long64(Int32(self.h2 + var2))
        self.h3 = Long64(Int32(self.h3 + var3))
        self.h4 = Long64(Int32(self.h4 + var4))

        return True

    def hex(self): # retuns string// 0x7b
        self.finalizeHash()
        x = self.h0
        a = self.h1
        e = self.h2
        t = self.h3
        l = self.h4
        
        return self._0x29b497[Int32(x >> 28 & 15)] + self._0x29b497[Int32(x >> 24 & 15)] + self._0x29b497[Int32(x >> 20 & 15)] + self._0x29b497[Int32(x >> 16 & 15)] + self._0x29b497[Int32(x >> 12 & 15)] + self._0x29b497[Int32(x >> 8 & 15)] + self._0x29b497[Int32(x >> 4 & 15)] + self._0x29b497[Int32(15 & x)] + self._0x29b497[Int32(a >> 28 & 15)] + self._0x29b497[Int32(a >> 24 & 15)] + self._0x29b497[Int32(a >> 20 & 15)] + self._0x29b497[Int32(a >> 16 & 15)] + self._0x29b497[Int32(a >> 12 & 15)] + self._0x29b497[Int32(a >> 8 & 15)] + self._0x29b497[Int32(a >> 4 & 15)] + self._0x29b497[Int32(15 & a)] + self._0x29b497[Int32(e >> 28 & 15)] + self._0x29b497[Int32(e >> 24 & 15)] + self._0x29b497[Int32(e >> 20 & 15)] + self._0x29b497[Int32(e >> 16 & 15)] + self._0x29b497[Int32(e >> 12 & 15)] + self._0x29b497[Int32(e >> 8 & 15)] + self._0x29b497[Int32(e >> 4 & 15)] + self._0x29b497[Int32(15 & e)] + self._0x29b497[Int32(t >> 28 & 15)] + self._0x29b497[Int32(t >> 24 & 15)] + self._0x29b497[Int32(t >> 20 & 15)] + self._0x29b497[Int32(t >> 16 & 15)] + self._0x29b497[Int32(t >> 12 & 15)] + self._0x29b497[Int32(t >> 8 & 15)] + self._0x29b497[Int32(t >> 4 & 15)] + self._0x29b497[Int32(15 & t)] + self._0x29b497[Int32(l >> 28 & 15)] + self._0x29b497[Int32(l >> 24 & 15)] + self._0x29b497[Int32(l >> 20 & 15)] + self._0x29b497[Int32(l >> 16 & 15)] + self._0x29b497[Int32(l >> 12 & 15)] + self._0x29b497[Int32(l >> 8 & 15)] + self._0x29b497[Int32(l >> 4 & 15)] + self._0x29b497[Int32(15 & l)]

    def reset(self):
        self.blocks = [Long64(0), Long64(0), Long64(0), Long64(0), Long64(0), Long64(0), Long64(0), Long64(0), Long64(0), Long64(0), Long64(0), Long64(0), Long64(0), Long64(0), Long64(0), Long64(0), Long64(0)]
        self.h0 = Long64(1732584193)
        self.h1 = Long64(4023233417)
        self.h2 = Long64(2562383102)
        self.h3 = Long64(271733878)
        self.h4 = Long64(3285377520)
        self.block = Long64(0)
        self.bytes = Long64(0)
        self.hBytes = Long64(0)
        self.start = Int32(0)
        self.finalized = self.hashed = False;
