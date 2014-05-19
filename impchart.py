import sys,os,re, math

#[state, S0, Z0, S1, Z1]
# S0:S0/S0,S1/Z1
transition = {}
# Cell: {crossed-out, [(pairs)]}

print("Implication chart calculator v0.1")
print("MIT licensed.")
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

npairs=0
log2npairs=0
v = re.sub("\s","", input("Enter the transition table string:"))
for state in v.split(";"):
    state = re.sub("\s", "", state) #Remove ALL whitespace
    if not state:
        continue

    m = re.match("^([^:,/]+):(.*)$", state)
    if not m:
        print("Invalid format (skipping): %s" % state)
        continue

    current_state = m.group(1)
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
        sp = tuple(x for x in pair.split("/") if x)
        if len(sp) != 2:
            raise Exception("Invalid pair %s from: %s" % (pair, state))
        
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
for k in tbl:
    print("%5s" % k[0], end=" |")
    for pair in k[1]:
        print("%5s" % pair[0], end=" ")
    for pair in k[1]:
        print("%5s" % pair[1], end=" ")
    print()

implication = {}
print(len(tbl))
for i in range(len(tbl) - 1):
    for j in range(i+1, len(tbl)):
        p1 = tbl[i]
        p2 = tbl[j]
        ret = [False, []]

        for k in range(len(p1[1])):
            if p1[1][k][1] != p2[1][k][1]: #Output not equal
                ret[0] = True
                ret[1] = []
                break
            else:
                ret[1].append((p1[1][k][0], p2[1][k][0]))
        
        implication[(p1[0],p2[0])] = ret

changed = True
while changed:
    changed = False
    for key in implication:
        entry = implication[key]
        if entry[0]:
            continue #Already crossed out
        for ipair in entry[1]:
            if ipair[0] == ipair[1]:
                continue #Self implication; e.g a-a
            if ipair in implication:
                if implication[ipair][0]:
                    #Other pair was crossed-out, so cross out this one too
                    entry[0] = True
                    changed = True
            else:
                swapped = (ipair[1], ipair[0])
                if swapped in implication:
                    if implication[swapped][0]:
                        #As above
                        entry[0] = True
                        changed = True
                else:
                    raise Exception(\
                        "Pair %s but not in implication table!" % (swapped,))
                
print("\nThe final implication table:")
implied={}
for j in range(1, len(tbl)):
    print(tbl[j][0], end="| ")
    for i in range(0, j):
        entry = implication[(tbl[i][0], tbl[j][0])]
        if entry[0]:
            print("X", end=(":" if entry[1] else " "))
        else:
            if tbl[i][0] not in implied:
                implied[tbl[i][0]] = set((tbl[j][0],))
            else:
                implied[tbl[i][0]].add(tbl[j][0])
        if entry[1]:
            print("(", end="")
            a = ",".join("%s-%s" % (ipair[0], ipair[1]) for ipair in entry[1])
            print(a + ")", end=" ")
        
    print()

print("-"*60)
print("    " , end="")
for i in tbl:
    print(i[0], end=" ")
print("\n")

print("Equivalent states:")
for minimal in sorted(implied):
    print("%s (equivalent to %s)" % (minimal, ",".join(implied[minimal])))
print("\nMinimal equivalent states")

for k in set(implied.keys()):
    if k in implied:
        for j in set(implied.keys()):
            if j != k and j in implied:
                if all(q in implied[k] for q in implied[j]):
                    del implied[j]

for minimal in sorted(implied):
    print("%s (equivalent to %s)" % (minimal, ",".join(implied[minimal])))

            













    
            
    
