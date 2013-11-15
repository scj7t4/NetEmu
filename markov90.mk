format 8
factor on
markov TRANS90
0_1_2_3 0_1_2_3E0123 0.0666666666667
0_1_2_3E0123 0123 0.0666666666667
reward
0123 rew_0123
0_1_2_3 rew_0_1_2_3
0_1_2_3E0123 rew_0_1_2_3E0123
end
0_1_2_3 1.0
end
bind
rew_0123 1
rew_0_1_2_3 0
rew_0_1_2_3E0123 0
end
var SS_trans cexrt(1200;TRANS90)
expr SS_trans
end
