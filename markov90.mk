format 8
factor on
markov TRANS90
0_1_2_3 E0_1_2_3 0.2
E0_1_2_3 0123 0.0666666666667
reward
0123 rew_0123
0_1_2_3 rew_0_1_2_3
E0_1_2_3 rew_E0_1_2_3
end
0_1_2_3 1.0
end
bind
rew_0123 1
rew_E0123 0
rew_0_1_2_3 0
rew_E0_1_2_3 0
end
var SS_trans cexrt(600;TRANS90)
var SS_avail cexrt(60;TRANS90)
var SS_rate exrt(60;TRANS90)
expr SS_trans
expr SS_avail
expr SS_rate
end
