format 8
factor on
markov TRANS60
0_1_2_3 E0_1_2_3 0.2
E0_1_2_3 0123 0.0666666666667
0123 013_2 0.0008
013_2 E013_2 0.2
E013_2 0123 0.0648
E013_2 2013 0.00186666666667
2013 0_213 0.0008
0_213 E0_213 0.2
E0_213 0123 0.0648
E0_213 2013 0.00186666666667
reward
0123 rew_0123
0_1_2_3 rew_0_1_2_3
E0_1_2_3 rew_E0_1_2_3
0_213 rew_0_213
E0_213 rew_E0_213
2013 rew_2013
013_2 rew_013_2
E013_2 rew_E013_2
end
0_1_2_3 1.0
end
bind
rew_0123 1
rew_E0123 0
rew_0_1_2_3 0
rew_E0_1_2_3 0
rew_0_213 1
rew_E0_213 0
rew_2013 1
rew_E2013 0
rew_013_2 1
rew_E013_2 0
end
var SS_trans cexrt(600;TRANS60)
var SS_avail cexrt(60;TRANS60)
var SS_rate exrt(60;TRANS60)
expr SS_trans
expr SS_avail
expr SS_rate
end
