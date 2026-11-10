"""Build the scientific report from the saved numerical results and figures."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/layered-oxide-mpl')
from pathlib import Path
import json, sys, hashlib
import matplotlib
matplotlib.use('Agg')
from matplotlib.mathtext import math_to_image
from matplotlib.font_manager import FontProperties
from PIL import Image as PILImage
try:
    import reportlab
except ModuleNotFoundError:
    sys.path.append('/Users/home/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages')
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
EQ=ROOT/'data/report_equations';EQ.mkdir(exist_ok=True)
FONT=Path('/Users/home/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype')
if not FONT.exists():
    from matplotlib import get_data_path
    FONT=Path(get_data_path())/'fonts/ttf'
for name,fn in [('Body','DejaVuSans.ttf'),('BodyBold','DejaVuSans-Bold.ttf'),('BodyItalic','DejaVuSans-Oblique.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT/fn)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
NAVY=colors.HexColor('#17384f');TEAL=colors.HexColor('#287a74');GRAY=colors.HexColor('#536270')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleX',fontName='BodyBold',fontSize=26,leading=32,textColor=NAVY,spaceAfter=15))
styles.add(ParagraphStyle(name='H1X',fontName='BodyBold',fontSize=17,leading=22,textColor=NAVY,spaceAfter=12))
styles.add(ParagraphStyle(name='H2X',fontName='BodyBold',fontSize=11.5,leading=16,textColor=TEAL,spaceBefore=10,spaceAfter=5))
styles.add(ParagraphStyle(name='BodyX',fontName='Body',fontSize=9.5,leading=14,spaceAfter=8))
styles.add(ParagraphStyle(name='SmallX',fontName='Body',fontSize=8,leading=11.5,textColor=GRAY,spaceAfter=6))
styles.add(ParagraphStyle(name='CaptionX',fontName='Body',fontSize=8.1,leading=11.5,textColor=GRAY,spaceAfter=11))
styles.add(ParagraphStyle(name='CellX',fontName='Body',fontSize=8.2,leading=11))
styles.add(ParagraphStyle(name='HeadCellX',fontName='BodyBold',fontSize=8.2,leading=11,textColor=colors.white))
W=524
story=[];eqcount=0
def p(txt,kind='BodyX'):story.append(Paragraph(txt,styles[kind]))
def title(txt):p(txt,'H1X')
def h(txt):p(txt,'H2X')
def page():story.append(PageBreak())
def table(rows,widths=None):
    cells=[[Paragraph(str(c),styles['HeadCellX' if i==0 else 'CellX']) for c in row] for i,row in enumerate(rows)]
    tb=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),
                           ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#eef3f6'),colors.white]),
                           ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
                           ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                           ('LINEBELOW',(0,0),(-1,0),.5,colors.white)]))
    story.append(tb);story.append(Spacer(1,10))
def fig(name,caption,width=W,maxheight=None):
    path=ROOT/'figures'/name
    ww,hh=PILImage.open(path).size;height=width*hh/ww
    if maxheight and height>maxheight:width*=maxheight/height;height=maxheight
    im=Image(str(path),width=width,height=height);im.hAlign='CENTER'
    story.append(im);story.append(Spacer(1,5));p(caption,'CaptionX')
def eq(text):
    global eqcount
    text=text.replace(r'\frac12',r'\frac{1}{2}').replace(r'\mathbf q',r'\mathbf{q}')
    eqcount+=1;path=EQ/f'eq_{eqcount:02}.png'
    math_to_image('$'+text+'$',str(path),prop=FontProperties(size=13),dpi=250,color='#17384f')
    ww,hh=PILImage.open(path).size
    width=ww*72/250;height=hh*72/250
    if width>W:height*=W/width;width=W
    im=Image(str(path),width=width,height=height);im.hAlign='CENTER'
    story.append(Spacer(1,4));story.append(im);story.append(Spacer(1,10))

boot=json.load(open(ROOT/'data/sts_bootstrap.json'))['summary']
fits=json.load(open(ROOT/'data/sts_fit_results.json'))
checks=json.load(open(ROOT/'data/spectral_checks.json'))

p('Layered oxide at half filling','TitleX')
p('Quantitative fits, conditional spectra, and the limits of microscopic inference','H2X')
p('Analysis of the supplied prompt and measurements • 28 October 2026','SmallX')
p('<b>Result.</b> The data support precise empirical activation scales and successful conditional spectral fits at half filling and at nominal filling 0.2. They do not determine a unique microscopic Hamiltonian, and the model comparisons carried out here did not establish one Hamiltonian that reproduces all the measurements. In particular, the tested simple spectral models fail for nominal filling 0.3.')
p('The distinction matters: a causal fit to local tunneling can predict a momentum-resolved spectrum only after choosing a momentum assignment and spectral ansatz. It does not determine spin-response vertices, superconducting stiffness, or a phase diagram. This report gives the computed results and plots without assigning measured confidence intervals to unmeasured microscopic interactions.')
table([['Quantity','Numerical result','Interpretation'],
       ['Effective normal-band t / D','0.9971 ± 0.0035','Conditional DOS fit'],
       ["Effective normal-band t′ / D",'0.1953 ± 0.0022','Conditional DOS fit'],
       ['Half-filled full spectral gap / D','8.0019; 95% [7.9809, 8.0262]','Clean two-pole fit'],
       ['Half-filled NMR activation / D','5.538 ± 0.135','Fixed-prefactor empirical fit'],
       ['Half-filled transport activation / D','3.722 ± 0.049','Fixed-prefactor empirical fit'],
       ['Half-filled Γ-side zero area / BZ','0.0813; 95% [0.0442, 0.1080]','Conditional scalar Green function']],
      [177,165,182])
h('Status of the five requested outputs')
table([['Requested output','What is established here'],
       ['Hamiltonian and every coupling','Explicit auxiliary spectral Hamiltonian; no validated microscopic Hamiltonian or data-derived U, J, interlayer hopping, or pairing interaction.'],
       ['Full filling-temperature phase diagram','Measured state map and transition brackets; unmeasured fillings and low-temperature limits are marked unknown.'],
       ['Explanation of all probes','Observable mechanisms and constraints; identified gaps between spectral fits and a unified microscopic explanation.'],
       ['Three ARPES intensity maps','Conditional half-filled map, a density-tension BCS map, and a clearly labeled rejected 0.3 trial spectrum.'],
       ['Kramers-Kronig and zero area','Executed with convergence checks; area differs from 1/2 within the chosen spectral family, not an established Luttinger-theorem violation.']],
      [173,351])
p('Uncertainties are one standard deviation unless a 95% interval is stated. Narrow statistical intervals condition on the model and measurement assumptions; they do not quantify uncertainty over different microscopic theories.','SmallX')
page()

title('1. Data audit and statistical conventions')
p('The analysis uses the 801-point bias trace in each of four STS panels, 18/39/41 NMR points for fillings 1/2, approximately 0.3 and approximately 0.2, and 48/53/53 resistivity points. No parameters of a named material were imported. Input copies and SHA-256 hashes are included in the accompanying data folder.')
h('Definitions that change the inference')
p('The density is n = 2ν electrons per transition-metal orbital, including both spins. Momenta in all plots use the specified units 2π/a. Energies and temperatures are in D, with k<sub>B</sub> = 1.')
p('The JSON explicitly stores R = 1/T<sub>1</sub>, not 1/(T<sub>1</sub>T). Both R and its quoted error are divided by T to reproduce the NMR display. Fits use the original R values and their original errors. The curves are normalized at T = 4D as supplied.')
p('All low-temperature STS axes are centered at the midpoint of the interval of vanishing conductance. This is known to be the chemical potential only for the half-filled crystal. Identifying the doped gap midpoint with μ is an additional assumption in the BCS trial, not a fact supplied by the data.')
p('The four STS traces are independently normalized. They have no supplied error bars, tunneling matrix elements, absolute spectral calibration, or numerical low/high temperatures. Consequently their relative peak areas cannot by themselves be used as absolute electron-count sum rules.')
h('Likelihood and uncertainty')
eq(r'R(T)=A T\exp(-E_N/T),\qquad \rho(T)=B\exp(E_\rho/T)')
p('NMR and positive resistivity fits minimize a raw-observable Gaussian likelihood with the supplied standard deviations. Exact zero-resistance points are used to bracket a transition and are not entered as infinitely weighted observations. Two thousand parametric bootstrap refits were used for fixed prefactors; one thousand for free powers of T. Covariance estimates were not shrunk when reduced χ² was below one.')
eq(r'S(V)=C\,N_c(V;\eta)+b_0+b_2 V^2')
p('For STS, a Lorentz-broadened local spectral density is fitted with an amplitude and a smooth background. Background, amplitude, and linewidth are measurement nuisance parameters, not Hamiltonian couplings. They are removed when constructing normalized spectra and the clean Green function. Residual-noise bootstrap intervals use 120 replicates, refitting the high-temperature band before the half-filled spectrum.')
p('Shared normalization can correlate errors; no covariance matrix is supplied. The quoted-error Gaussian fits therefore assume independent points. The STS bootstrap assumes independent residual noise and the chosen background form. Neither procedure includes uncertainty from an unknown matrix element, unobserved high-energy spectral weight, or changing the spectral model.')
h('Structural information and what it does not imply')
p('Equal in-plane distances and fourfold symmetry fix a square in-plane Bravais lattice with one transition-metal position per in-plane primitive cell. They do not specify the number of coupled layers in the full crystallographic cell. Unchanged structural diffraction excludes an observed structural supercell or distortion over the measured range; a single NMR line excludes resolved inequivalent local resonances. These observations alone do not establish spin rotation symmetry, time reversal, or absence of every magnetic or electronic order.')
page()

title('2. High-temperature STS: an effective normal band')
eq(r'\epsilon_{\mathbf{k}}=-2t[\cos(2\pi k_x)+\cos(2\pi k_y)]-4t^\prime\cos(2\pi k_x)\cos(2\pi k_y)')
eq(r'N_c(\omega)=-\frac{1}{\pi}\operatorname{Im}\left\langle\frac{1}{\omega+\mu+i\eta-\epsilon_{\mathbf{k}}}\right\rangle_{\mathrm{BZ}}')
fig('sts_normal_fit.png','Figure 1. Direct fit of the high-temperature trace at nominal ν ≈ 0.3. The asymmetric peak is consistent with a square-lattice van Hove feature in this ansatz. The residual RMS is 0.04731 in normalized conductance.',maxheight=302)
table([['Parameter','Estimate','Bootstrap SD','Conditional 95% interval'],
       ['t / D','0.99707','0.00347','[0.99107, 1.00358]'],
       ['t′ / D','0.19534','0.00216','[0.19213, 0.19970]'],
       ['μ / D','-0.90823','0.00812','[-0.92376, -0.89023]'],
       ['η / D','0.08332','0.00810','[0.06701, 0.09798]']],
      [105,105,105,209])
p('The fitted t and t′ describe this effective dispersion. The sign convention t &gt; 0 places the band minimum at Γ. Local DOS data alone do not establish that momentum assignment. The high-temperature value of μ is a spectral fit parameter; the numerical temperature is unspecified, so no finite-temperature density equation was imposed.')
p('<b>Crucial limitation:</b> a thermally deconvolved STS trace is still an interacting spectral measurement. A good fit to a bare-band expression does not prove that these hopping values are the bare kinetic parameters of a temperature-independent microscopic Hamiltonian.')
page()

title('3. Half-filled STS: a causal, number-consistent fit')
eq(r'E_\pm(\mathbf{k})=s[\epsilon_{\mathbf{k}}+4t^\prime]\pm V,\qquad w_\pm(\mathbf{k})=\frac12\pm r\epsilon_{\mathbf{k}}')
eq(r'A_c(\mathbf{k},\omega)=\sum_{\alpha=\pm}w_\alpha(\mathbf{k})\,\delta[\omega-E_\alpha(\mathbf{k})]')
fig('sts_half_linear_weights.png','Figure 2. Half-filled spectral fit. Momentum-dependent pole residues are needed to reproduce both branch shapes. Residual RMS 0.01495 is comparable with the observed fine-scale scatter.',maxheight=292)
table([['Parameter','Estimate ± bootstrap SD','Role'],
       ['s','0.501987 ± 0.002310','Dimensionless dispersion scale'],
       ['V / D','6.002992 ± 0.001657','Half the separation of the two poles'],
       ['rD','0.0323768 ± 0.0006977','Energy-dependent residue coefficient'],
       ['η / D','0.073768 ± 0.002322','Linewidth nuisance; excluded from clean Hamiltonian']],
      [90,205,229])
p('The bootstrap propagates the normal-band uncertainty. The full clean gap is 2(V - 4st) = 8.001864D, with 95% interval [7.980920, 8.026216]D. The clean outer band edges are approximately ±8.00505D. The 4st′ offset makes the gap midpoint exactly zero for this dispersion.')
p('Every momentum has w<sub>+</sub> + w<sub>-</sub> = 1, and the minimum residue is 0.34557. Since the Brillouin-zone average of ε is zero and the lower pole is filled, ⟨w<sub>-</sub>⟩ = 1/2 exactly. Positivity, the spectral sum rule, and the required half filling therefore hold without fitting a separate density parameter.')
page()

title('4. Explicit spectral Hamiltonian and its limits')
p('A Hermitian auxiliary realization of the preceding Green function is completely specified by the following terms, with spin-degenerate physical operators c and auxiliary operators f on the same square Bravais lattice:')
eq(r'H_{\mathrm{spec}}=\sum_{\mathbf{k},\sigma}\left[e_c c^\dagger_{\mathbf{k}\sigma}c_{\mathbf{k}\sigma}+e_f f^\dagger_{\mathbf{k}\sigma}f_{\mathbf{k}\sigma}+v_{\mathbf{k}}(c^\dagger_{\mathbf{k}\sigma}f_{\mathbf{k}\sigma}+f^\dagger_{\mathbf{k}\sigma}c_{\mathbf{k}\sigma})\right]')
eq(r'e_c=(s+2Vr)\epsilon_{\mathbf{k}}+4st^\prime,\qquad e_f=(s-2Vr)\epsilon_{\mathbf{k}}+4st^\prime')
eq(r'v_{\mathbf{k}}=V\sqrt{1-4r^2\epsilon_{\mathbf{k}}^2}')
p('All independent coefficients in this representation are t, t′, s, V and r, tabulated on the preceding pages with their conditional uncertainties. The phase of f fixes the otherwise arbitrary sign of v. No additional constant, interaction, magnetic field, or pairing term is implied. The chemical-potential origin is already incorporated in e<sub>c</sub> and e<sub>f</sub>.')
table([['Property','Status in this representation'],
       ['Translations and point group','Square one-site in-plane periodicity; C4 and reflections preserved.'],
       ['Charge and spin','Total c+f charge U(1) and spin SU(2) are imposed by the spin-independent normal quadratic ansatz.'],
       ['Time reversal','Preserved by real, even dispersions and real hybridization.'],
       ['Particle-hole symmetry','Not present for fitted t′ and offsets.'],
       ['Range','The nonpolynomial v(k) corresponds to generally long-range real-space hybridization.'],
       ['Physical unit cell','One measured in-plane site; f is bookkeeping for a self-energy pole, not an inferred additional atomic orbital.']],
      [145,379])
eq(r'G_c(\mathbf{k},z)=\left[z-e_c-\frac{v_{\mathbf{k}}^2}{z-e_f}\right]^{-1}')
p('<b>This is not a validated microscopic Hamiltonian for the material.</b> Interpreting f as an independent charged orbital would change the physical degrees of freedom and filling count. Interpreting it as a self-energy pole does not determine a spin vertex or the thermodynamic functional. Thus this construction supplies causal spectra, but cannot legitimately be used on its own to calculate the measured NMR, dc resistivity, or superconducting transition.')
p('A bilayer Hubbard model with interlayer singlets is one possible microscopic candidate because the layer count is unspecified. A single-layer correlated insulator or a time-reversal-breaking alternative is not selected or excluded merely by these structural observations. No finite data-derived confidence intervals on U, exchange J, interlayer hopping, spin-orbit coupling, or the pairing interaction follow from the spectral construction.')
page()

title('5. Doped STS: where the tested models fail')
fig('sts_bcs_density_test.png','Figure 3. Nominal ν ≈ 0.2: unconstrained BCS line shape versus a fit imposing exactly ν = 0.2. The unconstrained fit succeeds spectrally but gives a different filling under its number equation.',maxheight=270)
eq(r'\xi_{\mathbf{k}}=s_2\epsilon_{\mathbf{k}}-\mu_2,\quad E_{\mathbf{k}}=\sqrt{\xi_{\mathbf{k}}^2+\Delta^2},\quad w_\pm=\frac12(1\pm\xi_{\mathbf{k}}/E_{\mathbf{k}})')
table([['Nominal ν ≈ 0.2 BCS parameter','Estimate ± conditional Hessian SD'],
       ['s₂','1.003950 ± 0.001362'],['μ₂ / D','-1.913451 ± 0.003221'],
       ['Δ / D','1.966100 ± 0.000946'],['η / D','0.078351 ± 0.001048'],
       ['Calculated filling ν','0.256396 ± 0.000396']],
      [260,264])
p('These errors hold the high-temperature band fixed and assume the chosen background and a constant tunneling matrix element. The full BCS gap is 2Δ ≈ 3.9322D. The local residual RMS is 0.01485. Imposing exactly ν = 0.2 raises it to 0.06020. The input gives no tolerance on “approximately 0.2,” so this is a substantial density-consistency tension, not a formal rejection of every BCS description.')
p('The BCS trial additionally identifies the STS gap midpoint with μ. A different tunneling matrix element, incoherent spectral weight, a modified interacting dispersion, or a different energy-origin assignment can change this inference. Their parameters are not supplied or independently measured here.')
page()

title('6. Nominal filling 0.3: systematic model residuals')
fig('bdg_linear_weights_fit.png','Figure 4. One of the more flexible tested four-pole candidates. Its residuals remain systematic; adding a pairing extension to the successful half-filled spectral form does not solve the intermediate-filling spectrum.',maxheight=282)
table([['Tested spectral family','RMS','Calculated ν','Assessment'],
       ['Two poles; independent c/f dispersions','0.04864','Model-dependent','Systematic shape mismatch'],
       ['Four poles; common pairing, common slopes','0.05814','0.3741','Large linewidth required'],
       ['Four poles; independent affine slopes','0.05389','0.3474','Shape mismatch'],
       ['Four poles; independent t,t′ dispersions','0.04867','0.3698','Pairing reaches lower bound'],
       ['Four poles; linear normal residues','0.04609','0.3839','Residue hits positivity boundary'],
       ['Mirrored poles; fixed ν = 0.3','0.06458','0.3000','Shape mismatch']],
      [238,64,75,147])
p('The low-temperature STS scatter is about 0.015. These residuals are materially larger and have structure across the bands. The tested resolvent formulas were checked independently against momentum sums: common-gap BdG to 5 × 10<super>-16</super> and the mirrored-pole expression to 4 × 10<super>-14</super> at representative complex frequencies.')
p('This is a failure of the tested ansätze, not a theorem that the data are inconsistent or that no microscopic Hamiltonian can explain them. It prevents promoting these fits to a validated effective theory. The rejected trial ARPES map later in this report is included only to document the calculation, and is explicitly labeled as such.')
page()

title('7. NMR: activation and coherence-like enhancement')
fig('nmr_transport_nmr.png','Figure 5. Corrected 1/(T₁T) display, raw-space activated fits, and standardized residuals. Errors crossing the logarithmic display floor remain included in the likelihood. The low-filling enhancement is shown relative to the high-temperature plateau.',maxheight=275)
table([['Filling','Fit range T/D','E<sub>N</sub>/D ± 1σ','Bootstrap 95% interval'],
       ['1/2','All supplied points','5.538 ± 0.135','[5.279, 5.809]'],
       ['≈ 0.3','T ≤ 4.4318','2.634 ± 0.047','[2.540, 2.736]'],
       ['≈ 0.2','T ≤ 0.5','1.747 ± 0.053','[1.644, 1.849]']],
      [75,145,145,159])
p('Allowing R = A T<super>q</super> exp(-E/T) increases the uncertainty: E/D = 5.586 ± 0.516, 2.657 ± 0.139 and 1.641 ± 0.458 for the same three samples. The extra powers do not improve χ² materially, but demonstrate how much a “gap error bar” depends on the prefactor assumption.')
p('For ν ≈ 0.2, the high-temperature 1/(T₁T) plateau is 1.074 ± 0.084. The mean over T/D = 0.7372-1.0209 is 1.622 ± 0.180, a 2.75σ contrast under independent quoted errors. This is consistent with a coherence-like enhancement near superconductivity; it does not prove s-wave symmetry. A single activation law across the full temperature range fails (reduced χ² ≈ 4.92).')
eq(r'\frac{1}{T_1T}\ \propto\ \sum_{\mathbf q}|A_{\mathrm{hf}}(\mathbf q)|^2\lim_{\omega\to0}\frac{\chi^{\prime\prime}(\mathbf q,\omega)}{\omega}')
p('The activation scales measure suppression of the low-frequency spin response. They are not automatically a singlet-triplet gap or the tunneling gap. The hyperfine form factor and interacting spin vertex are unknown, and neither is fixed by a fit to the one-electron Green function.')
page()

title('8. Resistivity and observed transition brackets')
fig('nmr_transport_resistivity.png','Figure 6. Resistivity fits use only positive values. Zero-resistance data delimit transition intervals rather than receiving zero error in a least-squares fit.',maxheight=310)
table([['Filling','Model / measured behavior','Fitted scale'],
       ['1/2','B exp(Eρ/T), 0.45 ≤ T/D ≤ 4','Eρ/D = 3.722 ± 0.049'],
       ['≈ 0.3','B exp(Eρ/T), positive branch','Eρ/D = 0.900 ± 0.044'],
       ['≈ 0.2','a + b T/D, positive branch','a = 0.1759 ± 0.0396; b = 0.1751 ± 0.0172']],
      [70,245,209])
p('The 95% bootstrap transport intervals are [3.622, 3.812]D and [0.806, 0.980]D. Allowing B T<super>q</super> exp(Eρ/T) gives 3.761 ± 0.161D and 0.945 ± 0.140D. The NMR and transport activation scales are distinctly different; identifying both with the same excitation energy would require a derivation that is absent here.')
eq(r'0.325<T_c/D\leq0.400\quad(\nu\simeq0.3)')
eq(r'1.075<T_c/D\leq1.150\quad(\nu\simeq0.2)')
p('These brackets identify the zero-resistance transition as superconductivity, a plausible interpretation of the combined measurements. Bulk superconductivity and its order parameter would require a magnetic, thermodynamic or phase-stiffness test. At half filling, transport is activated down to 0.45D; no data establish the asymptotic T → 0 phase or exclude a lower-temperature transition.')
p('Microscopic resistivity requires a current-current response and a mechanism for relaxation. A density of states or a single-particle gap alone does not specify either. The linear and activated fits are therefore empirical descriptions rather than a Kubo calculation from H<sub>spec</sub>.')
page()

title('9. What can be drawn in the filling-temperature plane')
fig('phase_constraints.png','Figure 7. The measured state map covers 0 ≤ ν ≤ 1 and marks all three crystals. Strips encode measured temperature ranges, not widths of thermodynamic phases or filling error bars. Gray regions are unresolved.',maxheight=315)
table([['Crystal','Measured low-to-high-temperature sequence'],
       ['ν ≈ 0.2','Zero resistance (superconducting candidate) → transition interval → metallic transport with approximately constant high-T 1/(T₁T).'],
       ['ν ≈ 0.3','Zero resistance (superconducting candidate) → transition interval → activated normal transport with an activated spin response.'],
       ['ν = 1/2','Activated charge transport and activated spin response throughout the measured temperature range. Lower temperatures and any higher-temperature phase boundary are unresolved.']],
      [100,424])
p('A full phase diagram of one Hamiltonian would require a validated microscopic model and a calculation of its free energy, correlations, and phase stiffness. Neither a pair of observed transition intervals nor local STS determines the filling dependence of these quantities. No superconducting dome, half-filled metal transition, or pseudogap boundary is drawn by interpolation.')
p('The measured band asymmetry also removes any justification for simply reflecting the hole-doped data about ν = 1/2. The interval 1/2 &lt; ν ≤ 1 is unmeasured and can behave differently. Structural equivalence and a single NMR line constrain candidate phases but do not choose among them.')
page()

title('10. Quantitative consistency tests for simple models')
eq(r'T_c\leq\frac{\pi\nu}{2}\left(|t|+2|t^\prime|\right)')
p('For a strictly two-dimensional single-band model with the stated dispersion and interactions that do not add a current-carrying kinetic term, the superfluid stiffness bound gives the inequality above [1]. It is independent of pairing strength or symmetry within those assumptions.')
fig('model_review_stiffness.png','Figure 8. Conditional test using the effective normal-band fit as the bare kinetic dispersion. The upper bound 0.43598 ± 0.00229D is below the observed lower transition bracket 1.075D at nominal ν = 0.2.',maxheight=285)
p('This rules out that entire conjunction of assumptions, not every Hubbard-derived description. The fitted DOS hopping may be renormalized; the material may have coupled layers, additional bands, a three-dimensional transition, or current-carrying pair/correlated hopping. The uncertainty on the bound is conditional on fixed ν = 0.2 and the hopping covariance; these alternatives dominate its microscopic interpretation.')
h('A small exact-diagonalization check')
eq(r'\Delta_s=\frac{\sqrt{U^2+16t_\perp^2}-U}{2}')
p('An exact 16-state Hubbard-dimer diagonalization gives Δ<sub>s</sub> = 0.32456D for illustrative U = 12D and t<sub>⊥</sub> = D. Matching the half-filled NMR activation as a triplet gap at fixed U = 12D would require t<sub>⊥</sub> = 4.9288D. This is a consistency illustration only: neither U = 12D nor E<sub>N</sub> = Δ<sub>s</sub> is measured. It shows why inferring U from a peak separation and then declaring the spin sector solved is unjustified.')
page()

title('11. ARPES: computed maps and their status')
fig('arpes_candidates.png','Figure 9. Fermi-function-divided intensities are shown as the physical-c spectral function per spin, with a constant photoemission matrix element. The energy window is [-10D, 10D]. The middle panel is a rejected trial spectrum, not a material prediction.',maxheight=310)
p('<b>Half filling.</b> The accepted conditional model gives two roughly parallel branches separated by 2V ≈ 12D, each with bandwidth about 4D. Their weights vary with momentum while summing to one. The absence of zero-energy poles describes a hard single-particle gap; the two branches and weight transfer do not, by themselves, establish Mottness or topological order.')
p('<b>Nominal ν ≈ 0.3.</b> The displayed best independent-dispersion two-pole trial has broad gapped branches but fails the local STS line shape. Its dispersions must not be interpreted as a validated prediction. The missing momentum information cannot be repaired by drawing a visually plausible interpolation.')
p('<b>Nominal ν ≈ 0.2.</b> The BCS trial shows opposite particle/hole branches, back-bending where ξ(k) changes sign, and exchange of coherence weights. These are signatures of the assumed pairing structure. Its successful local line shape is accompanied by ν<sub>calc</sub> ≈ 0.256, so the map is conditional on resolving the filling/matrix-element issue.')
p('The common energy origin is the STS gap midpoint. It is μ for the half-filled crystal and is assumed to be μ in the BCS trial. The chemical potential of the intermediate-filling sample is not supplied. There is consequently no justified common Fermi-energy alignment for all three samples.')
p('A strict requirement for three quantitative material predictions from one fitted microscopic Hamiltonian is therefore not met. The figure preserves this distinction instead of presenting the rejected or density-inconsistent models as successful answers.')
page()

title('12. Kramers-Kronig reconstruction and zero volume')
eq(r'G_c(\mathbf{k},z)=\int_{-\infty}^{\infty}\frac{A_c(\mathbf{k},\omega^\prime)}{z-\omega^\prime}\,d\omega^\prime')
eq(r'G_c(\mathbf{k},z)=\frac{z-e_f(\mathbf{k})}{[z-s(\epsilon_{\mathbf{k}}+4t^\prime)]^2-V^2}')
fig('half_green_zeros.png','Figure 10. Numerical Kramers-Kronig integration agrees with the direct resolvent. The right panel uses the clean η → 0 limit, in which the hard gap makes Im G(k,0) vanish and Re G = 0 is an actual scalar Green-function zero.',maxheight=268)
eq(r'\epsilon_{\mathbf{k}}=-\frac{4st^\prime}{s-2Vr}=-3.4628403D')
eq(r'f_\Gamma=0.0813296,\qquad 95\%\ \mathrm{CI}=[0.04420,\,0.10797]')
p('The Γ-containing side is only about 8.13% of the Brillouin zone, substantially below ν = 1/2 within this spectral family. The bootstrap standard deviation is 0.01671. This is an uncertainty on a conditional prediction, not a model-independent experimental measurement of a zero surface.')
p('The full Brillouin zone, not just the high-symmetry path, was integrated. Grids from 128² to 2048² agree with a one-dimensional phase-space quadrature at approximately the 10<super>-4</super> level in area fraction. At each momentum the sum rule is exact, all residues are positive, and the integrated clean occupation is 1/2 to numerical precision.')
p('The independent principal-value quadrature pairs positive and negative frequencies. Increasing its cutoff from 24D to 40D to 80D reduces the maximum discrepancy from 1.04 × 10<super>-5</super> to 2.01 × 10<super>-6</super> to 2.39 × 10<super>-7</super> D<super>-1</super>. The final positive-frequency grid has 40,001 points. Finite linewidths are used for displayed ARPES only; a broadened Re G = 0 contour is not generally a zero of the full complex G.')
page()

title('13. Why the zero volume is not uniquely inferred')
fig('half_arpes_nonuniqueness.png','Figure 11. Shifting the conditional momentum assignment by (1/2, 1/2) preserves the local spectrum and number sum rule. It changes which side of the same translated contour contains Γ. The corresponding Γ-side fraction is approximately 0.91867 rather than 0.08133.',maxheight=257)
p('Local tunneling measures a momentum average. It therefore cannot determine a momentum assignment without additional structural/band information. An even stronger logical example changes the actual zero-contour volume while keeping a normalized local spectrum, half filling, and gap midpoint μ = 0 fixed. Define f(k) = [cos(2πk<sub>x</sub>) + cos(2πk<sub>y</sub>)]/2 and 0 &lt; λ &lt; 0.4:')
eq(r'A_\lambda=0.1\delta(\omega+4)+(0.4+\lambda f)\delta(\omega+6)+0.1\delta(\omega-4)+(0.4-\lambda f)\delta(\omega-8)')
eq(r'G_\lambda(\mathbf{k},0)=\frac{1}{60}+\frac{7\lambda}{24}f(\mathbf{k})')
p('Every member has nonnegative weights summing to one at each momentum, the same local DOS, occupation 1/2 per spin, and gap edges ±4D. Yet λ = 0.1, 0.2 and 0.3 give Γ-side fractions 0.84554, 0.71146 and 0.65641 on a 1200² grid. This is a logical spectral counterexample, not a fit to the supplied data and not a claim that the full spin and transport responses are identical.')
p('Finally, the auxiliary model makes the distinction between a projected scalar Green function and the full matrix explicit: G<sub>cc</sub> can have a zero while det G of the enlarged noninteracting problem does not. Consequently a scalar zero area unequal to ν is not, by itself, an experimental demonstration that Luttinger’s theorem is violated. General Mott-insulator zero-volume issues require additional assumptions [2,3].')
page()

title('14. Explaining the probes without overinterpreting them')
table([['Measurement','Supported physical implication','What remains model-dependent'],
       ['Diffraction','No observed in-plane structural symmetry breaking or supercell over the stated range.','Magnetic order, orbital currents, layer structure, topological order and weak electronic order are not fixed.'],
       ['Uniform STS','Homogeneous measured surface conductance; finite intervals of suppressed single-particle spectral weight.','Nature of the gap, exact doped μ, momentum dependence, matrix elements and microscopic interaction.'],
       ['Single NMR line','No resolved distinct transition-metal resonance environments.','It is not proof of all spin or time-reversal symmetries.'],
       ['Activated 1/(T₁T)','Suppressed low-frequency spin fluctuations; empirical activation scales quantified.','Triplet gap, hyperfine filtering, coherence factors and interaction vertices.'],
       ['Activated resistivity','Thermally activated transport in measured ranges.','Carrier excitation energy versus mobility activation and current relaxation.'],
       ['Zero resistance','Superconductivity is a plausible low-temperature interpretation for both doped crystals.','Bulk fraction, pairing symmetry, stiffness and transition universality.']],
      [94,205,225])
h('What can be claimed about the most credible state?')
p('The strongest economical description is a spatially uniform, single-particle-gapped half-filled state with activated charge transport and strongly suppressed low-energy spin response, together with doped superconducting candidates. A singlet correlated parent is plausible. Neither a single-layer spin liquid, an interlayer singlet insulator, a magnetic gap, nor another correlated state is uniquely established by the supplied probes.')
h('What cannot be assigned a measured coefficient and uncertainty?')
p('The onsite interaction U, exchange couplings, interlayer hopping, spin-orbit terms, pair hopping, pairing interaction, and their filling dependence have not been identified. Assigning them the pole separation V, the activation energy, or the fitted linewidth would confuse different quantities. There is no valid table of finite experimental error bars for all these microscopic terms.')
p('To close the inverse problem, the most discriminating missing inputs are the full layer/unit-cell structure; the true low-temperature chemical-potential reference for each doped spectrum; momentum-resolved normal and gapped bands; calibrated spectral weights or tunneling matrix elements; and bulk magnetic/superfluid response. A selected microscopic model could then be tested by finite-size many-body calculations. These are missing physical constraints, not missing algebra in the present fits.')
page()

title('15. Numerical record, reproducibility, and references')
table([['Calculation','Approximation / size actually used'],
       ['Normal-band local Green function','One momentum integral analytic, the remaining periodic quadrature numerical; convergence checked at the fitted broadening.'],
       ['Half-filled spectral function','Explicit two-pole ansatz; no many-body exactness claimed. 120 residual bootstrap replicates with normal-band refits.'],
       ['NMR and transport','Raw-observable nonlinear fits; 2,000 fixed-prefactor and 1,000 free-prefactor parametric bootstrap refits.'],
       ['ARPES paths','661 points along Γ-X-M-Γ; 1,801 frequencies in [-10D,10D] for the comparison figure.'],
       ['Zero contour / area','Full BZ grids up to 2048² plus one-dimensional quadrature; clean η = 0.'],
       ['Independent KK check','Positive-frequency Simpson quadrature up to 80D, 40,001 points, evaluated at 61 path momenta.'],
       ['Many-body diagnostic','Exact 16-state Hubbard-dimer diagonalization only. No ten-site material calculation or thermodynamic phase simulation is claimed.']],
      [160,364])
h('Reproduction package')
p('The accompanying folder contains the input copies and hashes, numerical JSON files, covariance matrices, bootstrap samples, NPZ spectral arrays, PNG figures, and analysis scripts. RUNME.txt gives the execution order. The scripts use NumPy, SciPy, Matplotlib and, for this report, ReportLab and Pillow. All plotted scientific parameters come from the supplied measurements or are explicitly labeled illustrative assumptions.')
p('Principal result files: sts_fit_results.json, sts_bootstrap.json, nmr_transport_results.json, spectral_checks.json, arpes_candidates_metadata.json, phase_constraints.json, and model_review_figure_results.json. Rejected-model fits are retained in the bdg_* and sts_* comparison files so that failures are reviewable.','SmallX')
h('Primary-method references')
p('[1] T. Hazra, N. Verma and M. Randeria, <i>Upper bounds on the superfluid stiffness and superconducting T<sub>c</sub></i>, Physical Review X 9, 031049 (2019). <link href="https://arxiv.org/abs/1811.12428" color="#1d6891">arXiv:1811.12428</link>. Used for the conditional stiffness bound, not for material parameters.','SmallX')
p('[2] T. D. Stanescu, P. W. Phillips and T.-P. Choy, <i>Much Ado about Zeros: The Luttinger Surface and Mottness</i>, Physical Review B 75, 104503 (2007). <link href="https://arxiv.org/abs/cond-mat/0602280" color="#1d6891">arXiv:cond-mat/0602280</link>.','SmallX')
p('[3] A. Rosch, <i>Breakdown of Luttinger’s theorem in two-orbital Mott insulators</i>, European Physical Journal B 59, 495 (2007). <link href="https://arxiv.org/abs/cond-mat/0602656" color="#1d6891">arXiv:cond-mat/0602656</link>.','SmallX')
h('Scope of the completed result')
p('The empirical fits, uncertainty estimates, conditional spectral calculations, Kramers-Kronig reconstruction, zero-volume calculation and model checks have been carried out. A single validated microscopic Hamiltonian and its full phase diagram have <b>not</b> been determined. The rejected intermediate-filling spectrum and unresolved phase regions are retained visibly, because replacing them with confident predictions would exceed what the analysis supports.')

def decor(c,doc):
    c.saveState();c.setStrokeColor(colors.HexColor('#c8d5df'));c.setLineWidth(.5)
    c.line(44,38,568,38);c.setFont('Body',7.4);c.setFillColor(GRAY)
    c.drawString(44,25,'Layered oxide | supplied-data analysis | conditional model results')
    c.drawRightString(568,25,str(doc.page));c.restoreState()

out=ROOT/'layered_oxide_analysis.pdf'
doc=SimpleDocTemplate(str(out),pagesize=(612,792),rightMargin=44,leftMargin=44,topMargin=42,bottomMargin=49,
                      title='Layered oxide: quantitative analysis and conditional predictions',author='Scientific analysis from supplied measurements')
doc.build(story,onFirstPage=decor,onLaterPages=decor)
print(out)
