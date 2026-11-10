"""Build the explicitly incomplete, corrected single-orbital research report."""
import os,sys,json,hashlib
os.environ['MPLCONFIGDIR']='/tmp/single-orbital-mpl'
sys.path.append('/Users/home/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages')
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
FONT=Path(matplotlib.get_data_path())/'fonts/ttf'
pdfmetrics.registerFont(TTFont('DejaVu',str(FONT/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuBold',str(FONT/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVuBold')
W,H=595.28,841.89;M=43.;BW=W-2*M
PDF=ROOT/'single_orbital_reanalysis.pdf'
C=canvas.Canvas(str(PDF),pagesize=(W,H))
C.setTitle('Single-orbital reanalysis: physical calculations and unresolved joint inference')
C.setAuthor('Research reanalysis from supplied prompt and measurements')
STYLE=ParagraphStyle('body',fontName='DejaVu',fontSize=10,leading=14,textColor=colors.HexColor('#243343'),spaceAfter=7)
SMALL=ParagraphStyle('small',parent=STYLE,fontSize=8.3,leading=11)
BLUE=colors.HexColor('#254d70');Y=0;PAGE=0;LOG=[]

def page(title,subtitle=''):
    global PAGE,Y
    if PAGE:endpage()
    PAGE+=1;Y=H-48
    C.setFillColor(BLUE);C.setFont('DejaVuBold',18);C.drawString(M,Y,title);Y-=22
    if subtitle:
        C.setFillColor(colors.HexColor('#667587'));C.setFont('DejaVu',9);C.drawString(M,Y,subtitle);Y-=18
    C.setStrokeColor(colors.HexColor('#c9d4dc'));C.line(M,Y,W-M,Y);Y-=17

def para(s,small=False):
    global Y
    p=Paragraph(s,SMALL if small else STYLE);w,h=p.wrap(BW,1000);p.drawOn(C,M,Y-h);Y-=h+8

def sub(s):
    global Y
    C.setFont('DejaVuBold',11);C.setFillColor(BLUE);C.drawString(M,Y-3,s);Y-=22

def table(rows,widths=None):
    global Y
    widths=widths or [BW/len(rows[0])]*len(rows[0])
    data=[[Paragraph(str(v),SMALL) for v in row] for row in rows]
    t=Table(data,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef3')),('VALIGN',(0,0),(-1,-1),'TOP'),
                          ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
                          ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
                          ('LINEBELOW',(0,0),(-1,0),.7,BLUE),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d7dfe6'))]))
    w,h=t.wrap(BW,1000);t.drawOn(C,M,Y-h);Y-=h+12

def fig(path,maxheight=350,caption=None):
    global Y
    p=ROOT/path;im=Image.open(p);ratio=im.width/im.height
    ww=min(BW,maxheight*ratio);hh=ww/ratio
    C.drawImage(ImageReader(im),M+(BW-ww)/2,Y-hh,width=ww,height=hh,mask='auto');Y-=hh+9
    if caption:para(caption,True)

def formula(name,lines,fontsize=14):
    p=ROOT/'figures'/name
    f=plt.figure(figsize=(10,.55*len(lines)+.12));f.patch.set_alpha(0)
    for i,line in enumerate(lines):f.text(.01,1-(i+.75)/(len(lines)+.25),line,fontsize=fontsize,va='center')
    f.savefig(p,dpi=220,transparent=True,bbox_inches='tight',pad_inches=.08);plt.close(f)
    fig('figures/'+name,maxheight=48*len(lines))

def endpage():
    LOG.append({'page':PAGE,'last_body_baseline':Y})
    assert Y>48,('Page overflow',PAGE,Y)
    C.setStrokeColor(colors.HexColor('#d7dfe6'));C.line(M,38,W-M,38)
    C.setFont('DejaVu',7.5);C.setFillColor(colors.HexColor('#6d7b87'))
    C.drawString(M,25,'Single physical orbital per site | energies in D | corrected research assessment')
    C.drawRightString(W-M,25,str(PAGE));C.showPage()

gap=json.load(open(ROOT/'data/hubbard_gap_fits.json'))
spin=json.load(open(ROOT/'response_spin_dynamics.json'))
trans=json.load(open(ROOT/'transport_kubo_results.json'))
kres=json.load(open(ROOT/'data/hubbard_kspace_results.json'))
audit=json.load(open(ROOT/'audit_electron_spectra.json'))

page('Single-orbital reanalysis','Outcome: physical calculations completed; a validated joint microscopic solution was not obtained')
para('<b>The previous auxiliary-pole construction is withdrawn as a solution to the microscopic single-orbital task.</b> This reanalysis uses only the four physical states of one spinful orbital at each site: empty, spin up, spin down, and double occupancy. It computes physical electron, spin, and current responses rather than assigning separate fitted gaps to three probes.')
para('<b>The main result is a failure to establish a joint fit, not a proof that no single-orbital theory can work.</b> Neither the ordinary Hubbard benchmarks nor the tested exchange/pairing extensions provide a validated common explanation. Consequently, this report does not supply an identified microscopic parameter set or claim a complete material phase diagram. The ARPES and Green-function plots below are explicitly conditional finite-cluster benchmarks.')
sub('Quantities the measurements do constrain')
table([
 ['Quantity','Estimate in D','Meaning / uncertainty'],
 ['Effective normal-state DOS hopping','t_eff = 0.9971 ± 0.0035<br/>t′_eff = 0.1953 ± 0.0022','Residual-bootstrap 1σ within a square-band DOS fit; not an identification of bare hopping.'],
 ['Half-filled STS full gap','8.002 ± 0.011','Conditional on the earlier line-shape extraction. Its microscopic interpretation is not retained.'],
 ['NMR activation, ν = 0.5','5.538 ± 0.135','Raw-rate fit R = A T exp(−E/T).'],
 ['NMR activation, ν ≈ 0.3','2.634 ± 0.047','Same empirical prefactor; not a proven singlet-triplet energy.'],
 ['NMR activation, ν ≈ 0.2','1.747 ± 0.053','Low-T window T ≤ 0.474D.'],
 ['Resistivity activation','3.722 ± 0.049 at ν = 0.5<br/>0.900 ± 0.044 at ν ≈ 0.3','Positive-resistance branch, ρ = A exp(Eρ/T).'],
 ['Zero-resistance onset','0.325 &lt; T/D ≤ 0.400 at ν ≈ 0.3<br/>1.075 &lt; T/D ≤ 1.150 at ν ≈ 0.2','Sampling brackets, not fitted Gaussian errors.']
 ],[130,173,BW-303])
para('These statistical errors condition on the fitted form and the supplied errors. They exclude uncertainty in the Hamiltonian, dimensionality, tunneling matrix elements, and approximate doped fillings. The earlier reported Γ-side zero area of about 8.13% is not a validated result and is withdrawn.',True)

page('Physical Hamiltonian and observables','One site per primitive in-plane cell; no independent auxiliary electron orbital')
formula('hamiltonian.png',[
 r'$H=-t\!\sum_{\langle ij\rangle,\sigma}(c^\dagger_{i\sigma}c_{j\sigma}+\mathrm{h.c.})-t^\prime\!\sum_{\langle\langle ij\rangle\rangle,\sigma}(c^\dagger_{i\sigma}c_{j\sigma}+\mathrm{h.c.})+U\sum_i n_{i\uparrow}n_{i\downarrow}-\mu\sum_i n_i$',
 r'$\quad+J_1\!\sum_{\langle ij\rangle}(\mathbf{S}_i\cdot\mathbf{S}_j-n_i n_j/4)+J_2\!\sum_{\langle\langle ij\rangle\rangle}(\mathbf{S}_i\cdot\mathbf{S}_j-n_i n_j/4)$',
 r'$\quad-P\!\sum_{\langle ij\rangle}(\Delta_i^\dagger\Delta_j+\mathrm{h.c.})+V_1\!\sum_{\langle ij\rangle}(n_i-1)(n_j-1),\qquad\Delta_i=c_{i\downarrow}c_{i\uparrow}.$'
 ],12)
para('Here nᵢ = nᵢ↑ + nᵢ↓ and Sᵢ = cᵢ†σcᵢ/2. All interactions act on the same physical electrons. The ordinary Hubbard benchmark sets J₁ = J₂ = P = V₁ = 0. The exchange and pair terms define the explicitly tested extension, not additional fitted material coefficients. Chemical potential fixes filling; canonical calculations omit −μN and restore μ in spectral energies.')
para('The real-coefficient bulk Hamiltonian has charge U(1), spin SU(2), time reversal, lattice translations, and square-lattice rotations. Its ground state could break some of these symmetries. A one-line NMR spectrum and unchanged ionic diffraction do not independently establish time reversal, spin-liquid order, or the absence of every electronic bond order. Nonzero t′ prevents assuming symmetry about ν = 1/2.')
sub('Two spectral peaks are compatible with one physical orbital')
formula('atomic_and_response.png',[
 r'$G_\sigma^{\mathrm{atom}}(z)=\frac{1-\langle n_{\bar\sigma}\rangle}{z+\mu}+\frac{\langle n_{\bar\sigma}\rangle}{z+\mu-U},\qquad A=-\mathrm{Im}\,G^R/\pi.$',
 r'$\frac{1}{T_1T}\ \propto\ \sum_{\mathbf{q}}|A_{\mathrm{hf}}(\mathbf{q})|^2\lim_{\omega\to\omega_N}\frac{\chi_{+-}^{\prime\prime}(\mathbf{q},\omega)}{\omega},\qquad\sigma_{xx}\ \text{from}\ \langle j_x j_x\rangle.$'
 ],13)
para('The atomic two poles describe different many-body addition/removal processes of the same orbital. In contrast, a chosen two-pole spectrum alone does not determine the spin vertex, the current response, or a thermodynamic phase diagram. That missing derivation was the central problem in the prior answer.')
para('For an onsite-U model, exact spectral moments require M₁(k) = ε(k) + U⟨n̄σ⟩ − μ and M₂(k) − M₁(k)² = U²⟨n̄σ⟩[1 − ⟨n̄σ⟩]. The earlier two-pole ansatz had a momentum-dependent variance and fails this onsite-U test. This tests that ansatz; local STS alone does not measure these momentum-resolved moments.',True)

page('Measured spectra and empirical responses','Original measurements preserved; raw NMR data are R = 1/T₁, not R/T')
fig('sts_empirical_observables.png',maxheight=530)
para('For NMR the likelihood uses the supplied R and its uncertainty; division by T is for display. Fitting a free temperature exponent broadens the NMR activation uncertainties substantially (about 0.52D, 0.14D, and 0.46D at the three fillings). These slopes are therefore not inserted directly as exchange couplings.',True)
para('Each STS trace has an independent scale. Low-T bias zero is the gap midpoint; only at half filling is it specified to equal μ. Doped spectral comparisons include a free offset between those origins. The high-T trace uses μ as zero and is thermally deconvolved.',True)

page('Direct single-orbital electron spectra','8- and 10-site square tori; physical canonical electron sectors and Lanczos spectral measures')
fig('figures/hubbard_ed_sts.png',maxheight=318)
table([['Cluster','Repulsive U/D for gap 8.002D','Attractive U/D for same gap'],
       ['8 sites','11.750 ± 0.013','−11.119 ± 0.013'],
       ['10 sites','11.494 ± 0.013','−11.452 ± 0.013']], [90,210,BW-300])
para('The quoted U errors propagate only the conditional ±0.011D gap error with t and t′ held fixed. The 8-to-10-site shifts, 0.257D and 0.333D, are much larger. They are not a calibrated systematic error bar. At U = 0, the 10-site cluster already has a 1.994D shell gap, whereas the 8-site cluster is open-shell. No bulk U estimate should be quoted with a ±0.013D uncertainty from this exercise.')
para('The six STS comparisons have normalized RMS residuals of 0.151–0.195, even with free amplitude, background, broadening, and doped origin offsets. They do not reproduce the data. The 10-site repulsive charge-gap match has a spin-sector gap of only 0.191D; the attractive match has 7.871D. Neither number is automatically the measured NMR activation.')
para('Largest canonical electronic sector: C(10,5)² = 63,504 states. The clean spectral weights satisfy positivity, normalization, filling, and the exact first two moments. A noninteracting spectral check agrees with the exact discrete DOS within 7.1 × 10⁻¹⁴. The mismatch is not explained by a fermion-sign or hole-energy-reference error.',True)

page('Actual dynamical-spin benchmark','Same repulsive U = 11.493525D; controlled as a strong-coupling spin-sector diagnostic')
fig('response_spin_dynamics.png',maxheight=225)
para('The projected Hamiltonian is Hₛ = J₁ΣNN Sᵢ·Sⱼ + J₂ΣNNN Sᵢ·Sⱼ, with J₁ = 4t²/U = 0.345984D and J₂ = 4t′²/U = 0.013280D. All 1,024 states of the 10-spin torus are diagonalized. Every local Sᵢ⁺ matrix element is included, with Boltzmann weights and averaging over sites.')
formula('spin_lehmann.png',[r'$S^{+-}_{\mathrm{loc}}(\omega)=\frac{1}{NZ}\sum_{i,a,b}e^{-E_a/T}|\langle b|S_i^+|a\rangle|^2\,\delta(\omega-E_b+E_a).$'],14)
para('For a contact hyperfine form factor, R is proportional to S_loc(ωN), so the displayed R/T is proportional to S_loc(ωN)/T. At T = 0.4472D, after normalization at 4D, the three broadenings give 6.734, 6.869, and 6.809. The measured value is 3.401 × 10⁻⁵. The finite-cluster spin gap is 0.28952D, and even a free overall amplitude gives χ² ≈ 244 for 17 degrees of freedom.')
para('The integrated local spectral sum is 1/2, verified to floating-point accuracy. Lorentzian tails generate artificial low-frequency subgap weight, so a separate exact-degenerate-weight diagnostic was also evaluated. Matching its temperature shape requires J₁ = 8.278D, with a conditional 68% interval [8.071, 8.490]D: about 24 times the Hubbard exchange. This is a shape diagnostic, not an inferred physical exchange or a finite relaxation rate.')
sub('What this test does and does not establish')
para('It demonstrates a severe scale and temperature-trend problem for this strong-coupling Hubbard benchmark. It does not establish a universal no-go theorem. The spin projection omits charge excitations; normalization at 4D is not deep in T ≪ U. A finite isolated cluster has discrete lines, not a bulk nuclear relaxation rate, and the hyperfine form factor has not been supplied.')

page('Physical-current transport benchmark','3 × 2 open square patch; six electrons; all 924 states and spin sectors')
fig('transport_kubo.png',maxheight=230)
formula('current_kubo.png',[
 r'$j_x=i\sum_{ij,\sigma}t_{ij}(x_i-x_j)(c^\dagger_{i\sigma}c_{j\sigma}-c^\dagger_{j\sigma}c_{i\sigma})=i[H,X],$',
 r'$\mathrm{Re}\,\sigma_{xx}^{\mathrm{reg}}(\omega)=\frac{\pi}{N}\sum_{a,b}\frac{p_a-p_b}{E_b-E_a}|\langle b|j_x|a\rangle|^2\delta(\omega-E_b+E_a).$'
 ],13)
para('The current sum counts each hopping bond once. The current, diamagnetic term, and every finite-temperature Lehmann transition are evaluated using the same t, t′, and U as the repulsive charge-gap match. The current independently agrees with i[H,X]. Static diamagnetic-paramagnetic cancellation on the open cluster has residual 4.65 × 10⁻¹⁶; the optical sum rule agrees to 8.34 × 10⁻¹⁶.')
para('At T = 0.45D, inverse broadened conductivity normalized at 4D ranges from 6.663 to 14.601 as η varies from 0.8D to 0.025D. The measured normalized resistivity is 1610.36. More fundamentally, σ(0;η) is proportional to η as η approaches zero: the apparent DC value is a Lorentzian-tail artifact.')
para('<b>This calculation does not supply bulk DC resistivity.</b> It shows explicitly why an STS charge gap, or an activated carrier-count formula, cannot replace a current-current response calculation. A thermodynamic limit and a justified relaxation mechanism are required before fitting transport coefficients. The open-cluster result is not an unconditional rejection of bulk Hubbard transport.')

page('Additional constraints and failed extensions','Restricted screens narrow the candidates; they do not rule out all single-orbital theories')
fig('response_stiffness_bounds.png',maxheight=260)
para('If the system is strictly two-dimensional, t and t′ above are the bare hopping, and interactions carry no additional charge current, the optical-sum/BKT bound optimized over all Pauli-allowed occupations gives Tᴮᴷᵀ ≤ 0.28481D at ν = 0.2. This is below the observed zero-resistance onset bracket. Interlayer coupling, a different bare band, or explicit charge-transferring interactions can invalidate those assumptions; the prompt does not exclude them. See Hazra, Verma and Randeria [1].')
para('An onsite-pair hopping P is a legitimate one-orbital term. A loose bound would require |P| ≳ 1.26D to bridge this discrepancy, but this is necessary only under the specified assumptions and is not sufficient. It is not a fitted P or an uncertainty interval.')
table([['Extension tested','Numerical outcome','Interpretation'],
 ['U, J₁, J₂ on 10 sites','Best proxy screen: U = −3.701D, J₁ = 4.418D, J₂ ≈ 0.','Only a restricted finite-cluster screen, not a response fit.'],
 ['Four proxy gaps','Calculated (8.040, 3.872, 2.603, 3.213)D vs targets (8, 5.54, 2.63, 1.75)D.','Wrong low-doping spin trend; RMS discrepancy 1.109D.'],
 ['Uniform-density stability','E(N) has negative pair-step curvature at N = 4, 6, 8.','Finite-cluster clustering warning; not a thermodynamic phase-separation proof.'],
 ['One-orbital pairing mean fields','d + id and s + id line-shape RMS ≈ 0.053 and 0.059 at nominal ν ≈ 0.3.','Number equations and common-coupling checks do not produce a successful joint model.']],[112,210,BW-322])

page('Phase information that is supported','A measured constraint map, not the uncomputed phase diagram of a fitted Hamiltonian')
fig('sts_empirical_phase_map.png',maxheight=355)
table([['Crystal','Low to high measured temperature','Unresolved identification'],
 ['ν = 1/2','Activated positive resistance down to 0.45D; low-T gapped STS and suppressed NMR.','T → 0 phase, spin order, topological order, and charge-carrier identity.'],
 ['ν ≈ 0.3','Zero resistance, onset bracket, then activated positive resistance.','Superconductivity is consistent; pairing symmetry and intervening phases are not fixed.'],
 ['ν ≈ 0.2','Zero resistance, onset bracket, then metallic temperature trend.','A coherence-like NMR enhancement is suggestive, not a symmetry determination.']],[65,224,BW-289])
para('No new/split diffraction peaks support the observed unchanged crystallographic cell. They do not justify assigning a unique electronic phase. There are no data at most fillings, and no justified interpolation of boundaries is available. In particular, the diagram is not reflected about ν = 1/2 when t′ ≠ 0. A microscopic phase diagram over 0 ≤ ν ≤ 1 remains uncomputed because no joint model has been validated.',True)

page('ARPES from the physical electron operator','Conditional reference only; the Hamiltonian has not passed the measured STS/NMR/transport tests')
fig('figures/hubbard_arpes_benchmark.png',maxheight=300)
para('The plotted quantity is A(k,ω), proportional to ARPES after division by the Fermi function only if the photoemission matrix element is taken constant. It comes from cₖ† and cₖ acting in the physical 10-site electron Fock space. The filling is exactly 0.5, 0.3, or 0.2 in these canonical calculations. Energy is measured from the canonical particle-addition/removal midgap chemical potential.')
para('The path is Γ = (0,0) → X = (1/2,0) → M = (1/2,1/2) → Γ. The plotted energy window is [−11D,11D]. At half filling the two separated groups are many-body removal/addition weight of one orbital. Doping transfers weight toward low energies and changes the chemical potential; it is not a rigid shift of a fitted two-band Hamiltonian. These features describe this reference calculation only.')
sub('Finite-momentum interpolation is an additional assumption')
para('The torus vectors are (3,1) and (−1,3), with ten allowed momenta Kⱼ = (j/10, −3j/10) modulo reciprocal lattice vectors. A continuous path cannot be exact on ten points. The figures use positive plane-wave projection weights |Σᵢ exp[2πi(k−K)·rᵢ]|²/N², averaged over rotated embeddings. Degenerate ground states are averaged over C₄ orientations. The weights sum to one, so positivity and spectral normalization are preserved.')
para('A 240-step Lanczos quadrature and η = 0.3D are used for display. The representative narrow-line convergence test is accurate at this width. Neither this projection nor the broadening is an uncertainty model for the material. X itself is not an exact allowed momentum on this torus. No superconducting coherence peaks or thermodynamic Fermi surface should be inferred from these finite-size images.',True)

page('Kramers-Kronig and zero-frequency zeros','Calculated from the physical half-filled Lehmann spectrum, with μ at its canonical gap midpoint')
formula('kk_zero.png',[
 r'$G(\mathbf{k},z)=\int_{-\infty}^{\infty}\!\frac{A(\mathbf{k},\omega^\prime)}{z-\omega^\prime}\,d\omega^\prime=\sum_a\frac{Z_{a\mathbf{k}}}{z-E_{a\mathbf{k}}},$',
 r'$\mathrm{Re}\,G(\mathbf{k},0)=-\mathcal{P}\!\int\frac{A(\mathbf{k},\omega)}{\omega}\,d\omega=-\sum_a\frac{Z_{a\mathbf{k}}}{E_{a\mathbf{k}}}.$'
 ],14)
fig('figures/hubbard_zero_embedding.png',maxheight=260)
para('The zero calculation uses the clean pole weights, not a truncated-window Hilbert transform of a broadened color map. At the four inequivalent allowed momenta, G(0) = (0.08848864, 0.05772089, −0.04850275, −0.12423947)D⁻¹. The 200-to-400-step change is below 10⁻¹⁶D⁻¹, and independent linear-system resolvents agree within 1.3 × 10⁻¹⁵D⁻¹.')
para('The two continuous projections shown agree at every exact cluster momentum. Moving one site representative by a torus period changes the interpolation and yields Γ-connected fractions 0.5174 and 0.5244 on a 241² grid. These are close to the nominal ν = 0.5, but they are <b>finite-cluster interpolation results, not the requested material area or its uncertainty</b>. The spread is not an exhaustive systematic-error estimate.')
para('A zero of the normal component in a paired state also need not be a zero eigenvalue of the full Nambu Green matrix. Multiple spectral poles, scalar zeros, and an enlarged physical orbital Hilbert space are distinct concepts. No Luttinger-volume equality is imposed as a fitting constraint.',True)

page('Why local STS does not fix the zero curve','An exact one-physical-orbital illustration; no agreement with NMR or transport is asserted')
formula('hk_model.png',[
 r'$H_{\mathrm{HK}}=\sum_{\mathbf{k}\sigma}(\epsilon_{\mathbf{k}}-\mu)n_{\mathbf{k}\sigma}+U\sum_{\mathbf{k}}n_{\mathbf{k}\uparrow}n_{\mathbf{k}\downarrow},$',
 r'$G(\mathbf{k},z)=\frac{1/2}{z-\bar\epsilon_{\mathbf{k}}+U/2}+\frac{1/2}{z-\bar\epsilon_{\mathbf{k}}-U/2},\qquad\bar\epsilon_{\mathbf{k}}=\epsilon_{\mathbf{k}}+4t^\prime.$'
 ],14)
fig('sts_local_inverse_example.png',maxheight=235)
para('The two illustrative Hamiltonians use t = +1D or −1D, t′ = 0.2D, and U = 12D. They are spinful single-orbital models with an interaction local in momentum and long-ranged in real space. The displayed Green function is spin-averaged in a paramagnetic ensemble. At half filling μ is chosen at the gap midpoint. Reversing t gives the unitary momentum relabeling k → k + (1/2,1/2), leaving the local spectrum identical. This illustrates missing momentum assignment, not distinct thermodynamic phases.')
para('Nevertheless, the sides of the zero contours containing Γ occupy 0.31170773 and 0.68829227 of the Brillouin zone on a 768² grid. Both have filling 0.5. The relabeling changes which side contains Γ; the total positive-sign volume of G is unchanged. Thus local spectral information plus a frequency Kramers-Kronig transform does not identify the requested Γ-side area. These are illustrative calculations, not estimates for the supplied crystal.')
para('The model is used only for this exact spectral counterexample [3]. Its long-range interaction and response subtleties mean it cannot be promoted to an oxide theory without independent dynamical-spin and transport calculations. Neither spin degeneracy alone nor the two-pole form is treated as a computed NMR result.')

page('What is resolved and what remains open','This is a corrected research result, not a claimed completion of the microscopic inverse problem')
table([['Requested item','Status'],
 ['Physical single-orbital Hamiltonian','Explicit candidate family and operators written; actual physical-Hilbert-space calculations performed.'],
 ['All coefficients with uncertainties','Not identified. Empirical scales and conditional finite-cluster gap-matching errors are provided, with model and size limitations.'],
 ['Joint STS, NMR, transport explanation','Not achieved by the tested candidates. Independent actual spectral, spin, and current responses reveal the problems.'],
 ['Full phase diagram','Not established. The figure gives measured constraints only, with unknown regions shown.'],
 ['Three ARPES density plots','Computed for the specified Hubbard benchmark; not validated material predictions.'],
 ['Green-function reconstruction and zeros','Computed from clean physical Lehmann poles; continuous zero area remains approximation-dependent and not inferred for the material.']],[171,BW-171])
para('The supplied observations are informative but do not specify interaction range, interlayer coupling, bare hopping, hyperfine form factor, current relaxation, or doped chemical-potential offsets. A defensible next microscopic calculation needs a physically motivated restriction on those choices and a forward method that tests all three responses. Adding enough adjustable terms could fit selected curves, but would not make their values or the unmeasured phases identifiable.')
para('No result here establishes that a successful one-orbital theory is impossible. Equally, the reference plots and narrow conditional error bars must not be represented as that successful theory. The earlier auxiliary-model phase diagram, ARPES predictions, and zero-area claim should not be used as a solution to the prompt.')
sub('Reproducibility and verification')
para('The accompanying archive includes unchanged source files, physical-model solvers, numerical spectra, empirical covariance/bootstrap records, model screens, figures, and audits. Key checks include exact two-site spectra, noninteracting dispersion/DOS, independent ground-state starts, spectral moments and filling, spin sum rules, current-commutator identity, optical sum rule, and independent zero-frequency resolvents. Report layout and plotted figures were also visually inspected.',True)
sub('Selected primary references')
para('[1] T. Hazra, N. Verma, M. Randeria, Phys. Rev. X 9, 031049 (2019). Stiffness and transition-temperature bounds. <link href="https://arxiv.org/abs/1811.12428" color="#254d70">arXiv:1811.12428</link><br/>[2] Y. M. Vilk, A.-M. S. Tremblay, J. Phys. I France 7, 1309 (1997). Hubbard conservation laws and spectral moments. <link href="https://arxiv.org/abs/cond-mat/9702188" color="#254d70">cond-mat/9702188</link><br/>[3] Y. Hatsugai, M. Kohmoto, J. Phys. Soc. Jpn. 61, 2056 (1992). Exact momentum-local interaction model. <link href="https://doi.org/10.1143/JPSJ.61.2056" color="#254d70">doi:10.1143/JPSJ.61.2056</link>',True)
endpage();C.save()
(ROOT/'data/report_layout_check.json').write_text(json.dumps({'pages':PAGE,'layout':LOG,'pdf_bytes':PDF.stat().st_size},indent=2))
print(PDF,PDF.stat().st_size,'bytes',PAGE,'pages')
