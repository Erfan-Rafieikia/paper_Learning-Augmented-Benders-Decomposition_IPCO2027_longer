import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
k=pd.read_pickle('/tmp/ipco_work/stats.pkl'); s=k[k.solvedcfg].copy()
plt.rcParams.update({'font.size':7,'font.family':'serif','axes.linewidth':0.5,'pdf.fonttype':42,'mathtext.fontset':'cm'})
order=['BD','LABD 5%','LABD 15%','LABD 25%','RND 5%','RND 15%','RND 25%']
lab=['BD','L5','L15','L25','R5','R15','R25']
MC={'BD':'#6b6b66','LABD':'#2a78d6','RND':'#eb6834'}
col=[MC[g.split()[0]] for g in order]
# (a) time composition
s['tot']=s.t_sub+s.t_cbo+s.t_master
g=s.groupby('grp')[['t_sub','t_cbo','t_master','tot']].sum(); fr=g[['t_sub','t_cbo','t_master']].div(g.tot,axis=0)
fr=fr.loc[order]; medt=s.groupby('grp').solution_time_sec.median().loc[order]
fig,axs=plt.subplots(1,3,figsize=(4.8,1.75))
ax=axs[0]; x=np.arange(len(order)); bottom=np.zeros(len(order))
parts=[('t_sub','exact subproblems','#1c5cab'),('t_cbo','other callback work','#86b6ef'),('t_master','master (Gurobi)','#cdcdc8')]
for c,l,cc in parts:
    v=(fr[c]*medt).values; ax.bar(x,v,bottom=bottom,color=cc,width=0.7,label=l,edgecolor='white',linewidth=0.4); bottom+=v
ax.set_xticks(x); ax.set_xticklabels(lab,fontsize=6); ax.set_ylabel('median time (s)',labelpad=1); ax.set_title('(a) time composition',fontsize=7,pad=3)
ax.legend(fontsize=5,frameon=False,loc='upper left',handlelength=1)
for ax,(c,t) in zip(axs[1:],[('bnb_nodes','(b) B&B nodes'),('lazy','(c) cuts in master')]):
    data=[s[s.grp==g][c].values for g in order]
    bp=ax.boxplot(data,positions=x,widths=0.6,patch_artist=True,showfliers=False,whis=(0,100),medianprops=dict(color='#1f1f1d',lw=0.9))
    for b,cc in zip(bp['boxes'],col): b.set(facecolor='white',edgecolor=cc,lw=0.8)
    for i,(w1,w2) in enumerate(zip(bp['whiskers'][::2],bp['whiskers'][1::2])): w1.set(color=col[i],lw=0.6); w2.set(color=col[i],lw=0.6)
    for i,(c1,c2) in enumerate(zip(bp['caps'][::2],bp['caps'][1::2])): c1.set(color=col[i],lw=0.6); c2.set(color=col[i],lw=0.6)
    ax.set_yscale('log'); ax.set_xticks(x); ax.set_xticklabels(lab,fontsize=6); ax.set_title(t,fontsize=7,pad=3)
for ax in axs:
    for sp in ['top','right']: ax.spines[sp].set_visible(False)
    ax.tick_params(width=0.4,length=2,pad=1.5); ax.grid(axis='y',lw=0.3,color='#e5e5e2'); ax.set_axisbelow(True)
fig.subplots_adjust(left=0.08,right=0.99,bottom=0.13,top=0.88,wspace=0.42)
fig.savefig('/tmp/ipco_work/fig_diag.pdf'); fig.savefig('/tmp/ipco_work/fig_diag.png',dpi=250)
print(fr.round(3)); print(medt.round(1))
