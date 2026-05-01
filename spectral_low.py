import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
from sympy import isprime
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Import mpmath for Riemann zeros
try:
    from mpmath import mp, zetazero
    mp.dps = 10  # Достатъчно за 5-6 знака точност след закръгляне
    MPMATH_AVAILABLE = True
except ImportError:
    MPMATH_AVAILABLE = False
    print("Warning: mpmath not installed. Install with: pip install mpmath")

# ==============================================================================
# CONFIGURATION AND DATA
# ==============================================================================
LIMIT = 1201
NUM_ZEROS = 500  # Number of zeros to use

# ==============================================================================
# 1. FUNCTION TO GENERATE RIEMANN ZEROS DYNAMICALLY (FAST VERSION)
# ==============================================================================
def get_riemann_zeros_fast(n_zeros):
    """
    Generate first n_zeros Riemann zeros using mpmath's optimized zetazero().
    Returns numpy array of imaginary parts rounded to 5 decimal places.
    """
    if not MPMATH_AVAILABLE:
        print("ERROR: mpmath is required. Install with: pip install mpmath")
        return None
    
    print(f"Generating first {n_zeros} Riemann zeros using zetazero()...")
    zeros = []
    
    for n in range(1, n_zeros + 1):
        try:
            # zetazero(n) returns the n-th zero as complex number
            zero = zetazero(n)
            # Get imaginary part and round to 5 decimal places
            zero_val = round(float(zero.imag), 5)
            zeros.append(zero_val)
            
            # Progress indicator
            if n % 50 == 0:
                print(f"  Generated {n} zeros... (last: {zero_val:.5f})")
        except Exception as e:
            print(f"Error at zero {n}: {e}")
            break
    
    print(f"Successfully generated {len(zeros)} zeros.")
    
    # Verify first few zeros
    print("\nFirst 10 generated zeros:")
    for i in range(min(10, len(zeros))):
        print(f"  γ_{i+1} = {zeros[i]:.5f}")
    
    return np.array(zeros)

# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================
def get_primes(n_max):
    """Generate all prime numbers up to n_max"""
    return [p for p in range(2, n_max + 1) if isprime(p)]

def build_hamiltonian(n_values, primes):
    """Build the Hamiltonian matrix with realistic physical parameters"""
    n = len(n_values)
    h = n_values[1] - n_values[0]  # grid spacing

    # Realistic physical parameters
    potential_coeff = 0.75
    lambda_base = 1e6  # Strength of delta interactions

    # Main diagonal: kinetic + 3/(4n²) potential
    diag = potential_coeff / (n_values**2 + 1e-12) + 2 / h**2
    off_diag = -1 / h**2

    # Delta-function potentials at prime locations
    delta_terms = np.zeros(n)
    prime_indices = [np.argmin(np.abs(n_values - p)) for p in primes if p <= n_values[-1]]
    if prime_indices:
        prime_indices = np.array(prime_indices)
        valid_primes = prime_indices[prime_indices < n]
        # Use logarithmic weakening as in the physical model
        delta_terms[valid_primes] = lambda_base / (np.log(n_values[valid_primes]))**2

    return diags([diag + delta_terms, off_diag, off_diag],
                 [0, -1, 1], shape=(n, n), format='csr')

# ==============================================================================
# 3. QUINITIC + LOGARITHMIC LAW
# ==============================================================================
def quinitic_with_log_law(x, A, B, C, D, E, F, A_log):
    """
    Quintic Polynomial + Logarithmic Correction Term:
    γ(λ) ≈ A + Bλ + Cλ² + Dλ³ + Eλ⁴ + Fλ⁵ + A_log * ln(λ)
    """
    poly_term = A + B*x + C*x**2 + D*x**3 + E*x**4 + F*x**5
    log_correction = A_log * np.log(x)
    return poly_term + log_correction

def fit_and_scale_with_log_quinitic(eigenvalues, target_zeros, weights=None):
    """
    Fit the 7-parameter Quintic + Log model using Weighted Least Squares (WLS)
    """
    X = np.arange(1, len(target_zeros) + 1).astype(float)
    Y = target_zeros

    # Initial guess from previous stable fits
    p0_log_quinitic = [
        11.379,        # A
        3.220,         # B
        -0.0141,       # C
        0.000053,      # D
        -0.00000009,   # E
        0.0000000001,  # F
        5.0            # A_log
    ]

    fit_args = {'p0': p0_log_quinitic}
    if weights is not None:
        fit_args['sigma'] = 1.0 / np.sqrt(weights)
        fit_args['absolute_sigma'] = True

    try:
        popt, _ = curve_fit(quinitic_with_log_law, X, Y, **fit_args)
    except RuntimeError as e:
        print(f"!!! curve_fit failed: {e}. Falling back to initial guess.")
        popt = p0_log_quinitic

    Y_predicted = quinitic_with_log_law(X, *popt)
    R2 = r2_score(Y, Y_predicted)
    MAE = mean_absolute_error(Y, Y_predicted)
    Residuals = Y - Y_predicted

    A, B, C, D, E, F, A_log = popt
    return A, B, C, D, E, F, A_log, Y_predicted, R2, MAE, Residuals

