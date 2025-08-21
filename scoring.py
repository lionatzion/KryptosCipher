from collections import Counter
EN_LETTER_FREQ={'E':12.7,'T':9.1,'A':8.2,'O':7.5,'I':7.0,'N':6.7,'S':6.3,'H':6.1,'R':6.0,'D':4.3,'L':4.0,'C':2.8,'U':2.8,'M':2.4,'W':2.4,'F':2.2,'G':2.0,'Y':2.0,'P':1.9,'B':1.5,'V':1.0,'K':0.8,'J':0.15,'X':0.15,'Q':0.10,'Z':0.07}
COMMON_BIGRAMS=['TH','HE','IN','ER','AN','RE','ON','AT','EN','ND','TI','ES','OR','TE','OF','ED']
FUNC_WORDS=['THE','OF','TO','IN','ON','AND','IS','IT','AS','AT']
def chi_square_score(t):
    from collections import Counter
    N=len(t); c=Counter(t); chi=0.0
    for ch,p in EN_LETTER_FREQ.items():
        e=p/100.0*N; o=c.get(ch,0)
        if e>0: chi += (o-e)**2/e
    return -chi
def english_fitness(t):
    bg=sum(t.count(b) for b in COMMON_BIGRAMS)
    fw=sum(t.count(w) for w in FUNC_WORDS)
    return chi_square_score(t)*0.5 + bg*1.0 + fw*1.5
