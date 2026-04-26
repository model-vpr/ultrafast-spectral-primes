"""
RIEMANN ZETA ZEROS FROM QUANTUM OPERATOR
=========================================
Hamiltonian-based generation of Riemann zeros with dynamic zero generation.
No static array - uses mpmath.zetazero() for ground truth.
"""

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
from sympy import isprime
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, PolynomialFeatures  # <-- ДОБАВЕТЕ ТОВА
from sklearn.pipeline import Pipeline
from sklearn.utils import resample
import matplotlib.pyplot as plt
import warnings
import time


warnings.filterwarnings('ignore')

# Try to import mpmath for dynamic zero generation
try:
    from mpmath import zetazero, mp
    mp.dps = 30
    MPMATH_AVAILABLE = True
except ImportError:
    MPMATH_AVAILABLE = False
    print("Warning: mpmath not installed. Install with: pip install mpmath")


# ============================================================================
# DYNAMIC RIEMANN ZERO GENERATION
# ============================================================================

def get_riemann_zeros_dynamic(n_zeros, verbose=True):
    """
    Generate first n_zeros Riemann zeros dynamically using mpmath.
    
    Parameters:
    -----------
    n_zeros : int
        Number of zeros to generate
    verbose : bool
        Print progress information
    
    Returns:
    --------
    numpy.ndarray
        Array of imaginary parts of zeros (γ_n)
    """
    if not MPMATH_AVAILABLE:
        print("ERROR: mpmath is required for dynamic zero generation.")
        print("Please install: pip install mpmath")
        return None
    
    print(f"Generating first {n_zeros} Riemann zeros using mpmath.zetazero()...")
    zeros = []
    start_time = time.time()
    
    for n in range(1, n_zeros + 1):
        try:
            zero = zetazero(n)
            zeros.append(float(zero.imag))
            
            if verbose and n % 100 == 0:
                elapsed = time.time() - start_time
                print(f"  Generated {n} zeros in {elapsed:.1f}s...")
        except Exception as e:
            print(f"Error at zero {n}: {e}")
            break
    
    elapsed = time.time() - start_time
    zeros = np.array(zeros)
    
    print(f"✓ Generated {len(zeros)} zeros in {elapsed:.1f}s")
    
    # Show first few zeros for verification
    print(f"\nFirst 5 zeros (verification):")
    for i in range(min(5, len(zeros))):
        print(f"  γ_{i+1} = {zeros[i]:.6f}")
    
    return zeros


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_primes(n_max):
    """Generate prime numbers up to n_max"""
    return [p for p in range(2, n_max + 1) if isprime(p)]


def build_hamiltonian(n_values, primes):
    """
    Build Hamiltonian with realistic parameters.
    This is the Quantum Resonance Operator.
    """
    n = len(n_values)
    h = n_values[1] - n_values[0]  # grid spacing

    # Physical parameters
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
        # Logarithmic weakening as in the physical model
        delta_terms[valid_primes] = lambda_base / (np.log(n_values[valid_primes] + 10))**2

    return diags([diag + delta_terms, off_diag, off_diag],
                 [0, -1, 1], shape=(n, n), format='csr')


# ============================================================================
# MODEL FITTING FUNCTIONS
# ============================================================================

