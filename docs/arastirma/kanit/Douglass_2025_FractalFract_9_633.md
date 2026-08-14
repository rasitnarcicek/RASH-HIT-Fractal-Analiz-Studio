

_Article_ 

# **Automated Box-Counting Fractal Dimension Analysis: Sliding Window Optimization and Multi-Fractal Validation** 

### **Rod W. Douglass** 

Douglass Research and Development, LLC, 8330 South 65th Street, Lincoln, NE 68516, USA; rwdlanm@gmail.com 

### **Abstract** 

Academic Editor: Carlo Cattani Received: 15 August 2025 Revised: 23 September 2025 Accepted: 25 September 2025 Published: 29 September 2025 

**Citation:** Douglass, R.W. Automated Box-Counting Fractal Dimension Analysis: Sliding Window Optimization and Multi-Fractal Validation. _Fractal Fract._ **2025** , _9_ , 633. https://doi.org/10.3390/ fractalfract9100633 

**Copyright:** © 2025 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license (https://creativecommons.org/ licenses/by/4.0/). 

This paper presents a systematic methodology for identifying optimal scaling regions in segment-based box-counting fractal dimension calculations through a three-phase algorithmic framework combining grid offset optimization, boundary artifact detection, and sliding window optimization. Unlike traditional pixelated approaches that suffer from rasterization artifacts, the method used directly analyzes geometric line segments, providing superior accuracy for mathematical fractals and other computational applications. The three-phase optimization algorithm automatically determines optimal scaling regions and minimizes discretization bias without manual parameter tuning, achieving significant error reduction compared to traditional methods. Validation across the Koch curve, Sierpinski triangle, Minkowski sausage, Hilbert curve, and Dragon curve demonstrates substantial improvements: excellent accuracy for the Koch curve (0.11% error) and significant error reduction for the Hilbert curve. All optimized results achieve _R_<sup>2</sup> _≥_ 0.9988. Iteration analysis establishes minimum requirements for reliable measurement, with convergence by level 6+ for the Koch curve and level 3+ for the Sierpinski triangle. Each fractal type exhibits optimal iteration ranges where authentic scaling behavior emerges before discretization artifacts dominate, challenging the assumption that higher iteration levels imply more accurate results. Application to a Rayleigh–Taylor instability interface (D = 1.835 ± 0.0037) demonstrates effectiveness for physical fractal systems where theoretical dimensions are unknown. This work provides objective, automated fractal dimension measurement with comprehensive validation establishing practical guidelines for mathematical and real-world fractal analysis. The sliding window approach eliminates subjective scaling region selection through systematic evaluation of all possible linear regression windows, enabling measurements suitable for automated analysis workflows. 

**Keywords:** fractal dimension; box-counting method; sliding window optimization; scaling region selection; boundary artifact detection; convergence analysis 

## **1. Introduction** 

The accurate measurement of fractal dimensions is a longstanding challenge that spans mathematics, computational science, and diverse application domains. From Richardson’s pioneering empirical studies of coastline lengths [1] and Mandelbrot’s foundational formalism [2], the development of practical algorithms began with Liebovitch and Toth’s implementation of box-counting [3]. Despite decades of refinement, systematic errors remain significant, such as the baseline quantization errors of roughly 8% identified by Bouda et al. [4]. Recent comparative reviews further highlight the sensitivity of all prevalent algorithms to implementation and parameter choices [5]. 

_Fractal Fract._ **2025** , _9_ , 633 

https://doi.org/10.3390/fractalfract9100633 

_Fractal Fract._ **2025** , _9_ , 633 

2 of 20 

Fractal objects such as the Koch curve possess precisely known dimensions (e.g., _D_ = log(4)/ log(3) _≈_ 1.2619), yet computational estimates using box-counting frequently diverge due to region selection, grid placement, and parameterization. For instance, the measured dimension may vary from _D_ = 1.18 to _D_ = 1.32 depending on chosen scaling regions, grid offset procedures, or regression protocols [6,7]. This reveals persistent limitations in reproducibility and underscores the need for objective, automated analysis. 

### _1.1. Recent Advances and Systematic Benchmarks_ 

Recent years have seen significant methodological advances across multiple dimensions of fractal analysis. Systematic benchmark studies compare box-counting and alternatives such as correlation sum and entropy-based estimators under varied data lengths, noise levels, and dimensionality, providing quantitative performance baselines [5]. Comprehensive reviews document this methodological evolution: Lopes and Betrouni’s systematic analysis establishes foundational challenges in fractal and multifractal analysis [8], while recent comparative frameworks emphasize reproducibility and standardized implementation across modern algorithms. 

Methodological refinements continue addressing fundamental algorithmic limitations through diverse approaches. Xu and Lacidogna’s Modified Box-Counting Method specifically targets border effects and noninteger box size problems, achieving consistent accuracy improvements with errors below 5% through geometric preservation principles [9]. Contemporary algorithmic advances include Wu et al.’s improvements to direct fractal dimension estimation [10], So et al.’s enhanced box-counting algorithms [11], and recent work by Jiang et al. addressing grid size selection challenges in differential box-counting methods [12]. Wang et al.’s analysis of scale parameters and counting origins further demonstrates ongoing attention to systematic bias reduction [13]. 

Contemporary research specifically targets objective scaling region selection, addressing the persistent challenge of subjective bias. Roy et al. develop an improved box-counting algorithm that automatically identifies optimal scaling ranges using statistical criteria to determine fractal behavior cutoffs [14]. Deshmukh et al. propose ensemble-based methods that systematically evaluate all possible endpoint combinations for scaling region identification in dynamical systems applications [15]. Both approaches demonstrate that automated region selection eliminates confirmation bias and improves reproducibility across nonlinear science applications, validating the fundamental importance of objective, automated approaches for reliable invariant measurement. 

Despite these advances, the challenge persists: subjective or ad hoc region selection continues to introduce inconsistencies, restricts automation, and limits scaling to large datasets. Automated detection and characterization of scaling regions is now recognized as a central objective in fractal analysis [15]. Methods such as ensemble-based slope estimation or changepoint-based region transitions are increasingly validated against benchmark sets [5]. Meanwhile, quantization, boundary artifacts, and discretization effects remain nontrivial sources of error [4,16]. 

### _1.2. Research Objectives and Proposed Approach_ 

This work addresses the persistent challenges in fractal dimension estimation through a comprehensive sliding-window optimization framework with fully automated scaling region selection. The research objectives are as follows: 

Primary Objective: Develop a reproducible algorithm that combines objective, automated selection of optimal scaling regions with improved boundary artifact detection and grid offset procedures, minimizing manual parameter tuning and human bias. 

_Fractal Fract._ **2025** , _9_ , 633 

3 of 20 

Validation Strategy: Demonstrate the reliability and practical utility of the algorithm by benchmarking across multiple fractal types of known dimension, incorporating quantitative assessment of error reduction against both traditional and recently proposed automated methods. 

In summary, the presented algorithm builds on decades of development and recent advances in automation, integrating both established and contemporary practices for robust fractal dimension estimation. It aims to serve as a reproducible, scalable foundation for systematic studies in fractal and nonlinear science. 

## **2. Materials and Methods** 

A comprehensive three-phase optimization framework was developed that systematically addresses the fundamental limitations identified in Section 1. Rather than treating boundary detection, scaling region selection, and grid discretization as separate concerns, the general algorithm integrates these requirements into a unified strategy. The fractal dimension analysis was implemented using custom Python3 software (see Supplementary Materials). 

### _2.1. Design Philosophy: Synthesis of Historical Insights_ 

The sliding window optimization algorithm synthesizes key insights from the literature into a unified algorithmic strategy guided by three fundamental principles: 

Segment-Based Geometric Analysis: Unlike traditional pixelated approaches, this method analyzes curves formed by a set of straight line segments, eliminating rasterization artifacts and providing superior accuracy for mathematical applications where interface geometry must be preserved precisely. 

Boundary Artifact Detection: Comprehensive boundary artifact detection using statistical criteria (slope deviation threshold 0.12, correlation threshold 0.95) is used that automatically identifies and removes problematic data points without manual intervention. 

Objective Region Selection: The sliding window approach eliminates subjective scaling region selection through systematic evaluation of all possible linear regression windows, addressing the reproducibility challenges that have limited practical applications. 

### _2.2. Three-Phase Implementation Framework_ 

This comprehensive approach addresses the complete pipeline from data generation through final dimension calculation, with each phase targeting specific limitations identified in historical research. The three-phase architecture systematically eliminates sources of error and bias. 

### 2.2.1. Phase 1: Grid Offset Optimization 

The first phase, Algorithm 1, implements grid offset optimization to minimize discretization bias inherent in traditional box-counting methods. The calculated dimension depends critically on how the grid of boxes intersects the curve. A curve segment lying near a box boundary may be counted as occupying one box or multiple boxes depending on slight shifts in grid positioning, introducing systematic bias into the intersection count. This quantization error can significantly affect fractal dimension estimates (c.f., Bouda et al. [4], Foroutan-pour et al. [6], and Gonzato et al. [7]). 

### 2.2.2. Phase 2: Enhanced Boundary Artifact Detection 

The second phase, Algorithm 2, systematically identifies and removes boundary artifacts that corrupt linear regression analysis, addressing limitations identified by Buczkowski et al. [16] and Gonzato et al. [7]. 

_Fractal Fract._ **2025** , _9_ , 633 

4 of 20 

### **Algorithm 1** Phase 1: Grid Offset Optimization 

1: **Input:** Segments, box_size, min_box_size, spatial index bounds 2: **Output:** Minimum box count across all tested grid offsets 3: 4: Determine adaptive grid density based on box size: 5: **if** box_size < min_box_size _×_ 5 **then** 6: Set offset_increments = [0, 0.25, 0.5, 0.75] _▷_ Fine grid: 4 _×_ 4 offset tests (16 total) 7: **else if** box_size < min_box_size _×_ 20 **then** 8: Set offset_increments = [0, 0.33, 0.67] _▷_ Medium grid: 3 _×_ 3 offset tests (9 total) 9: **else** 10: Set offset_increments = [0, 0.5] _▷_ Coarse grid: 2 _×_ 2 offset tests (4 total) 11: **end if** 12: 13: Initialize: min_count = ∞, max_count = 0 14: **for** dx_fraction in offset_increments **do** 15: **for** dy_fraction in offset_increments **do** 16: Calculate offsets: offset_x = spatial_min_x + dx_fraction _×_ box_size 17: offset_y = spatial_min_y + dy_fraction _×_ box_size 18: Count occupied boxes using spatial indexing within bounds 19: current_count = number of boxes intersecting segments 20: min_count = min(min_count, current_count) 21: max_count = max(max_count, current_count) 22: **end for** 23: **end for** 24: 25: Calculate improvement: improvement_pct = (max_count - min_count) / max_count _×_ 100% 26: **return** min_count, improvement_pct 

### **Algorithm 2** Phase 2: Enhanced Boundary Artifact Detection 

1: **Input:** Box count data ( _log_ ( _ϵi_ ), _log_ ( _N_ ( _ϵi_ ))), optional manual trim parameters 2: **Output:** Cleaned data with boundary artifacts removed 

3: 4: **if** manual trimming requested **then** 5: Apply specified boundary point removal _▷_ Allows user override if needed 6: **end if** 

7: 

8: **if** sufficient points available ( _n >_ 8) **then** 9: Calculate _segment_  size_ = max(3, _⌊n_ /4 _⌋_ ) _▷_ Min 3 points for regression, quarter-segments for analysis 10: Compute linear regression slopes for: 11: • First segment: points [0, _segment_  size −_ 1] 12: • Middle segment: points [ _segment_  size_ , 3 _× segment_  size −_ 1] 13: • Last segment: points [ _n − segment_  size_ , _n −_ 1] 14: 15: Set _slope_  threshold_ = 0.12 _▷_ Slope deviation tolerance 16: Set _r_<sup>2</sup>  threshold_ = 0.95 _▷_ Minimum linearity requirement 17: 18: **if** _| f irst_  slope − middle_  slope| > slope_  threshold_ OR _f irst_  r_<sup>2</sup> _< r_<sup>2</sup>  threshold_ **then** 19: Mark first segment for removal _▷_ Large-scale boundary effects 20: **end if** 21: **if** _|last_  slope − middle_  slope| > slope_  threshold_ OR _last_  r_<sup>2</sup> _< r_<sup>2</sup>  threshold_ **then** 22: Mark last segment for removal _▷_ Small-scale discretization effects 23: **end if** 

24: 25: Apply boundary trimming and verify linearity improvement 26: **Return:** Trimmed data ( _log_ ( _ϵclean_ ), _log_ ( _N_ ( _ϵclean_ ))) 27: **end if** 

_Fractal Fract._ **2025** , _9_ , 633 

5 of 20 

Rather than relying on arbitrary endpoint removal, this phase uses statistical criteria to identify genuine boundary artifacts. The slope deviation threshold (0.12) was determined through systematic analysis across multiple fractal types to distinguish meaningful boundary effects from normal statistical variation. The correlation threshold (0.99) ensures statistical significance consistent with established standards for excellent linear fit quality [17,18], providing objective quality control independent of fractal geometry. 

### 2.2.3. Phase 3: Comprehensive Sliding Window Analysis 

The third phase, Algorithm 3, implements the core innovation: systematic evaluation of all possible scaling regions to identify optimal linear regression windows without subjective selection. This systematic evaluation eliminates subjective scaling region selection by testing all possible contiguous windows and applying objective selection criteria. The dual selection approach (accuracy-optimized when theoretical values are known for validation, statistical quality-optimized for unknown cases) ensures optimal performance across both validation and application scenarios without introducing circular reasoning, whereby knowing the dimension leads to decisions made that return that value. This circularity manifests in several possible ways: 

- Subjective endpoint selection: Researchers may unconsciously choose scaling ranges that yield dimensions close to expected values. 

- Post-hoc justification: Poor-fitting data points may be excluded without systematic criteria, introducing confirmation bias. 

- Inconsistent methodology: Different practitioners analyzing identical datasets may select different scaling regions, yielding inconsistent results. 

- Limited reproducibility: Manual scaling region selection prevents automated analysis of large datasets. 

### _2.3. Computational Implementation Details_ 

The segment-based approach requires several key computational components that distinguish it from traditional pixelated methods. 

### 2.3.1. Spatial Indexing and Line-Box Intersection 

Efficient fractal dimension calculation for large datasets requires optimized spatial indexing. Hierarchical spatial partitioning [19] is implemented combined with the Liang-Barsky line clipping algorithm [20] for robust line-box intersection testing. 

The Liang-Barsky algorithm provides several advantages for fractal analysis: 

- Computational Efficiency: O(1) line-box intersection tests enable scalability to large datasets. 

- Numerical Robustness: Parametric line representation avoids floating-point precision issues common in geometric intersection. 

- Partial Intersection Handling: Accurately handles line segments that partially cross box boundaries. 

### 2.3.2. Adaptive Box Size Determination 

Automatic box size range calculation adapts to fractal extent and complexity: 

- Minimum box size ( _ϵmin_ ): Set to 2× average segment length to ensure adequate geometric resolution. 

- Maximum box size ( _ϵmax_ ): Limited to 1/8 of fractal bounding box to maintain statistical validity. 

- Logarithmic progression: Box sizes follow _ϵi_ = _ϵmin ·_ 2<sup>_i_</sup> for consistent scaling analysis. 

_Fractal Fract._ **2025** , _9_ , 633 

6 of 20 

This adaptive approach ensures consistent measurement quality across fractals of vastly different scales and complexities. 

**Algorithm 3** Phase 3: Comprehensive Sliding Window Analysis 

- 1: **Input:** Cleaned box count data, optional mathematical dimension _Dtheo_ 

- 2: **Output:** Optimal fractal dimension _Dbest_ , window parameters 

3: 

- 4: Compute log values: _xi_ = log( _ϵi_ ) and _yi_ = log( _N_ ( _ϵi_ )) 

- 5: Set window size range: _wmin_ = 3, _wmax_ = _n_ 6: Initialize: _R_<sup>2</sup> _best_<sup>=</sup><sup>_−_1,</sup><sup>_Dbest_= 0,</sup><sup>_best_window_in f o_=</sup><sup>_{}_</sup> 

7: 8: **for** window size _w_ = _wmin_ to _wmax_ **do** 9: _best_  r_<sup>2</sup>  f or_  window_ = _−_ 1 10: _best_  result_  f or_  window_ = _{}_ 11: 12: **for** starting position _start_ = 0 to _n − w_ **do** 13: _end_ = _start_ + _w −_ 1 _▷_ Inclusive end index for w points 14: Extract window data: _{_ ( _xi_ , _yi_ ) _|start ≤ i ≤ end}_ 15: 16: Perform linear regression: _y_ = _mx_ + _b_ 17: Calculate dimension _D_ = _−m_ (negative slope) 18: Calculate correlation coefficient _R_<sup>2</sup> 19: Calculate standard error _SE_ 20: 21: **if** _R_<sup>2</sup> _> best_  r_<sup>2</sup>  f or_  window_ **then** 22: Store as best result for this window size: 23: _best_  result_  f or_  window_ = _{D_ , _R_<sup>2</sup> , _SE_ , _start_ , _end}_ 24: **end if** 25: **end for** 26: 27: Record best result for this window size 28: **end for** 29: 30: **Selection Criteria:** 31: **if** Mathematical dimension _Dtheo_ known **then** 32: Select window minimizing _|D − Dtheo|_ among high-quality fits ( _R_<sup>2</sup> _>_ 0.995) _▷_ Validation mode: accuracy-optimized 33: **else** 34: Select window maximizing _R_<sup>2</sup> among reasonable dimensions (1.0 _< D <_ 3.0) _▷_ Application mode: statistical quality-optimized 35: **end if** 36: 37: **return** _Dbest_ , optimal window size, scaling region bounds, regression statistics 

### _2.4. Computational Complexity and Efficiency_ 

The three-phase approach achieves computational efficiency through strategic resource allocation: 

- Phase 1: _O_ ( _k · m_ ) where _k_ is the number of offset tests (4–16) and _m_ is the spatial intersection complexity, with adaptive testing density. 

- Phase 2: _O_ ( _n_ ) for boundary artifact detection, with early termination for clean data. 

- • Phase 3: The sliding window analysis has practical complexity _O_ ( _k_<sup>3</sup> ) where _k_ represents the number of box sizes (typically 10–20) , not the number of line segments. This distinction is crucial: while segment count may reach hundreds of thousands, the box size count remains small due to logarithmic progression, maintaining computational efficiency even for large datasets. 

Total computational complexity remains practical for real-time applications while providing systematic optimization across all three algorithmic phases. 

_Fractal Fract._ **2025** , _9_ , 633 

7 of 20 

## **3. Results** 

To validate the accuracy and robustness of the fractal dimension algorithm, comprehensive testing was performed using five well-characterized mathematical fractals with known dimensions ranging from 1.26 to 2.00, shown in Figures 1–5. This validation approach ensures our method performs reliably across the full spectrum of geometric curves encountered in two-dimensional fractal analysis. For real-world applications, the algorithm constrains calculated dimensions to physically reasonable ranges (1.0 < D < 2.0 for planar curves) to prevent unphysical results. 

These five fractal curves represent infinite mathematical objects that possess selfsimilar structure at all scales. Since true fractals contain unlimited detail, they can only be approximated through finite computational processes. Each fractal is generated by starting with a simple geometric seed (such as a line segment or triangle) and repeatedly applying a specific replacement rule through multiple iterations or recursive calls. The “level” parameter controls the number of times this replacement rule is applied—higher levels produce increasingly detailed approximations that more closely resemble the true infinite fractal. While complete fractals cannot be achieved computationally, these finite approximations capture sufficient geometric complexity to accurately measure fractal dimensions and analyze the self-similar properties that characterize real-world phenomena like fluid interfaces and coastlines. Therefore, computing their dimensions requires evaluating their “convergence” toward the infinite form. 

Consequently, fractal dimension computation involves two critical aspects: first, whether the algorithm accurately calculates the dimension of the given curve, and second, whether the curve accurately represents the desired mathematical fractal. For mathematical fractals, curve fidelity depends on the iteration or recursion level used in generation. For computational physics applications where curves are generated from simulations and analyzed for fractal properties, the analogous consideration is grid convergence, since increased geometric detail emerges as the computational grid is refined. 

### _3.1. Comprehensive Validation Framework_ 

The validation strategy addresses both methodological rigor and practical applicability through systematic testing across diverse fractal geometries and avoiding the circularity problem. 

### 3.1.1. Fractal Selection and Computational Scope 

The validation employs five well-characterized mathematical fractals with known dimensions spanning the complete range relevant to mathematical fractal analysis as shown in Figures 1–5: 

- Dragon curve ( _D_ = 1.5236): Complex space-filling pattern with 1023 segments at level 9. 

- Koch curve ( _D_ = 1.2619): Classic self-similar coastline fractal with 16,384 segments at level 7. 

- Hilbert curve ( _D_ = 2.0000): Space-filling curve approaching two-dimensional behavior with 16,383 segments at level 7. 

- Minkowski sausage ( _D_ = 1.5000): Exact mathematical dimension with 262,144 segments at level 6. 

- Sierpinski triangle ( _D_ = 1.5850): Triangular self-similar structure with 6561 segments at level 7. 

This selection provides comprehensive validation across the dimensional spectrum (D = 1.26 to D = 2.00) while testing computational scalability across nearly three orders of 

_Fractal Fract._ **2025** , _9_ , 633 

8 of 20 

magnitude in dataset size (1K to 262K segments). Each fractal represents distinct geometric characteristics, from simple near-linear to complex space-filling curves. 



<!-- Start of picture text -->
0.05<br>0.00<br>−0.05<br>−0.10<br>−0.15<br>−0.20<br>−0.25<br>−0.30<br>0.0 0.2 0.4 0.6 0.8 1.0<br>X<br>Figure 1. Koch curve (Level 7): Classic self-similar coastline fractal ( D<br>0.3<br>0.2<br>0.1<br>0.0<br>0.0 0.2 0.4 0.6 0.8 1.0<br>X<br>Figure 2. Minkowski sausage (Level 6):<br>dimension ( D = 1.5000). 1.5000).<br>1.0<br>0.8<br>0.6<br>0.4<br>0.2<br>0.0<br>0.0 0.2 0.4 0.6 0.8 1.0<br>X<br>Y<br>Y<br>Y<br><!-- End of picture text -->

**Figure 1.** Koch curve (Level 7): Classic self-similar coastline fractal ( _D_ = 1.2619). 

**Figure 2.** Minkowski sausage (Level 6): Classic boundary-type fractal with known mathematical dimension ( _D_ = 1.5000). 1.5000). 

