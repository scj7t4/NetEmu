format 8
factor on
markov TRANS65
0_1_2_3 0_1_2_3E0123 0.0665333333333
0_1_2_3E0123 0123 0.0666666666667
0_1_2_3 0_1_2_3E013_2 0.000133333333333
0_1_2_3E013_2 013_2 0.0666666666667
0123 013_2 0.000266666666667
013_2 013_2E0123 0.0661333333333
013_2E0123 0123 0.0666666666667
013_2 013_2E2013 0.000533333333333
013_2E2013 2013 0.0666666666667
2013 0_213 0.000266666666667
0_213 0_213E0123 0.0661333333333
0_213E0123 0123 0.0666666666667
0_213 0_213E2013 0.000533333333333
0_213E2013 2013 0.0666666666667
reward
0123 rew_0123
0_1_2_3 rew_0_1_2_3
0_213 rew_0_213
2013 rew_2013
013_2 rew_013_2
0_1_2_3E013_2 rew_0_1_2_3E013_2
0_213E0123 rew_0_213E0123
0_213E2013 rew_0_213E2013
013_2E0123 rew_013_2E0123
013_2E2013 rew_013_2E2013
0_1_2_3E0123 rew_0_1_2_3E0123
end
0_1_2_3 1.0
end
bind
rew_0123 1
rew_0_1_2_3 0
rew_0_213 1
rew_2013 1
rew_013_2 1
rew_0_1_2_3E013_2 0
rew_0_213E0123 0
rew_0_213E2013 0
rew_013_2E0123 0
rew_013_2E2013 0
rew_0_1_2_3E0123 0
end
var SS_total cexrt(600;TRANS65)
var SS_trans cexrt(60;TRANS65)
expr SS_total
expr SS_trans
end