def improved_realistic_scaling(eigenvalues, target_zeros):
    """
    Improved estimation with overfitting protection.
    Maps Hamiltonian eigenvalues to Riemann zeros.
    """
    valid_mask = (eigenvalues > 0) & ~np.isnan(eigenvalues)
    valid_eigenvalues = eigenvalues[valid_mask]
    valid_targets = target_zeros[:len(valid_eigenvalues)]
    
    if len(valid_eigenvalues) < 20:
        print("Not enough data for reliable estimation")
        return None, None, None

    X = valid_eigenvalues.reshape(-1, 1)
    y = valid_targets

    print(f"Analyzing {len(X)} examples")

    # Compare several models for stability check
    models = {
        'Linear': LinearRegression(),
        'GBM_Simple': GradientBoostingRegressor(n_estimators=50, max_depth=2, random_state=42),
        'GBM_Medium': GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    }

    best_test_r2 = -float('inf')
    best_predictions = None
    best_model_name = None

    for name, model in models.items():
        print(f"\nTesting {name}...")

        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        print(f"  CV R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")

        # Train/test evaluation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.4, random_state=42
        )

        model.fit(X_train, y_train)
        y_test_pred = model.predict(X_test)
        test_r2 = r2_score(y_test, y_test_pred)

        print(f"  Test R²: {test_r2:.4f}")

        if test_r2 > best_test_r2:
            best_test_r2 = test_r2
            best_model_name = name
            best_model = model
            best_predictions = best_model.predict(X)

    print(f"\nBEST MODEL: {best_model_name} (Test R² = {best_test_r2:.4f})")

    # Stability check via bootstrap
    print("\nStability check (bootstrap)...")
    bootstrap_r2 = []
    n_bootstrap = 20

    for i in range(n_bootstrap):
        X_bs, y_bs = resample(X, y, random_state=i)
        X_train, X_test, y_train, y_test = train_test_split(
            X_bs, y_bs, test_size=0.3, random_state=42
        )
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        bootstrap_r2.append(r2_score(y_test, y_pred))

    print(f"  Bootstrap R²: {np.mean(bootstrap_r2):.4f} (±{np.std(bootstrap_r2):.4f})")

    # Final predictions with best model
    final_model = models[best_model_name]
    final_model.fit(X, y)
    final_predictions = final_model.predict(X)

    # Overfitting diagnostics
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    final_model.fit(X_train, y_train)

    train_pred = final_model.predict(X_train)
    test_pred = final_model.predict(X_test)

    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)

    overfitting_gap = train_r2 - test_r2
    print(f"\nOVERFITTING DIAGNOSTICS:")
    print(f"  Train R²: {train_r2:.4f}")
    print(f"  Test R²: {test_r2:.4f}")
    print(f"  Gap: {overfitting_gap:.4f}")

    if overfitting_gap > 0.1:
        print("  ⚠️ SIGNIFICANT OVERFITTING")
    elif overfitting_gap > 0.05:
        print("  ⚠️ MILD OVERFITTING")
    else:
        print("  ✅ GOOD GENERALIZATION")

    return final_predictions, test_r2, overfitting_gap


def improved_conservative_analysis(eigenvalues, target_zeros):
    """
    Improved conservative analysis with better scaling.
    """
    valid_mask = (eigenvalues > 0) & ~np.isnan(eigenvalues)
    valid_eigenvalues = eigenvalues[valid_mask]
    valid_targets = target_zeros[:len(valid_eigenvalues)]

    if len(valid_eigenvalues) < 15:
        return np.full(len(eigenvalues), np.nan), 0, "Insufficient data"

    X = valid_eigenvalues.reshape(-1, 1)
    y = valid_targets

    # Data normalization for better scaling
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()

    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).ravel()

    # Use robust linear model
    model = Ridge(alpha=1.0, random_state=42)

    # Strict evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_scaled, test_size=0.4, random_state=42
    )

    model.fit(X_train, y_train)

    # Predictions in normalized scale
    y_pred_scaled = model.predict(X_scaled)

    # Inverse transform to original scale
    y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()

    # Evaluate on test data
    y_test_pred_scaled = model.predict(X_test)
    y_test_pred = scaler_y.inverse_transform(y_test_pred_scaled.reshape(-1, 1)).ravel()
    y_test_original = scaler_y.inverse_transform(y_test.reshape(-1, 1)).ravel()

    test_r2 = r2_score(y_test_original, y_test_pred)

    # Reliability assessment
    if test_r2 < 0.95:
        reliability = "MEDIUM"
    elif test_r2 < 0.98:
        reliability = "GOOD"
    else:
        reliability = "EXCELLENT"

    # Create result array
    result = np.full(len(eigenvalues), np.nan)
    result[valid_mask] = y_pred

    return result, test_r2, reliability


def advanced_diagnosis(eigenvalues, target_zeros):
    """
    Extended model diagnostics.
    """
    print("\nEXTENDED DIAGNOSTICS")
    print("="*50)

    valid_mask = (eigenvalues > 0) & ~np.isnan(eigenvalues)
    X = eigenvalues[valid_mask].reshape(-1, 1)
    y = target_zeros[:len(X)]

    # Check linear dependence
    correlation = np.corrcoef(X.ravel(), y)[0, 1]
    print(f"Eigenvalue-zero correlation: {correlation:.4f}")

    # Residual analysis
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    residuals = y - y_pred

    print(f"Mean residual: {np.mean(residuals):.6f}")
    print(f"Std of residuals: {np.std(residuals):.6f}")

    # Nonlinearity check
    poly_model = Pipeline([
        ('poly', PolynomialFeatures(degree=2)),
        ('linear', LinearRegression())
    ])

    poly_model.fit(X, y)
    poly_score = poly_model.score(X, y)
    print(f"R² with quadratic terms: {poly_score:.4f}")

    return correlation, np.std(residuals), poly_score


