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
var SS_total cexrt(600;TRANS90)
var SS_trans cexrt(60;TRANS90)
expr SS_total
expr SS_trans
end