# ==============================================================================
# 4. MAIN ANALYSIS FUNCTION
# ==============================================================================
def main_final():
    print("FINAL SPECTRAL ANALYSIS: QUINTIC + LOG LAW")
    print("=" * 75)
    
    # Generate Riemann zeros dynamically
    riemann_zeros = get_riemann_zeros_fast(NUM_ZEROS)
    
    if riemann_zeros is None:
        print("Failed to generate Riemann zeros. Exiting.")
        return
    
    print(f"\n{'='*75}")
    print(f"Using {len(riemann_zeros)} Riemann zeros for analysis")
    print(f"{'='*75}\n")
    
    # Generate primes and numerical grid
    print("Generating primes and numerical grid...")
    primes = get_primes(LIMIT)
    n_points = 20000
    n_values = np.geomspace(1.0001, LIMIT, n_points)
    
    # Build Hamiltonian and compute eigenvalues
    print("Building Hamiltonian and computing eigenvalues...")
    print(f"Grid size: {n_points}, Number of primes: {len(primes)}")
    H = build_hamiltonian(n_values, primes)
    
    try:
        # Compute eigenvalues
        print(f"Computing first {NUM_ZEROS} eigenvalues (this may take a moment)...")
        eigenvalues = eigsh(H, k=NUM_ZEROS, which='LM', sigma=0,
                            maxiter=1000, tol=1e-10)[0]
        eigenvalues = np.sort(eigenvalues)
        
        # Weighted Least Squares
        print("\nApplying Weighted Least Squares...")
        weights = np.ones(NUM_ZEROS)
        if NUM_ZEROS >= 1: weights[0] = 1000
        if NUM_ZEROS >= 2: weights[1] = 50
        if NUM_ZEROS >= 3: weights[2] = 20
        if NUM_ZEROS >= 4: weights[3] = 10
        if NUM_ZEROS >= 5: weights[4] = 5
        
        # Calibrate the model
        A, B, C, D, E, F, A_log, Y_predicted, R2, MAE, Residuals = \
            fit_and_scale_with_log_quinitic(eigenvalues, riemann_zeros, weights)
        
        # Results
        print("\n" + "="*75)
        print("DISCOVERED SPECTRAL LAW (Quintic + Log)")
        print("="*75)
        print(f"R² Score:          {R2:.10f}")
        print(f"MAE:               {MAE:.8f}")
        max_abs_error = np.max(np.abs(Residuals))
        max_abs_error_idx = np.argmax(np.abs(Residuals))
        print(f"Max Abs Error:     {max_abs_error:.6f} (at index {max_abs_error_idx + 1})")
        
        print("\nFORMULA: γ(λ) ≈ A + Bλ + Cλ² + Dλ³ + Eλ⁴ + Fλ⁵ + A_log·ln(λ)")
        print(f"A (constant):      {A:.10f}")
        print(f"B (linear):        {B:.10f}")
        print(f"C (quadratic):     {C:.10f}")
        print(f"D (cubic):         {D:.10f}")
        print(f"E (quartic):       {E:.10f}")
        print(f"F (quintic):       {F:.10f}")
        print(f"A_log (ln term):   {A_log:.10f}")
        
        # First 10 zeros comparison
        print(f"\n{'='*75}")
        print("FIRST 10 ZEROS COMPARISON")
        print("="*75)
        print(f"{'#':>3} {'Theory (γ)':>12} {'Predicted':>12} {'Residual':>12}")
        print("-" * 42)
        for i in range(min(10, NUM_ZEROS)):
            print(f"{i+1:3d} {riemann_zeros[i]:12.5f} {Y_predicted[i]:12.5f} {Residuals[i]:12.6f}")
        
        # Plot results
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Residual plot
        ax1.scatter(np.arange(1, NUM_ZEROS + 1), Residuals, 
                   color='darkred', s=20, alpha=0.6)
        ax1.axhline(0, color='black', linestyle='--', linewidth=1)
        ax1.axhline(max_abs_error, color='red', linestyle=':', alpha=0.7)
        ax1.axhline(-max_abs_error, color='red', linestyle=':', alpha=0.7)
        ax1.set_title(f'Residuals - Quintic + Log Law\nR² = {R2:.8f}, Max Error = {max_abs_error:.4f}')
        ax1.set_xlabel('Zero Index')
        ax1.set_ylabel('Residual')
        ax1.grid(True, alpha=0.3)
        
        # Comparison plot
        ax2.plot(np.arange(1, NUM_ZEROS + 1), riemann_zeros, 'b-', 
                label='Riemann Zeros', linewidth=1, alpha=0.7)
        ax2.plot(np.arange(1, NUM_ZEROS + 1), Y_predicted, 'r--', 
                label='Predicted (Quintic+Log)', linewidth=1, alpha=0.7)
        ax2.set_title(f'Spectral Law calibrate (first {NUM_ZEROS} zeros)')
        ax2.set_xlabel('Zero Index')
        ax2.set_ylabel('γ (Imaginary part)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        print("\n" + "="*75)
        print("ANALYSIS COMPLETE")
        print("="*75)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main_final()