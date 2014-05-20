import sys,os,re,atexit,math
from qm import QuineMcCluskey
#Such spaghetti code

transition = {}

print("Sequential analysis v0.1")
print()
print("THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.")
print()
print("Usage: A transition table string is of the form:")
print("\tA:B/0,C/1")
print("\tWhere 'A' is the current state, and if the input is 0, then the ")
print("\tnext state is B with output 0. If the input is 1, then the next state")
print("\tis C with an output of 1.")
print()
print("\tList all such 'rows' by delimiting them with semicolons, e.g:")
print("\tA:B/0,C/1;B:C/1,D/0;...")
print()

def hold():
    input("Press enter to exit.")

atexit.register(hold)

use_jk = False if \
         input("Use JK flip-flop? (Otherwise D-FF) [y]/n:")[:1].lower() == 'n' \
         else True

npairs=0
log2npairs=0
v = re.sub("\s","", input("Enter the transition table string:"))
for state in v.split(";"):
    if not state:
        continue

    m = re.match("^([^:,/]+):(.*)$", state)
    if not m:
        print("Invalid format (skipping): %s" % state)
        continue

    current_state = m.group(1).upper()
    pairs = m.group(2).split(",")
    if npairs == 0:
        npairs = len(pairs)
        if not (npairs and not(npairs & (npairs - 1))):
            raise Exception("The number of pairs is not a power of 2!")
        log2npairs = int(math.log(npairs, 2))
    elif npairs != len(pairs):
        raise Exception(\
            "Invalid pair length! Expected %d pairs, but got %d: %s" % \
              (npairs, len(pairs), state))
        
    for pair in pairs:
        sp = list(x.upper() for x in pair.split("/") if x)
        if len(sp) != 2:
            raise Exception("Invalid pair %s from: %s" % (pair, state))
        elif sp[1] != "1" and sp[1] != "0":
            raise Exception("Output must be either 0 or 1: %s" % state)
        
        if current_state not in transition:
            transition[current_state] = [sp]
        else:
            transition[current_state].append(sp)

print("Transition table:")
print("%10s %16s %22s" % ("Current", "Next", "Output"))
print(" " * 11, end="")
for j in range(2):
    for i in range(npairs):
        v = "X=" + "{0:b}".format(i).zfill(log2npairs)
        print("%-5s" % v, end=" ")
    print(end="|")
print()
print("-" * 60)

tbl = sorted(transition.items())
ff_assignment = {}
i = 0
nflipflops = int(math.ceil(math.log(len(tbl),2)))

for k in tbl:
    ff_assignment[k[0]] = tuple(int(x) for x in "{0:b}".format(i).zfill(nflipflops))
    i += 1
    print("%5s" % k[0], end=" |")
    for pair in k[1]:
        print("%5s" % pair[0], end=" ")
    for pair in k[1]:
        print("%5s" % pair[1], end=" ")
    print()


def j_excite(qt,qt1):
    if qt == 0 and qt1 == 0:
        return 0
    elif qt == 0 and qt1 == 1:
        return 1
    return -1

def k_excite(qt,qt1):
    if qt == 1 and qt1 == 0:
        return 1
    elif qt == 1 and qt1 == 1:
        return 0
    return -1

def d_excite(qt, qt1):
    return qt1

def insert_excitation(row, ff_inputs, use_jk=True):
    cstate = ff_assignment[row[0]]
    for entry in row[1]:
        if "__Z" not in ff_inputs:
            ff_inputs["__Z"] = [int(entry[1])]
        else:
            ff_inputs["__Z"].append(int(entry[1]))
        
        nstate = ff_assignment[entry[0]]
        ffi = []
        for i in range(len(cstate)):
            ffn = len(cstate) - i - 1
            if use_jk:
                val = (\
                j_excite(cstate[i], nstate[i]),
                k_excite(cstate[i], nstate[i]))
                ffnames = ("J%d" % ffn, "K%d" % ffn)
            else:
                val = (d_excite(cstate[i], nstate[i]),)
                ffnames = ("D%d" % ffn,)

            for v in range(len(val)):
                if ffnames[v] not in ff_inputs:
                    ff_inputs[ffnames[v]] = [val[v]]
                else:
                    ff_inputs[ffnames[v]].append(val[v])
            
            ffi.append(val)
        entry.append(ffi)

print("Assigned transition table:")
print("%8s %8s %8s %12s %11s" % ("Current", "Input", "Next", "FF input", "Output"))
print(end="  ")
for x in range(nflipflops-1, -1, -1):
    print("Q%d" % x, end=" ")
print("      X", end="       ")
for x in range(nflipflops-1, -1, -1):
    print("Q%d" % x, end=" ")
print(end="  ")
for x in range(nflipflops-1, -1, -1):
    if use_jk:
        print("J%d,K%d" % (x,x), end=" ")
    else:
        print("D%d" % x, end=" ")
print(end="     ")
print(" Z")
print("-" * 60)

ff_inputs = {}

for k in tbl:
    i = 0
    insert_excitation(k, ff_inputs, use_jk)
    for pair in k[1]:
        
        print("%5s" % "".join(str(x) for x in ff_assignment[k[0]]), end=" ")
        print("%5s" % "{0:b}".format(i).zfill(log2npairs), end=" ")
        print("%5s" % "".join(str(x) for x in ff_assignment[pair[0]]), end=" ")
        for ff in pair[2]:
            print("%5s" % ",".join((str(x) if x >= 0 else "x") for x in ff), end=" ")
        print("%5s" % pair[1], end=" ")
        i += 1
        print()

snames = []
for i in range(nflipflops-1, -1, -1):
    snames.append("Q%d" % i)
snames.append("X")

def fmt_str(names, minterm):
    fmt = []
    for i in range(len(minterm)):
        if minterm[i] == '0':
            fmt.append(names[i] + "'")
        elif minterm[i] == '1':
            fmt.append(names[i])
    return ".".join(fmt)

print("Minimised inputs to the flip-flops and output:")
qm = QuineMcCluskey()
for ff in sorted(ff_inputs):
    high = []
    dc = []
    entry = ff_inputs[ff]
    for i in range(len(entry)):
        if entry[i] == 1:
            high.append(i)
        elif entry[i] == -1:
            dc.append(i)
    if ff == "__Z":
        ff = "Z (output)"
    print("%s:" % ff, end=" ")
    #print(snames, qm.simplify(high, dc))
    print(" + ".join(fmt_str(snames, x) for x in qm.simplify(high, dc)))

    
