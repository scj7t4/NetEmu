format 8
factor on
markov TRANS0
0_1_2_3 0_1_2_3E01_23 0.2
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
var SS_trans cexrt(600;TRANS0)
var SS_avail cexrt(60;TRANS0)
var SS_rate exrt(60;TRANS0)
expr SS_trans
expr SS_avail
expr SS_rate
end