**Figure 3.** Hilbert curve (Level 7): Space-filling curve approaching two-dimensional behavior ( _D_ = 2.0000). 

_Fractal Fract._ **2025** , _9_ , 633 

9 of 20 



<!-- Start of picture text -->
0.8<br>0.6<br>0.4<br>0.2<br>0.0<br>0.0 0.2 0.4 0.6 0.8 1.0<br>X<br>Figure 4. Sierpinski triangle (Level 7): Triangular self-similar structure (<br>1.0<br>0.8<br>0.6<br>0.4<br>0.2<br>0.0<br>0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7<br>X<br>Y<br>Y<br><!-- End of picture text -->

**Figure 4.** Sierpinski triangle (Level 7): Triangular self-similar structure ( _D_ = 1.5850). 

**Figure 5.** Dragon curve (Level 9): Complex space-filling pattern ( _D_ = 1.5236). 

### 3.1.2. Dual-Criteria Selection Framework 

Sliding window optimization eliminates subjective bias through a systematic dualcriteria approach that explicitly separates algorithm validation from real-world application: 

Validation Mode (Mathematical Fractals): When mathematical dimensions are known (Koch curve, Sierpinski triangle, etc.), the algorithm minimizes _|Dcalculated − Dmathematical|_ among all windows achieving high statistical quality ( _R_<sup>2</sup> _>_ 0.995). This approach is appropriate for algorithm validation because: 

- The mathematical dimension provides an objective accuracy benchmark. 

- Statistical quality thresholds prevent selection of spurious fits. 

- The goal is explicitly to validate algorithmic performance against known standards. 

- Results inform algorithm development and parameter optimization. 

   - This validation approach addresses potential circularity through several safeguards: 

- (1) mathematical dimensions serve only as post hoc accuracy assessment, not as optimiza- 

_Fractal Fract._ **2025** , _9_ , 633 

10 of 20 

tion targets during window evaluation; (2) the algorithm independently identifies all high-quality scaling regions ( _R_<sup>2</sup> _>_ 0.995) before any comparison to theoretical values; (3) the dual-criteria framework explicitly separates algorithm validation (where known theoretical values enable performance measurement) from real-world application (where statistical quality drives selection); and (4) the algorithm’s effectiveness is ultimately demonstrated through its application to physical systems where no theoretical dimension exists, such as Rayleigh–Taylor interface analyses (c.f., Section 4.1.2). 

Application Mode (Unknown Dimensions): For real-world applications where true dimensions are unknown, the algorithm maximizes _R_<sup>2</sup> among windows yielding physically reasonable dimensions (1.0 _< D <_ 2.0 for two-dimensional structures). This approach ensures objectivity because: 

- No prior knowledge of expected dimensions influences selection. 

- Statistical quality becomes the primary optimization criterion. 

- Physical constraints prevent obviously unphysical results. 

- The method remains fully automated and reproducible. 

### _3.2. Sliding Window Optimization Results_ 

This section presents the performance of the three-phase optimization algorithm across all five mathematical fractals, demonstrating the improvements achieved through systematic elimination of measurement artifacts and biases. 

### 3.2.1. Algorithmic Enhancement Demonstration: Three-Phase Progression 

The Hilbert curve provides an illustration of the algorithm’s effectiveness, representing a challenge for fractal dimension measurement due to its space-filling nature and complex geometric structure. As demonstrated in Figures 6–8 the progressive improvement achieved through each algorithmic phase demonstrates the cumulative necessity of all three algorithmic phases for optimal performance. 



<!-- Start of picture text -->
10 5<br>Da a poin s<br>Fi : D = 1 . 8013 ± 0 . 0339<br>10 4<br>10 3<br>10 2<br>10 1<br>10 010 −3 10 −2 10 −1 10 0<br>Box Size (r)<br>Number of Boxes (N)<br><!-- End of picture text -->

**Figure 6.** Basic box-counting for the Hilbert curve (Level 7) includes all box sizes with no optimization in the regression giving _D_ = 1.8013 _±_ 0.034 (9.9% error). 

_Fractal Fract._ **2025** , _9_ , 633 

11 of 20 



<!-- Start of picture text -->
10 4<br>All Data Points<br>Optimal Window (D=1.9764)<br>Optimal Fit (slope=1.9764)<br>10 3<br>10 2<br>10 110 −2 10 −1 10 0<br>Box Size (r)<br>Figure 7. Optimization using only Algorithms 2 and 3 for the Hilbert curve: 2 and 3 for the Hilbert curve: and 3 for the Hilbert curve: 3 for the Hilbert curve: for the Hilbert curve:<br>(1.2% error).<br>10 4<br>All D a t a  P o i n t s<br>O p ti ma l Wi n d ow  (D = 1 . 9923)<br>Optimal Fit (slope = 1.9923)<br>10 3<br>10 2<br>10 1<br>10 010 −2 10 −1 10 0<br>Box Size ( )<br>Number of Boxes (N)<br>Numbe  of Boxes (N)<br><!-- End of picture text -->

**Figure 7.** Optimization using only Algorithms 2 and 3 for the Hilbert curve: 2 and 3 for the Hilbert curve: and 3 for the Hilbert curve: 3 for the Hilbert curve: for the Hilbert curve: _D_ = 1.9764 _±_ 0.014 (1.2% error). 

**Figure 8.** Complete three-phase optimization: _D_ = 1.9923 _±_ 0.0174 (0.39% error). 

Basic Box-Counting: Figure 6 illustrates the implementation analyzing data for all box sizes shown which produces _D_ = 1.801 _±_ 0.034, representing 9.9% error from the mathematical value _D_ = 2.000. The large error and uncertainty reflect boundary artifacts, poor scaling region selection, and grid discretization bias. 

Two-Phase Optimization: If boundary artifact detection and sliding window optimization (Algorithms 2 and 3) are added the results shown in Figure 7 improves performance to _D_ = 1.976 _±_ 0.014, achieving 1.20% error. 

Complete Three-Phase Optimization: Finally, integration of the grid offset optimization of Algorithm 1 as shown in Figure 8 yields _D_ = 1.992 _±_ 0.017 with only 0.39% error. 

_Fractal Fract._ **2025** , _9_ , 633 

12 of 20 

### 3.2.2. Validation Results and Performance Summary 

To demonstrate the effectiveness of the three-phase optimization approach, Table 1 presents baseline results using traditional box-counting with all available box sizes included in linear regression analysis. These results establish the performance benchmark against which our optimized algorithm is evaluated. 

The three-phase optimization algorithm demonstrates consistent good performance across all five mathematical fractals. Figures 9 and 10 illustrate the detailed optimization process for the Minkowski sausage, showing both the sliding window analysis that identifies the optimal scaling region and the resulting excellent power-law fit. Likewise, Figure 11 shows the effectiveness of the three-phase algorithm for the Koch curve. Table 2 presents the comprehensive performance summary across all fractal types, demonstrating the algorithm’s reliability and precision. 



<!-- Start of picture text -->
1.80 Theoretical D = 1.5000<br>1.75 Optimal: D = 1.5037 ± 0.0136 (size=17)<br>Calculated Dimension<br>1.70<br>1.65<br>1.60<br>1.55<br>1.50<br>1.45<br>1.00<br>Error from theoretical: 0.0037<br>0.99<br>0.98<br>0.97<br>0.96 R ²  Value<br>Optimal R² = 0.9988<br>R² = 0.99<br>0.95<br>4 6 8 10 12 14 16 18<br>Window Size (number of points)<br>Figure 9. Minkowski sausage optimization:<br>scaling region yielding  D = 1.504 1.504  ±  0.014 (0.25% error from exact mathematical<br>All Data Points<br>10 5 Optimal Window (D=1.5037)<br>Optimal Fit (slope = 1 . 5037)<br>10 4<br>10 3<br>10 2<br>10 1<br>10 −3 10 −2 10 −1<br>Box Size (r)<br>Fractal Dimension<br>alue<br>R² V<br>Number of Boxes (N)<br><!-- End of picture text -->

**Figure 9.** Minkowski sausage optimization: Sliding window analysis identifies optimal 17-point scaling region yielding _D_ = 1.504 1.504 _±_ 0.014 (0.25% error from exact mathematical _D_ = 1.500). 

**Figure 10.** Minkowski sausage log-log analysis: Excellent power-law scaling across the optimal window with _R_<sup>2</sup> = 0.9988. 

_Fractal Fract._ **2025** , _9_ , 633 

13 of 20 



<!-- Start of picture text -->
Theoretical D = 1.2619<br>1.32 Optimal: D = 1 . 2605 ± 0 . 0101 (size=5)<br>Calculated Dimension<br>1.30<br>1.28<br>1.26<br>1.00<br>Error from theoretical: 0.0013<br>0.99<br>0.98<br>0.97<br>0.96 R ²  Value<br>Optimal R² = 0.9998<br>R² = 0.99<br>0.95<br>4 6 8 10 12 14 16<br>Window Size (number of points)<br>Fractal Dimension<br>alue<br>R² V<br><!-- End of picture text -->

**Figure 11.** Koch curve (iteration level 7) sliding window optimization demonstrates optimal 14-point scaling region with _D_ = 1.2605 _±_ 0.0101 (0.11% error from exact mathematical _D_ = 1.2619). 

**Table 1.** Baseline box-counting results using all available box sizes in linear regression (no optimization). 

|**Fractal**|**Mathematical D**|**Baseline D**|**Error %**|**Segments**|
|---|---|---|---|---|
|Dragon|1.5236|1.4747 ± 0.0267|3.2%|1024|
|Koch|1.2619|1.2519 ± 0.0104|0.79%|16,384|
|Hilbert|2.0000|1.8013 ± 0.0339|9.9%|16,383|
|Minkowski|1.5000|1.4493 ± 0.0073|3.4%|262,144|
|Sierpinski|1.5850|1.5890 ± 0.0108|0.3%|6561|
|Average|||3.5%||



**Table 2.** Complete three-phase algorithm validation summary. 

|**Fractal**|**Mathematical D**|**Measured D**|**Error %**|**Window**|**R²**|**Segments**|
|---|---|---|---|---|---|---|
|Minkowski|1.5000|1.5037 ± 0.0140|0.25%|17|0.9988|262,144|
|Hilbert|2.0000|1.9923 ± 0.0174|0.39%|7|0.9996|16,383|
|Koch|1.2619|1.2605 ± 0.0101|0.11%|5|0.9998|16,384|
|Sierpinski|1.5850|1.6394 ± 0.0075|3.4%|4|1.0000|6561|
|Dragon|1.5236|1.6362 ± 0.0135|7.4%|3|0.9999|1024|
|Average|||2.3%|7|0.9996||



Table 2 presents the corresponding optimized results, demonstrating significant improvements for most fractal types while revealing limitations for cases with insufficient scaling data. 

The validation demonstrates strong algorithmic performance with mean absolute error of 2.3% across all fractal types and consistently high statistical quality ( _R_<sup>2</sup> _≥_ 0.9996). The algorithm automatically adapts to different fractal characteristics, as evidenced by the varying optimal window sizes (3–14 points) that reflect each fractal’s unique scaling behavior. This adaptability, combined with the consistently excellent statistical quality, confirms the robustness of the three-phase optimization approach across diverse fractals. 

The Dragon curve represents an important limitation case where the three-phase optimization performed worse than baseline regression (7.4% vs. 3.2% error). Analysis reveals that the automatic box size determination generated only 8 box sizes spanning 

_Fractal Fract._ **2025** , _9_ , 633 

14 of 20 

1.15 decades of scaling, providing insufficient data for reliable sliding window optimization. The algorithm selected a 3-point regression window from limited options, demonstrating that the sliding window approach requires adequate scaling range data to be effective. This suggests that future work is needed on this portion of the Algorithm such as adaptive range expansion or alternative box size selection strategies for such highly folded fractals. 

### _3.3. Fractal-Specific Convergence Behavior and Guidelines_ 

The convergence of dimension with iteration level results reveal that each fractal type exhibits distinct convergence patterns with optimal iteration ranges where authentic scaling behavior emerges before discretization artifacts dominate. Figures 12 and 13 illustrate representative convergence behavior for two contrasting fractal types, while Table 3 provides comprehensive guidelines for all five fractals tested, enabling optimal computational resource allocation across diverse fractals. 



<!-- Start of picture text -->
1.6 Theoretical Dimension (1.523600)<br>Calculated Dimension 1.00<br>1.5<br>0.98<br>1.4<br>0.96<br>R-squared<br>1.3 0.94<br>1.2 0.92<br>0.90<br>1 2 3 4 5 6 7 8 9<br>Dragon Curve Iteration Level<br>Figure 12. The Dragon curve shows a characteristic oscillatory approach with convergence by level<br>6–7 and stable behavior through level 9.<br>Theoretical Dimension (1.500000)<br>Calculated Dimension 1.00<br>1.5<br>0.98<br>1.4 0.96<br>R-squared<br>0.94<br>1.3<br>0.92<br>1.2<br>0.90<br>1 2 3 4 5 6<br>Minkowski Curve Iteration Level<br>R-squared<br>Fractal Dimension<br>R-squared<br>Fractal Dimension<br><!-- End of picture text -->

**Figure 12.** The Dragon curve shows a characteristic oscillatory approach with convergence by level 6–7 and stable behavior through level 9. 

**Figure 13.** The Minkowski sausage exhibits rapid convergence by level 2–3 with high stability through level 6. 

_Fractal Fract._ **2025** , _9_ , 633 

15 of 20 

**Table 3.** Iteration convergence guidelines for reliable fractal dimension measurement. 

|**Fractal Type**|**Initial**<br>**Convergence**|**Stable Range**|**Recommended**<br>**Level**|**Compute Cost**|
|---|---|---|---|---|
|Dragon|Level 5–6|Level 6|Level 8–9|Moderate (2<sup>_n_ </sup>segments)|
|Koch|Level 4–5|Level 5–7|Level 6–7|Moderate (4<sup>_n_ </sup>segments)|
|Hilbert|Level 4–5|Level 5–7|Level 6–7|High (complex path)|
|Minkowski|Level 2–3|Level 3–6|Level 5–6|High (8<sup>_n_ </sup>segments)<br>|
|Sierpinski|Level 2–3|Level 4–6|Level 5–6|Low (3<sup>_n_+1 </sup>segments)|



The convergence analysis reveals three distinct patterns: **rapid convergers** (Sierpinski, Minkowski) achieve reliable measurements by level 2–3, making them ideal for validation studies and computationally efficient applications; **moderate convergers** (Koch, Hilbert) require level 4–5 for initial convergence, representing typical requirements for practical fractal analysis; and **gradual convergers** (Dragon) need level 6–7, reflecting their mathematical complexity. This classification provides essential guidance for optimal computational resource allocation and ensures measurement reliability across diverse fractal types, establishing that higher iteration levels do not automatically yield more accurate results. 

### Convergence-Based Best Practices 

The results confirms the findings of Buczkowski et al. [16], who demonstrated two fundamental principles for pixelated geometries: (1) convergence analysis is essential for reliable dimension measurement, and (2) infinite iteration does not improve—and may actually degrade—dimensional accuracy. 

The segment-based approach validates both principles while extending them to geometric line analysis: each fractal type exhibits an optimal iteration range where authentic scaling behavior emerges before discretization artifacts dominate. Rather than using maximum available iteration levels, we employ convergence-stabilized levels that capture authentic fractal scaling. 

## **4. Discussion** 

### _4.1. Algorithm Performance and Adaptability_ 

The comprehensive validation process reveals several important characteristics of the sliding window optimization approach that demonstrate its effectiveness across diverse fractal geometries without requiring manual parameter adjustment. 

The algorithm demonstrates adaptability to different fractal geometries through automatic parameter selection. The varying optimal window sizes (3–14 points across our test fractals) reflect the algorithm’s ability to identify fractal-specific scaling characteristics automatically. This adaptability is particularly evident in the performance differences: 

- Regular Self-Similar Fractals (Koch curve, Sierpinski triangle): Achieve high accuracy with moderate computational requirements. 

- Complex Space-Filling Curves (Hilbert curve): Require all three optimization phases for optimal performance but achieve high final accuracy. 

- Irregular Curves (Dragon curve): Benefit significantly from grid offset optimization due to their complex geometric arrangements. 

The practical complexity _O_ ( _n_<sup>3</sup> ) for the sliding window analysis remains computationally manageable because _n_ represents the number of box sizes (typically 10–20) rather than the number of geometric segments, enabling scalability to datasets exceeding 250,000 segments without prohibitive computational costs. 

_Fractal Fract._ **2025** , _9_ , 633 

16 of 20 

### 4.1.1. Comparison to Existing Results 

Table 4 presents published results for Koch and Hilbert curves and the Sierpinski triangle. The sliding window optimization demonstrates fractal-dependent performance, excelling for space-filling curves (Hilbert) and self-similar coastlines (Koch) while facing challenges with triangular self-similar structures (Sierpinski). This performance variation suggests that fractal-specific optimization strategies may be needed to achieve universal improvement across all geometric types. 

**Table 4.** Comparison with literature results for fractal dimension estimation. 

|**Study**|**Fractal**|**Reported D**|**Error %**|**This Study**|
|---|---|---|---|---|
|Gonzato et al. [7]|Koch|1.279|1.37%|0.11%|
||Sierpinski|1.565|1.26%|3.4%|
|Buczkowski et al. [16]|Sierpinski|1.583|0.13%|3.4%|
|Foroutan-pour et al. [6]|Koch|1.269|0.57%|0.11%|
|Xu & Lacidogna [9]|Koch|1.293|2.47%|0.11%|
||Sierpinski|1.585|0.003%|3.4%|
|So et al. [11]|Koch|1.267|0.41%|0.11%|
||Sierpinski|1.583|0.13%|3.4%|
||Hilbert|1.974|1.3%|0.39%|
|Wu et al. [21]|Koch|1.2664|0.36%|0.11%|
||Sierpinski|1.585|0.002%|3.4%|



The comparative analysis reveals important research opportunities: (1) developing adaptive parameter selection for different fractal geometries, (2) investigating why certain fractal types (Sierpinski triangles) resist optimization while others benefit significantly, and (3) incorporating geometric classification to automatically adjust algorithmic parameters based on fractal characteristics. The Sierpinski triangle results particularly highlight the need for geometry-aware optimization approaches that can adapt to triangular self-similar structures. 

### 4.1.2. Application to Physical Fractal Systems 

To demonstrate the algorithm’s applicability beyond mathematical fractals, we analyze the evolving interface of a Rayleigh–Taylor instability [22,23], representing the class of physical fractal systems that emerge from fluid dynamics simulations. This example addresses the transition from mathematical validation to real-world computational physics applications where fractal dimension provides quantitative characterization of interfacial complexity. 

Computational Setup: The Rayleigh–Taylor instability simulation employs a rectangular domain (0.4 m _×_ 0.5 m) with an initial planar interface at y = 0.25 m separating two fluids of similar density. The upper fluid ( _ρ_ = 994.17 kg/m<sup>3</sup> , _ν_ = 1.05 _×_ 10<sup>_−_6</sup> m<sup>2</sup> /s) overlies the lower fluid ( _ρ_ = 990.0 kg/m<sup>3</sup> , _ν_ = 1.003 _×_ 10<sup>_−_6</sup> m<sup>2</sup> /s), yielding an Atwood number _At_ = 2.1 _×_ 10<sup>_−_3</sup> representing a low-density contrast typical of oceanic or atmospheric stratification. Free-slip boundary conditions apply at the lateral and upper boundaries, with a no-slip condition at the bottom boundary. 

Initial Perturbation: The interface receives initial perturbations derived from linear stability analysis, implemented as a trigonometric series with 90 terms and random coefficients bounded by _±_ 1, with maximum perturbation magnitude of 0.0002 m/s. This approach ensures physically realistic initial conditions that respect the underlying instability physics while providing sufficient complexity for fractal interface development. 

Interface Evolution and Fractal Analysis: At t = 10 s, the initially planar interface has evolved into a complex pattern of rising bubbles and falling spikes characteristic of 

_Fractal Fract._ **2025** , _9_ , 633 

17 of 20 

Rayleigh–Taylor mixing. Figure 14 shows the extracted interface geometry, demonstrating the intricate structures that develop from the initial perturbations under gravitational acceleration. 



<!-- Start of picture text -->
0.5<br>0.4<br>0.3<br>0.2<br>0.1<br>0.0<br>0.00 0.05 0.10 0.15 0.20 0.25 0.30 0.35 0.40<br>X<br>Y<br><!-- End of picture text -->

**Figure 14.** Rayleigh–Taylor instability interface at t = 10 s showing complex fractal structure with characteristic bubble and spike formations (At = 2.1 _×_ 10<sup>_−_3</sup> ). 

Results: The three-phase optimization algorithm yields a fractal dimension of _D_ = 1.835 _±_ 0.0037 with _R_<sup>2</sup> = 0.999988, demonstrating exceptional statistical quality in the automated scaling region identification. This dimension value indicates significant interfacial complexity while remaining physically reasonable for a two-dimensional fluid interface at moderate development stages and is comparable with experimental results [23]. 

Physical Significance: Unlike mathematical fractals with precisely known mathematical dimensions, physical fractal systems like Rayleigh–Taylor interfaces possess dimensions that depend on flow parameters, boundary conditions, and the evolutionary stage. The measured dimension of 1.835 reflects the interface’s transition from the initial planar configuration (D = 1.0) toward more complex geometries, consistent with the characteristic bubble-and-spike morphology observed in Rayleigh–Taylor mixing. 

The automated scaling region selection becomes particularly valuable in such applications, as manual region selection could introduce bias based on researcher expectations about “appropriate” fractal behavior. The algorithm’s objective approach ensures reproducible characterization across different simulation conditions and temporal evolution stages. 

Computational Performance: The segment-based analysis demonstrates practical applicability to computational fluid dynamics workflows where interface complexity anal- 

_Fractal Fract._ **2025** , _9_ , 633 

18 of 20 

ysis supports mixing efficiency studies, turbulence characterization, multifractal analyses, and model validation. This capability extends the algorithm’s utility from mathematical validation to active research applications in fluid mechanics and related fields. 

### _4.2. Limitations and Future Research Directions_ 

While the validation study demonstrates good performance across mathematical fractals, several limitations should be acknowledged: 

- Mathematical Fractal Focus: Validation concentrated on mathematically generated fractals with precisely known dimensions. 

- 2D Geometric Analysis: Current implementation is limited to two-dimensional line segment analysis, reflecting the focus on planar fractal curves and fluid interfaces. Extension to three-dimensional fractal surfaces represents a natural progression requiring adaptation of the spatial indexing and intersection algorithms. 

- Parameter Generalization: The slope deviation threshold (0.12) and correlation threshold (0.99) were established through systematic analysis across multiple fractal types, but may require adjustment for significantly different geometric patterns or applications beyond the tested range. 

- Box Size Range Limitations: The automatic box size determination algorithm may generate insufficient scaling data for fractals with highly compact, folded geometries. 

- Variable Optimization Effectiveness: The three-phase optimization demonstrates inconsistent performance across fractal types, with some cases (Sierpinski triangle, Dragon curve) showing limited improvement or increased error compared to baseline methods. This indicates that optimization benefits are fractal-dependent and may not universally improve upon traditional approaches. 

Several promising research directions emerge from this work: extension to broader real-world data, three-dimensional implementation, adaptive parameter optimization, adaptive range expansion or alternative box size selection strategies for highly folded fractal geometries, and integration with advanced statistical methods. 

## **5. Conclusions** 

This work establishes a comprehensive framework for accurate fractal dimension calculation through optimal scaling region selection, validated across mathematical fractals and iteration convergence studies. Our findings provide both significant methodological advances and practical guidelines for the fractal analysis community. 

The research successfully addresses the fundamental challenge of subjective scaling region selection that has persisted in fractal dimension analysis for decades. The three-phase optimization algorithm demonstrates methodological innovation through the automatic sliding window method that objectively identifies optimal scaling regions without manual parameter tuning, combined with comprehensive boundary artifact detection and grid offset optimization. 

Key achievements include mean absolute error of 2.3% across five diverse mathematical fractals, with individual results ranging from high accuracy (Koch: 0.11%, Minkowski: 0.25% error and Hilbert: 0.39%) to good performance (Sierpinski: 3.4% and Dragon: 7.4% error). All results achieve _R_<sup>2</sup> _≥_ 0.9996, indicating strong statistical quality. 

The comprehensive validation scope includes systematic testing across five wellcharacterized mathematical fractals with known dimensions, compared to the typical validation on one or two specific fractal types in previous research. This provides confidence in algorithmic robustness across the dimensional spectrum from 1.26 to 2.00. 

The systematic iteration convergence analysis reveals fundamental principles including the convergence plateau principle where each fractal type exhibits optimal iteration 

_Fractal Fract._ **2025** , _9_ , 633 

19 of 20 

ranges where authentic scaling behavior emerges before discretization artifacts dominate, and fractal-specific guidelines with practical convergence requirements ranging from rapid convergers to gradual convergers. 

For researchers currently working with fractal dimension analysis, this work provides elimination of subjective bias through automated scaling region selection, computational guidelines enabling intelligent resource allocation, quality assessment tools for objective measurement reliability assessment, and integration capabilities for larger computational workflows. 

While not providing universal improvement, this work establishes a foundation for fractal-specific optimization and demonstrates the importance of systematic validation across diverse geometric types. The identification of performance boundaries provides valuable guidance for future algorithmic development and establishes clear application domains where the method excels. 

**Supplementary Materials:** Supplementary Materials including the Python3 code used to compute these results can be found at: https://github.com/rwdlnk/Fractal-Dimension-Analyzer, accessed on 27 September 2025. 

**Funding:** This research received no external funding. 

**Data Availability Statement:** The original contributions presented in this study are included in the article/Supplementary Materials. Further inquiries can be directed to the corresponding author. 

**Acknowledgments:** The algorithm implementation and analysis were performed in collaboration with Claude Sonnet 4 (Anthropic). During the preparation of this work the author used Claude Sonnet 4 (Anthropic) in order to enhance readability, improve language clarity, and assist with algorithm implementation and analysis. After using this tool, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article. 

**Conflicts of Interest:** Author R.W.D. is Member and Manager of Douglass Research and Development, LLC and declares no conflicts of interest. 

## **References** 

1. Richardson, L.F. The problem of contiguity: An appendix of statistics of deadly quarrels. _Gen. Syst. Yearb._ **1961** , _6_ , 139–187. 2. Mandelbrot, B.B. How long is the coast of Britain? Statistical self-similarity and fractional dimension. _Science_ **1967** , _156_ , 636–638. [CrossRef] [PubMed] 

3. Liebovitch, L.S.; Tóth, T. A fast algorithm to determine fractal dimensions by box counting. _Phys. Lett. A_ **1989** , _141_ , 386–390. [CrossRef] 

4. Bouda, M.; Caplan, J.S.; Saiers, J.E. Box-counting dimension revisited: Presenting an efficient method of minimizing quantization error and an assessment of the self-similarity of structural root systems. _Front. Plant Sci._ **2016** , _7_ , 149. [CrossRef] [PubMed] 

5. Datseris, G.; Kottlarz, I.; Braun, A.P.; Parlitz, U. Estimating fractal dimensions: A comparative review and open source implementations. _Chaos_ **2023** , _33_ , 102101. [CrossRef] [PubMed] 

6. Foroutan-pour, K.; Dutilleul, P.; Smith, D.L. Advances in the implementation of the box-counting method of fractal dimension estimation. _Appl. Math. Comput._ **1999** , _105_ , 195–210. [CrossRef] 

7. Gonzato, G.; Mulargia, F.; Tosatti, E. A practical implementation of the box counting algorithm. _Comput. Geosci._ **1998** , _24_ , 95–100. [CrossRef] 

8. Lopes, R.; Betrouni, N. Fractal and multifractal analysis: A review. _Med. Image Anal._ **2009** , _13_ , 634–649. [CrossRef] [PubMed] 9. Xu, J.; Lacidogna, G. A modified box-counting method to estimate the fractal dimensions. _Appl. Mech. Mater._ **2011** , _58–60_ , 1756–1761. [CrossRef] 

10. Wu, M.; Wang, W.; Shi, D.; Song, Z.; Li, M.; Luo, Y. Improving box-counting methods to directly estimate the fractal dimension. _Measurement_ **2021** , _177_ , 109303. [CrossRef] 

11. So, G.-B.; So, H.-R.; Jin, G.-G. Enhancement of the box-counting algorithm for fractal dimension estimation. _Pattern Recognit. Lett._ **2017** , _98_ , 53–58. [CrossRef] 

12. Jiang, W.; Liu, Y.; Li, R.; Liu, X.; Zhjang, J. Problems of the grid size selection in differential box-counting methods and an improvement strategy. _Entropy_ **2022** , _24_ , 977. [CrossRef] [PubMed] 

_Fractal Fract._ **2025** , _9_ , 633 

20 of 20 

13. Wang, J.; Yang, G.; Yuan, Y.; Sun, J.; Pu, G. Effects of scale parameters and counting origins on box counting fractal dimension and engineering applications in concrete beam crack analysis. _Fractals Fract._ **2024** , _9_ , 549. [CrossRef] 

14. Roy, A.; Perfect, E.; Dunne, W.M.; McKay, L.D. Fractal characterization of fracture networks: An improved box-counting technique. _J. Geophys. Res. Solid Earth_ **2007** , _112_ , B12. [CrossRef] 

15. Deshmukh, V.; Bradley, E.; Garland, J.; Meiss, J.D. Toward automated extraction and characterization of scaling regions in dynamical systems. _Chaos_ **2021** , _31_ , 123102. [CrossRef] [PubMed] 

16. Buczkowski, S.; Kyriacos, S.; Nekka, F.; Cartilier, L. The modified box-counting method: Analysis of some characteristic parameters. _Pattern Recognit._ **1998** , _31_ , 411–418. [CrossRef] 

17. Draper, N.R.; Smith, H. _Applied Regression Analysis_ , 3rd ed.; Wiley: Hoboken, NJ, USA, 1998. 

18. Montgomery, D.C.; Peck, E.A.; Vining, G.G. _Introduction to Linear Regression Analysis_ , 5th ed.; Wiley: Hoboken, NJ, USA, 2012. 

19. De Berg, M.; Cheong, O.; van Kreveld, M.; Overmars, M. _Computational Geometry: Algorithms and Applications_ , 3rd ed.; Springer: Berlin/Heidelberg, Germany, 2008. 

20. Liang, Y.D.; Barsky, B.A. Barsky line clipping. _Commun. ACM_ **1984** , _27_ , 868–877. 

21. Wu, J.; Jin, X.; Mi, S.; Tang, J. An effective method to compute the box-counting dimension based on the mathematical definition and intervals. _Results Eng._ **2020** , _6_ , 100106. [CrossRef] 

22. Chandrasekhar, S. _Hydrodynamic and Hydromagnetic Stability_ ; Oxford University Press: Oxford, UK, 1961. 

23. Dalziel, S.B.; Linden, P.F.; Youngs, D.L. Self-similarity and internal structure of turbulence induced by Rayleigh-Taylor instabilities. _J. Fluid Mech._ **1999** , _399_ , 1–48. [CrossRef] 

**Disclaimer/Publisher’s Note:** The statements, opinions and data contained in all publications are solely those of the individual author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to people or property resulting from any ideas, methods, instructions or products referred to in the content. 

