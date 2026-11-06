#!/usr/bin/env python3
"""Reproducible synthetic diagnostics. No model API calls, no model capability claims."""
import json
import math
import platform
import random
import statistics as st
from pathlib import Path

SEED = 20261106

def ci(mean, se):
    return [mean - 1.959963984540054 * se, mean + 1.959963984540054 * se]

def paired(counts):
    # both correct, A only, B only, both wrong
    both, a_only, b_only, neither = counts
    a = [1]*both + [1]*a_only + [0]*b_only + [0]*neither
    b = [1]*both + [0]*a_only + [1]*b_only + [0]*neither
    d = [x-y for x,y in zip(a,b)]
    se = math.sqrt(st.variance(d) / len(d))
    unpaired_se = math.sqrt((st.variance(a)+st.variance(b))/len(d))
    return dict(n=len(d), A=st.mean(a), B=st.mean(b), delta=st.mean(d),
                discordant=a_only+b_only, paired_se=se, paired_ci95=ci(st.mean(d),se),
                unpaired_se=unpaired_se, unpaired_ci95=ci(st.mean(d),unpaired_se))

def bootstrap_ci(values, rng, B=10000):
    n=len(values)
    samples=sorted(st.mean(rng.choices(values,k=n)) for _ in range(B))
    return [samples[round(.025*(B-1))],samples[round(.975*(B-1))]]

def main():
    rng=random.Random(SEED)
    high=paired((680,40,20,260))
    low=paired((430,290,270,10))
    assert high['A']==low['A']==.72 and high['B']==low['B']==.70
    assert high['paired_ci95'][0]>0 and low['paired_ci95'][0]<0
    # 100 independently sampled clusters, ten identical observations in each.
    clusters=[1]*60+[0]*40
    rows=[x for x in clusters for _ in range(10)]
    naive=math.sqrt(st.variance(rows)/len(rows))
    cluster=math.sqrt(st.variance(clusters)/len(clusters))
    cluster_result=dict(n_rows=len(rows),n_clusters=len(clusters),mean=st.mean(rows),
        naive_se=naive,cluster_mean_se=cluster,se_ratio=cluster/naive,
        naive_row_bootstrap_ci95=bootstrap_ci(rows,rng,2000),
        cluster_bootstrap_ci95=bootstrap_ci(clusters,rng,2000))
    # Each model is truly 70% accurate; selecting by one held-out realization inflates the winner.
    winners=[]
    for _ in range(2000):
        winners.append(max(sum(rng.random()<.7 for _ in range(200))/200 for _ in range(20)))
    output={
      'experiment_type':'synthetic mathematical/statistical diagnostics, not LLM inference',
      'seed':SEED,'python':platform.python_version(),
      'same_aggregate_different_paired_uncertainty':{'high_overlap':high,'low_overlap':low},
      'cluster_pseudoreplication':cluster_result,
      'judge_prevalence':{'gold_positive':95,'gold_negative':5,'judge_always_positive':True,
          'raw_accuracy':.95,'positive_recall':1.,'negative_recall':0.,'balanced_accuracy':.5,
          'chance_agreement_from_marginals':.95,'cohen_kappa':0.,'repeat_consistency':1.},
      'multiple_comparisons':{'independent_tests':20,'per_test_alpha':.05,
          'probability_at_least_one_false_positive':1-.95**20},
      'winner_selection':{'true_success_probability':.7,'candidates':20,'n_per_candidate':200,
          'replications':len(winners),'mean_selected_observed_score':st.mean(winners),
          'mean_optimism':st.mean(winners)-.7},
      'zero_failures':{'independent_trials':100,'failures':0,
          'one_sided_95pct_binomial_upper_failure_rate':1-.05**(1/100)},
      'different_denominators':{'A_slice_rates':[.90,.60],'B_slice_rates':[.85,.55],
          'A_slice_weights':[.10,.90],'B_slice_weights':[.90,.10],
          'A_mismatched_overall':.1*.9+.9*.6,'B_mismatched_overall':.9*.85+.1*.55,
          'A_common_equal_weight':(.9+.6)/2,'B_common_equal_weight':(.85+.55)/2},
      'task_heterogeneity':{'per_task_p':[.2,.8],'mean_p':.5,
          'mean_pass_at_2':sum(1-(1-p)**2 for p in [.2,.8])/2,
          'plug_in_mean_pass_at_2':1-(1-.5)**2,
          'mean_all_2_success':sum(p**2 for p in [.2,.8])/2,
          'plug_in_mean_all_2_success':.5**2},
      'variance_identity_audit':{'variance_A':1/12,'variance_B':1/12,'correlation':.5,
          'covariance':1/24,'unpaired_variance_before_dividing_n':1/6,
          'paired_variance_before_dividing_n':1/12,
          'relative_variance_reduction':.5},
    }
    output_path=Path(__file__).parent/'results'/'statistical_diagnostics.json'
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(output,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
