This is a small, self-contained, **real** Python application used as the test subject for AURA's engine tests.

It contains:
- Real import relationships (auth → database, routes → auth, payment service crossing concerns)
- A deliberately large `database.py` (many methods + size) to produce genuine "Oversized Module / God Object" risks
- Multiple modules so that static dependency analysis and temporal coupling have real signals

A fresh copy of this tree is git-initialized with 4 real commits at test time so that `chronos_git_engine` produces authentic co-change data (no mocks).

All AURA test assertions are derived from actual output of the scanners and reasoning engines running on this code.