format 8
factor on
markov TRANS0
0_1_2_3 0_1_2_3E01_23 0.0666666666667
0_1_2_3E01_23 01_23 0.0666666666667
reward
0_1_2_3 rew_0_1_2_3
01_23 rew_01_23
0_1_2_3E01_23 rew_0_1_2_3E01_23
end
0_1_2_3 1.0
end
bind
rew_0_1_2_3 0
rew_01_23 1
rew_0_1_2_3E01_23 0
end
var SS_total cexrt(600;TRANS0)
var SS_trans cexrt(60;TRANS0)
expr SS_total
expr SS_trans
end
