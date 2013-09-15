import random

def attempt_delivery(p):
    if random.random() <= p/100.0:
        return True
    return False

class SUC(object):
    def __init__(self):
        self.q = []
        self.ACK = None
        self.s = 0

    def tick(self,p):
        i = 0
        while i < len(self.q) and i < 8:
            if attempt_delivery(p):
                yield ('MSG',self.q[i][0],self.q[i][1])
            i += 1
        if self.ACK and attempt_delivery(p):
            yield ('ACK',self.ACK,'')
            #self.ACK = None

    def recv(self, msg):
        (t,s,m) = msg
        if t == 'ACK':
            while 0 < len(self.q) and self.q[0][0] <= s:
                self.q.pop(0)
        if t == 'MSG' and self.ACK < s:
            self.ACK = s
            
    def send(self, msg):
        self.q.append((self.s,msg))
        self.s += 1

