import pandas as pd, numpy as np, glob, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
R='/tmp/trc/SCFLP_class/RESULTS/labd_ipco_'
def tr(root,t):
    f=glob.glob(f'{R}{root}/task_{t}_*/convergence_traces/*.csv')[0]; d=pd.read_csv(f)
    return d[d.event!='solver_iteration_start']
S300='ipco_full300_pmedian_v0_20261107_211634'; FULL='ipco_full_pmedian_20261105_193605'; V0='ipco_cmp_pmedian_v0_20261106_171133'
cases=[('p4, 500 scenarios',10653.75,[(FULL,1,'Standard BD','#6b6b66','-'),(V0,1,'LABD 5%','#2a78d6','-'),(V0,3,'LABD 25%','#2a78d6',(0,(3,1.5))),(FULL,2,'RND 5%','#eb6834','-'),(FULL,4,'RND 25%','#eb6834',(0,(3,1.5)))]),
       ('p10, 300 scenarios',7611.37,[(S300,15,'Standard BD','#6b6b66','-'),(S300,19,'LABD 5%','#2a78d6','-'),(S300,21,'LABD 25%','#2a78d6',(0,(3,1.5))),(S300,16,'RND 5%','#eb6834','-'),(S300,18,'RND 25%','#eb6834',(0,(3,1.5)))])]
plt.rcParams.update({'font.size':7,'font.family':'serif','axes.linewidth':0.5,'pdf.fonttype':42,'mathtext.fontset':'cm'})
fig,axs=plt.subplots(2,2,figsize=(4.8,3.6))
for row,(name,opt,runs) in enumerate(cases):
    for root,t,l,c,ls in runs:
        d=tr(root,t); x=d.elapsed_seconds.clip(lower=1)
        axs[row,0].plot(x,d.lower_bound,color=c,ls=ls,lw=0.9,label=l)
        axs[row,0].plot(x,d.master_upper_bound,color=c,ls=ls,lw=0.9,alpha=0.5)
        axs[row,1].plot(x,100*d.master_relative_gap,color=c,ls=ls,lw=0.9,label=l)
        print(name,l,round(d.elapsed_seconds.max()),round(d.lower_bound.dropna().iloc[-1],2))
    axs[row,0].axhline(opt,color='k',lw=0.5,ls=':')
    axs[row,0].set_ylim(0.15*opt,1.2*opt); axs[row,0].set_ylabel('objective',labelpad=1); axs[row,1].set_ylabel('master gap (%)',labelpad=1); axs[row,1].set_ylim(0,100)
    axs[row,0].set_title(f'{name}: bounds',fontsize=7,pad=3); axs[row,1].set_title(f'{name}: gap',fontsize=7,pad=3)
for ax in axs.flat:
    ax.set_xscale('log')
    for sp in ['top','right']: ax.spines[sp].set_visible(False)
    ax.tick_params(width=0.4,length=2,pad=1.5); ax.grid(lw=0.3,color='#e5e5e2'); ax.set_axisbelow(True)
for ax in axs[1]: ax.set_xlabel('time (s, log scale)',labelpad=1)
axs[0,1].legend(fontsize=5.5,frameon=False,loc='upper right',handlelength=2)
fig.subplots_adjust(left=0.1,right=0.99,bottom=0.1,top=0.94,wspace=0.3,hspace=0.45)
fig.savefig('/tmp/ipco_work/fig_lbub.pdf'); fig.savefig('/tmp/ipco_work/fig_lbub.png',dpi=250)
