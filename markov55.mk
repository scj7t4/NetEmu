format 8
factor on
markov TRANS55
0_1_2_3 0_1_2_3E0123 0.1988
0_1_2_3E0123 0123 0.0666666666667
0_1_2_3 0_1_2_3E013_2 0.0012
0_1_2_3E013_2 013_2 0.0666666666667
0123 013_2 0.0016
013_2 013_2E0123 0.19
013_2E0123 0123 0.0666666666667
013_2 013_2E2013 0.01
013_2E2013 2013 0.0666666666667
013_2 01_2_3 0.0004
013_2 01_2_3 0.0004
2013 0_213 0.0016
01_2_3 01_2_3E012_3 0.002
01_2_3E012_3 012_3 0.0666666666667
01_2_3 01_2_3E0123 0.19
01_2_3E0123 0123 0.0666666666667
01_2_3 01_2_3E013_2 0.008
01_2_3E013_2 013_2 0.0666666666667
012_3 012_3E0123 0.19
012_3E0123 0123 0.0666666666667
012_3 012_3E3012 0.01
012_3E3012 3012 0.0666666666667
012_3 01_2_3 0.0004
012_3 01_2_3 0.0004
0_213 0_213E0123 0.19
0_213E0123 0123 0.0666666666667
0_213 0_213E2013 0.01
0_213E2013 2013 0.0666666666667
3012 0_312 0.0016
0_312 0_312E0123 0.19
0_312E0123 0123 0.0666666666667
0_312 0_312E3012 0.01
0_312E3012 3012 0.0666666666667
reward
0_1_2_3 rew_0_1_2_3
012_3 rew_012_3
0_213 rew_0_213
0_312 rew_0_312
0123 rew_0123
2013 rew_2013
01_2_3 rew_01_2_3
013_2 rew_013_2
3012 rew_3012
0_312E3012 rew_0_312E3012
01_2_3E012_3 rew_01_2_3E012_3
012_3E3012 rew_012_3E3012
0_1_2_3E013_2 rew_0_1_2_3E013_2
012_3E0123 rew_012_3E0123
01_2_3E013_2 rew_01_2_3E013_2
01_2_3E0123 rew_01_2_3E0123
0_213E2013 rew_0_213E2013
013_2E0123 rew_013_2E0123
0_312E0123 rew_0_312E0123
013_2E2013 rew_013_2E2013
0_1_2_3E0123 rew_0_1_2_3E0123
0_213E0123 rew_0_213E0123
end
0_1_2_3 1.0
end
bind
rew_0_1_2_3 0
rew_012_3 1
rew_0_213 1
rew_0_312 1
rew_0123 1
rew_2013 1
rew_01_2_3 1
rew_013_2 1
rew_3012 1
rew_0_312E3012 0
rew_01_2_3E012_3 0
rew_012_3E3012 0
rew_0_1_2_3E013_2 0
rew_012_3E0123 0
rew_01_2_3E013_2 0
rew_01_2_3E0123 0
rew_0_213E2013 0
rew_013_2E0123 0
rew_0_312E0123 0
rew_013_2E2013 0
rew_0_1_2_3E0123 0
rew_0_213E0123 0
end
var SS_trans cexrt(600;TRANS55)
var SS_avail cexrt(60;TRANS55)
var SS_rate exrt(60;TRANS55)
expr SS_trans
expr SS_avail
expr SS_rate
end
