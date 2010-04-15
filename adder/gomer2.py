# Reimplementation of Gomer, using a 3-address intermediate form.
#  Well, it can't really be 3-address, can it? Sometimes you need to
#  call a function with >2 args.  The main characteristic is that
#  there are no function arguments which include function calls.  So:
#
#   list<x> := "" | ( x ("," x)* )
#   simple := var | literal
#   fcall := var "=" var "(" list<simple> ( "," var "=" simple )* ")"
#   assign := var "=" simple
#   return := "return" simple
#   yield := "yield" simple
#   try := "try" stmt ("except" var stmt)* ("finally" stmt)?
#   raise := raise var
#   if := "if" simple "then" stmt ["else" stmt]
#   while := "while" simple stmt
#   def := "def" var "(" list<var> [ ",*" ("," var)+] ")" stmt
#   break := "break"
#   continue := "continue"
#   global := "global" list<var>
#   nonlocal := "nonlocal" list<var>
#   pass := "pass"
#   stmt := fcall | assign | return | yield | try | raise
#         | if | while | def | break | continue
#         | global | nonlocal | pass
#         | list<stmt>
