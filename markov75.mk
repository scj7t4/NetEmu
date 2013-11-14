format 8
factor on
markov TRANS75
0_1_2_3 0_1_2_3E0123 0.2
0_1_2_3E0123 0123 0.0666666666667
0123 013_2 0.0004
013_2 013_2E0123 0.2
013_2E0123 0123 0.0666666666667
reward
0123 rew_0123
0_1_2_3 rew_0_1_2_3
013_2 rew_013_2
0_1_2_3E0123 rew_0_1_2_3E0123
013_2E0123 rew_013_2E0123
end
0_1_2_3 1.0
end
bind
rew_0123 1
rew_0_1_2_3 0
rew_013_2 1
rew_0_1_2_3E0123 0
rew_013_2E0123 0
end
var SS_trans cexrt(600;TRANS75)
var SS_avail cexrt(60;TRANS75)
var SS_rate exrt(60;TRANS75)
expr SS_trans
expr SS_avail
expr SS_rate
end
