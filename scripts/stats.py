import pandas as pd, numpy as np
k=pd.read_pickle('/tmp/ipco_work/main_all.pkl'); r=pd.read_pickle('/tmp/ipco_work/metrics_all.pkl')
bd=k[k.M=='BD']; solved_keys=set(zip(bd[bd.stopping_reason=='OPTIMAL'].inst,bd[bd.stopping_reason=='OPTIMAL'].S))
k['solvedcfg']=[ (i,s) in solved_keys for i,s in zip(k.inst,k.S)]
k['share']=(k.ratio.astype(float)*100).round()
k['grp']=np.where(k.M=='BD','BD',k.M+' '+k.share.fillna(0).astype(int).astype(str)+'%')
k['mipsol']=k.mipsol_root+k.mipsol_nonroot
k['callbacks']=k.iteration
k['cuts_exact']=k.exact_cut_construction_count; k['cuts_pred']=k.ml_cut_construction_count
k['lazy']=k.gurobi_mip_cut_count_last_observed
k['t_sub']=k.callback_exact_subproblem_time_sec; k['t_cbo']=k.callback_other_time_sec; k['t_master']=k.master_solver_internal_time_sec
k['t_warm']=k.phase1_execution_time_sec.fillna(0); k['t_pmed']=k.parametric_pmedian_time_sec.fillna(0)
k['t_sel']=k.unified_selection_training_time_sec.fillna(0)
k['t_rest']=k.solution_time_sec-k.t_sub-k.t_cbo-k.t_master-k.t_warm-k.t_sel
s=k[k.solvedcfg]
order=['BD','LABD 5%','LABD 15%','LABD 25%','RND 5%','RND 15%','RND 25%']
cols=['solution_time_sec','t_warm','t_pmed','callbacks','bnb_nodes','mipsol','cuts_exact','cuts_pred','lazy','t_sub','t_cbo','t_master','t_sel','t_rest']
med=s.groupby('grp')[cols].median().loc[order]
pd.set_option('display.width',250); print(med.round(1).to_string())
k.to_pickle('/tmp/ipco_work/stats.pkl')
