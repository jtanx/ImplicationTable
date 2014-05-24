ImplicationTable
================

Calculates the implication chart to minimise the number of states of a finite state machine.
It seems to work, I dunno...

Example:
~~~~~
Usage: A transition table string is of the form:
        A:B/0,C/1
        Where 'A' is the current state, and if the input is 0, then the
        next state is B with output 0. If the input is 1, then the next state
        is C with an output of 1.

        List all such 'rows' by delimiting them with semicolons, e.g:
        A:B/0,C/1;B:C/1,D/0;...

Enter the transition table string:a:c/0,f/0;b:d/0,e/0;c:h/0,g/0;d:b/0,g/0;e:e/0,
b/1;f:f/0,a/1;g:c/0,g/1;h:c/0,f/0
Transition table:
   Current             Next                 Output
           X=0   X=1   |X=0   X=1   |
------------------------------------------------------------
    A |    C     F     0     0
    B |    D     E     0     0
    C |    H     G     0     0
    D |    B     G     0     0
    E |    E     B     0     1
    F |    F     A     0     1
    G |    C     G     0     1
    H |    C     F     0     0
8

The final implication table:
B| (C-D,F-E)
C| X:(C-H,F-G) X:(D-H,E-G)
D| X:(C-B,F-G) X:(D-B,E-G) (H-B,G-G)
E| X X X X
F| X X X X (E-F,B-A)
G| X X X X X:(E-C,B-G) X:(F-C,A-G)
H| (C-C,F-F) (D-C,E-F) X:(H-C,G-F) X:(B-C,G-F) X X X
------------------------------------------------------------
    A B C D E F G

Equivalent states:
A (equivalent to H,B)
B (equivalent to H)
C (equivalent to D)
E (equivalent to F)

Minimal equivalent states
A (equivalent to H,B)
C (equivalent to D)
E (equivalent to F)

Minimised complete set of states required:
(ABH) (CD) (EF) G
~~~~~

There should not *theoretically* be any limit to the size of input -- it should be able to handle n flip flops, but will subsequently require 2^n transitions/outputs to be specified for each state.