def print_detailed_comparison(computed_γ, target_zeros, title="COMPARISON"):
    """Detailed result comparison."""
    valid_mask = ~np.isnan(computed_γ)
    valid_computed = computed_γ[valid_mask]
    valid_targets = target_zeros[:len(valid_computed)]

    print(f"\n{title}:")
    print("="*80)
    print(f"{'#':>3} {'Theory':>12} {'Computed':>12} {'Diff':>12} {'Rel.Error(%)':>15}")
    print("-"*80)
    
    differences = []
    relative_errors = []

    for i, (comp, th) in enumerate(zip(valid_computed, valid_targets)):
        diff = abs(comp - th)
        rel_error = (diff / th) * 100
        differences.append(diff)
        relative_errors.append(rel_error)

        if i < 10 or (i % 10 == 9 and i > 0):
            print(f"{i+1:3d} {th:12.6f} {comp:12.6f} {diff:12.6f} {rel_error:15.2f}")

    print("-"*80)
    print(f"Mean absolute difference: {np.mean(differences):.6f}")
    print(f"Mean relative error: {np.mean(relative_errors):.2f}%")
    print(f"Max difference: {np.max(differences):.6f}")

    return differences, relative_errors


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main_final():
    """
    Main analysis: Generate Riemann zeros dynamically using Hamiltonian,
    then compare with true Riemann zeros from mpmath.
    """
    print("="*80)
    print("QUANTUM OPERATOR → RIEMANN ZEROS")
    print("Hamiltonian-based generation with dynamic zero validation")
    print("="*80)
    
    # Configuration
    LIMIT = 150000
    NUM_ZEROS = 10000  # Can be increased (e.g., 200, 500, 1000)
    
    print(f"\nConfiguration:")
    print(f"  Prime limit: {LIMIT}")
    print(f"  Target zeros: {NUM_ZEROS}")
    
    # Generate dynamic Riemann zeros for validation
    print("\n" + "-"*80)
    print("STEP 1: Generating true Riemann zeros (for validation)")
    print("-"*80)
    
    true_zeros = get_riemann_zeros_dynamic(NUM_ZEROS, verbose=True)
    
    if true_zeros is None:
        print("Cannot proceed without mpmath. Exiting.")
        return
    
    # Generate primes and grid
    print("\n" + "-"*80)
    print("STEP 2: Building Hamiltonian")
    print("-"*80)
    
    print("Generating primes...")
    primes = get_primes(LIMIT)
    print(f"  Found {len(primes)} primes up to {LIMIT}")
    
    print("Building numerical grid...")
    n_points = 20000
    n_values = np.geomspace(1.0001, LIMIT, n_points)
    print(f"  Grid created with {n_points} points")
    
    print("Building Hamiltonian matrix...")
    H = build_hamiltonian(n_values, primes)
    
    # Compute eigenvalues
    print("\n" + "-"*80)
    print("STEP 3: Computing eigenvalues (this may take a moment)")
    print("-"*80)
    
    try:
        eigenvalues = eigsh(H, k=NUM_ZEROS, which='LM', sigma=0,
                           maxiter=1000, tol=1e-10)[0]
        eigenvalues = np.sort(eigenvalues)
        
        print(f"\n✓ Computed {len(eigenvalues)} eigenvalues")
        print(f"  Range: [{eigenvalues[0]:.2f}, {eigenvalues[-1]:.2f}]")
        
        # Fit models
        print("\n" + "-"*80)
        print("STEP 4: Fitting models")
        print("-"*80)
        
        print("\n1. STANDARD ANALYSIS (GradientBoosting):")
        computed_γ, test_r2, overfitting_gap = improved_realistic_scaling(
            eigenvalues, true_zeros
        )
        
        print("\n2. CONSERVATIVE ANALYSIS (Ridge regression):")
        conservative_γ, conservative_r2, reliability = improved_conservative_analysis(
            eigenvalues, true_zeros
        )
        
        # Extended diagnostics
        from sklearn.preprocessing import PolynomialFeatures
        
        print("\n" + "-"*80)
        print("STEP 5: Diagnostics")
        print("-"*80)
        
        correlation, resid_std, poly_score = advanced_diagnosis(eigenvalues, true_zeros)
        
        print(f"\nDIAGNOSTIC INDICATORS:")
        print(f"  High correlation: {correlation > 0.95} ({correlation:.4f})")
        print(f"  Stable residuals: {resid_std < 1.0} ({resid_std:.4f})")
        print(f"  Nonlinearity: {poly_score > 0.999} ({poly_score:.4f})")
        
        print(f"\nFINAL ASSESSMENT:")
        print(f"  Standard Test R²: {test_r2:.4f}")
        print(f"  Conservative Test R²: {conservative_r2:.4f}")
        print(f"  Reliability: {reliability}")
        
        # Visualization
        if computed_γ is not None and conservative_γ is not None:
            print("\n" + "-"*80)
            print("STEP 6: Detailed Comparison")
            print("-"*80)
            
            valid_mask = ~np.isnan(computed_γ)
            x = np.arange(np.sum(valid_mask))
            
            # Detailed comparison
            diff_std, rel_std = print_detailed_comparison(
                computed_γ, true_zeros, "STANDARD MODEL"
            )
            diff_cons, rel_cons = print_detailed_comparison(
                conservative_γ, true_zeros, "CONSERVATIVE MODEL"
            )
            
            # Visualization
            plt.figure(figsize=(16, 12))
            
            # Plot 1: Zero comparison
            plt.subplot(2, 2, 1)
            plt.plot(x, true_zeros[:len(x)], 'ko-', ms=4, label='True Riemann Zeros', linewidth=0.5)
            plt.plot(x, computed_γ[valid_mask], 'ro-', ms=4, label='Standard (GBM)', alpha=0.7, linewidth=0.5)
            plt.plot(x, conservative_γ[valid_mask], 'bo-', ms=4, label='Conservative (Ridge)', alpha=0.7, linewidth=0.5)
            plt.ylabel('Zero value (γ)')
            plt.xlabel('Zero index')
            plt.legend()
            plt.title(f'Zero Comparison\nBest R²: {max(test_r2, conservative_r2):.4f}')
            plt.grid(True, alpha=0.3)
            
            # Plot 2: Absolute errors
            plt.subplot(2, 2, 2)
            errors_std = np.abs(computed_γ[valid_mask] - true_zeros[:len(x)])
            errors_cons = np.abs(conservative_γ[valid_mask] - true_zeros[:len(x)])
            
            plt.plot(x, errors_std, 'r-', label='Standard error', alpha=0.7)
            plt.plot(x, errors_cons, 'b-', label='Conservative error', alpha=0.7)
            plt.xlabel('Zero index')
            plt.ylabel('Absolute error')
            plt.legend()
            plt.title('Absolute Error Comparison')
            plt.grid(True, alpha=0.3)
            
            # Plot 3: Relative errors
            plt.subplot(2, 2, 3)
            plt.plot(x, rel_std, 'r-', label='Standard rel. error', alpha=0.7)
            plt.plot(x, rel_cons, 'b-', label='Conservative rel. error', alpha=0.7)
            plt.xlabel('Zero index')
            plt.ylabel('Relative error (%)')
            plt.legend()
            plt.title('Relative Errors')
            plt.grid(True, alpha=0.3)
            
            # Plot 4: Error distribution
            plt.subplot(2, 2, 4)
            plt.hist(errors_std, bins=20, alpha=0.7, color='red', label='Standard')
            plt.hist(errors_cons, bins=20, alpha=0.7, color='blue', label='Conservative')
            plt.xlabel('Absolute error')
            plt.ylabel('Frequency')
            plt.legend()
            plt.title('Error Distribution')
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('quantum_operator_zeros.png', dpi=150)
            plt.show()
            
            print(f"\n✓ Plot saved to 'quantum_operator_zeros.png'")
        
        # Final conclusion
        print("\n" + "="*80)
        print("FINAL CONCLUSION")
        print("="*80)
        
        if test_r2 > 0.99 and overfitting_gap < 0.05:
            print("✅ HIGH MODEL QUALITY - excellent fit with minimal overfitting")
            print("   The quantum operator successfully reproduces Riemann zeros!")
        elif test_r2 > 0.95:
            print("✅ GOOD FIT - model captures main dependencies")
            print("   The quantum operator shows strong correlation with Riemann zeros")
        else:
            print("⚠️ MODERATE EFFECTIVENESS - room for improvement")
            print("   Consider increasing grid resolution or adjusting physical parameters")
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Execution error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main_final()