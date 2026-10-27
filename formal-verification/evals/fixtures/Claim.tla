----------------------------- MODULE Claim -----------------------------
EXTENDS Naturals, FiniteSets
CONSTANT Recheck
Actors == {1, 2}
VARIABLES owners, ready
vars == <<owners, ready>>
Init == /\ owners = {} /\ ready = {}
Check(i) == /\ owners = {}
            /\ ready' = ready \cup {i}
            /\ UNCHANGED owners
Take(i) == /\ i \in ready
           /\ (IF Recheck THEN owners = {} ELSE TRUE)
           /\ owners' = owners \cup {i}
           /\ ready' = ready \ {i}
Release(i) == /\ i \in owners
              /\ owners' = owners \ {i}
              /\ UNCHANGED ready
Next == \E i \in Actors : Check(i) \/ Take(i) \/ Release(i)
TypeOK == /\ owners \subseteq Actors /\ ready \subseteq Actors
SingleOwner == Cardinality(owners) <= 1
Spec == Init /\ [][Next]_vars
=============================================================================
