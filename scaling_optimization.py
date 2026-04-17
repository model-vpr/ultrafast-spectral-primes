"""
SCALABLE SPECTRAL LAW: Multi-Range Optimization
================================================
This script finds optimal coefficients for different ranges of n
and analyzes how they scale with n_max.
"""
# Copyright (c) 2026 Stefka Georgieva
# Licensed under CC BY-NC-ND 4.0
# Commercial use requires a separate license. 
# Contact: georgieva@vpr-research.eu; vpr.model@gmail.com


import numpy as np
import matplotlib.pyplot as plt
from mpmath import zetazero
from scipy.optimize import curve_fit
from scipy.stats import linregress
import time

# ============================================================================
# SPECTRAL LAW MODEL
# ============================================================================

def spectral_law_model(x, A, B, C, D, E, F, A_log):
    """
    Quinitic polynomial + logarithmic term
    γ(x) ≈ A + B·x + C·x² + D·x³ + E·x⁴ + F·x⁵ + A_log·ln(x)
    """
    poly = A + B*x + C*x**2 + D*x**3 + E*x**4 + F*x**5
    log_term = A_log * np.log(x)
    return poly + log_term


def fit_spectral_law(n_values, zeros, weights=None):
    """Fit spectral law to given range"""
    X = n_values
    Y = zeros
    
    # Initial guess
    p0 = [11.7, 2.4, -0.0068, 2.15e-5, -3.2e-8, 0.0, 6.4]
    
    try:
        popt, _ = curve_fit(spectral_law_model, X, Y, p0=p0, maxfev=10000)
        Y_pred = spectral_law_model(X, *popt)
        residuals = Y - Y_pred
        r2 = 1 - np.sum(residuals**2) / np.sum((Y - np.mean(Y))**2)
        mae = np.mean(np.abs(residuals))
        max_error = np.max(np.abs(residuals))
        
        return {
            'A': popt[0], 'B': popt[1], 'C': popt[2],
            'D': popt[3], 'E': popt[4], 'F': popt[5],
            'A_log': popt[6],
            'r2': r2, 'mae': mae, 'max_error': max_error
        }
    except Exception as e:
        print(f"  Fit failed: {e}")
        return None


# ============================================================================
# GENERATE TRUE ZEROS (CACHED)
# ============================================================================

def get_true_zeros_cached(n_max):
    """Get true zeros from cache or compute"""
    cache_file = f'true_zeros_{n_max}.npy'
    try:
        return np.load(cache_file)
    except:
        print(f"  Computing {n_max} zeros (this may take time)...")
        zeros = [float(zetazero(n).imag) for n in range(1, n_max + 1)]
        zeros = np.array(zeros)
        np.save(cache_file, zeros)
        return zeros


# ============================================================================
# MULTI-RANGE OPTIMIZATION
# ============================================================================

def optimize_for_ranges(ranges, verbose=True):
    """Optimize spectral law for multiple ranges"""
    results = []
    
    print("\n" + "="*80)
    print("MULTI-RANGE SPECTRAL LAW OPTIMIZATION")
    print("="*80)
    
    for n_max in ranges:
        print(f"\n--- Optimizing for n ≤ {n_max} ---")
        
        # Get true zeros
        zeros = get_true_zeros_cached(n_max)
        n_vals = np.arange(1, n_max + 1)
        
        # Fit spectral law
        start = time.time()
        result = fit_spectral_law(n_vals, zeros)
        elapsed = time.time() - start
        
        if result:
            result['n_max'] = n_max
            result['time'] = elapsed
            results.append(result)
            
            if verbose:
                print(f"  R² = {result['r2']:.8f}")
                print(f"  MAE = {result['mae']:.6f}")
                print(f"  Time = {elapsed:.2f}s")
                print(f"  A = {result['A']:.6f}, B = {result['B']:.6f}, A_log = {result['A_log']:.6f}")
    
    return results


# ============================================================================
# ANALYZE COEFFICIENT SCALING
# ============================================================================

def analyze_scaling(results):
    """Analyze how coefficients scale with n_max"""
    
    n_vals = [r['n_max'] for r in results]
    
    # Extract coefficients
    A_vals = [r['A'] for r in results]
    B_vals = [r['B'] for r in results]
    A_log_vals = [r['A_log'] for r in results]
    
    # Fit scaling laws
    log_n = np.log(n_vals)
    
    # A ~ a * log(n) + b
    slope_A, intercept_A, r_A, _, _ = linregress(log_n, A_vals)
    
    # B ~ a / log(n) + b
    inv_log_n = 1 / log_n
    slope_B, intercept_B, r_B, _, _ = linregress(inv_log_n, B_vals)
    
    # A_log ~ a * log(log(n)) + b
    log_log_n = np.log(log_n)
    slope_Alog, intercept_Alog, r_Alog, _, _ = linregress(log_log_n, A_log_vals)
    
    # Return as dictionary with correct keys
    return {
        'n_vals': n_vals,
        'A_vals': A_vals,
        'B_vals': B_vals,
        'A_log_vals': A_log_vals,
        'scaling': {
            'A': (slope_A, intercept_A, r_A**2),
            'B': (slope_B, intercept_B, r_B**2),
            'A_log': (slope_Alog, intercept_Alog, r_Alog**2)
        }
    }


# ============================================================================
# EXTRAPOLATION FOR LARGER N
# ============================================================================

def extrapolate_coefficients(n_max, scaling):
    """Extrapolate coefficients for larger n using scaling laws"""
    log_n = np.log(n_max)
    log_log_n = np.log(log_n)
    
    slope_A, intercept_A, _ = scaling['A']
    slope_B, intercept_B, _ = scaling['B']
    slope_Alog, intercept_Alog, _ = scaling['A_log']
    
    A_pred = slope_A * log_n + intercept_A
    B_pred = slope_B / log_n + intercept_B
    A_log_pred = slope_Alog * log_log_n + intercept_Alog
    
    return {
        'A': A_pred,
        'B': B_pred,
        'A_log': A_log_pred,
        'n_max': n_max
    }


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_results(results, scaling):
    """Plot coefficient evolution and scaling"""
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    n_vals = [r['n_max'] for r in results]
    
    # Plot 1: R² evolution
    ax1 = axes[0, 0]
    r2_vals = [r['r2'] for r in results]
    ax1.semilogx(n_vals, r2_vals, 'bo-', linewidth=2, markersize=8)
    ax1.axhline(y=0.99999, color='red', linestyle='--', label='0.99999 target')
    ax1.set_xlabel('n_max (log scale)')
    ax1.set_ylabel('R²')
    ax1.set_title('R² vs Range Size')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: MAE evolution
    ax2 = axes[0, 1]
    mae_vals = [r['mae'] for r in results]
    ax2.semilogx(n_vals, mae_vals, 'rs-', linewidth=2, markersize=8)
    ax2.set_xlabel('n_max (log scale)')
    ax2.set_ylabel('Mean Absolute Error')
    ax2.set_title('MAE vs Range Size')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: A coefficient scaling
    ax3 = axes[0, 2]
    A_vals = [r['A'] for r in results]
    ax3.semilogx(n_vals, A_vals, 'g^-', linewidth=2, markersize=8, label='Fitted')
    log_n = np.log(n_vals)
    slope_A, intercept_A, _ = scaling['scaling']['A']
    A_fit = slope_A * log_n + intercept_A
    ax3.semilogx(n_vals, A_fit, 'r--', linewidth=1.5, label=f'Fit: A = {slope_A:.3f}·ln(n) + {intercept_A:.3f}')
    ax3.set_xlabel('n_max (log scale)')
    ax3.set_ylabel('A (constant term)')
    ax3.set_title('Coefficient A Scaling')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Plot 4: B coefficient scaling
    ax4 = axes[1, 0]
    B_vals = [r['B'] for r in results]
    ax4.semilogx(n_vals, B_vals, 'm^-', linewidth=2, markersize=8, label='Fitted')
    inv_log_n = 1 / np.log(n_vals)
    slope_B, intercept_B, _ = scaling['scaling']['B']
    B_fit = slope_B / np.log(n_vals) + intercept_B
    ax4.semilogx(n_vals, B_fit, 'r--', linewidth=1.5, label=f'Fit: B = {slope_B:.3f}/ln(n) + {intercept_B:.3f}')
    ax4.set_xlabel('n_max (log scale)')
    ax4.set_ylabel('B (linear term)')
    ax4.set_title('Coefficient B Scaling')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # Plot 5: A_log coefficient scaling
    ax5 = axes[1, 1]
    A_log_vals = [r['A_log'] for r in results]
    ax5.semilogx(n_vals, A_log_vals, 'c^-', linewidth=2, markersize=8, label='Fitted')
    log_log_n = np.log(np.log(n_vals))
    slope_Alog, intercept_Alog, _ = scaling['scaling']['A_log']
    A_log_fit = slope_Alog * log_log_n + intercept_Alog
    ax5.semilogx(n_vals, A_log_fit, 'r--', linewidth=1.5, 
                label=f'Fit: A_log = {slope_Alog:.3f}·ln(ln(n)) + {intercept_Alog:.3f}')
    ax5.set_xlabel('n_max (log scale)')
    ax5.set_ylabel('A_log (log term)')
    ax5.set_title('Coefficient A_log Scaling')
    ax5.grid(True, alpha=0.3)
    ax5.legend()
    
    # Plot 6: Summary table
    ax6 = axes[1, 2]
    ax6.axis('tight')
    ax6.axis('off')
    
    table_data = [
        ['n_max', 'R²', 'MAE', 'A', 'B', 'A_log'],
    ]
    for r in results[-5:]:  # Last 5 results
        table_data.append([
            f"{r['n_max']}",
            f"{r['r2']:.6f}",
            f"{r['mae']:.4f}",
            f"{r['A']:.4f}",
            f"{r['B']:.4f}",
            f"{r['A_log']:.4f}"
        ])
    
    table = ax6.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 1.5)
    
    plt.suptitle('Spectral Law Coefficients vs Range Size (n_max)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    
    print("="*80)
    print("SCALABLE SPECTRAL LAW: Multi-Range Optimization")
    print("="*80)
    
    # Define ranges to test (adjust based on available cache)
    ranges = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    
    # Optimize for each range
    results = optimize_for_ranges(ranges, verbose=True)
    
    # Analyze scaling
    scaling = analyze_scaling(results)
    
    # Visualize
    plot_results(results, scaling)
    
    # Extrapolate for larger ranges
    print("\n" + "="*80)
    print("EXTRAPOLATION FOR LARGER RANGES")
    print("="*80)
    
    for n in [2000, 5000, 10000]:
        pred = extrapolate_coefficients(n, scaling['scaling'])
        print(f"\nn_max = {n}:")
        print(f"  A = {pred['A']:.6f}")
        print(f"  B = {pred['B']:.6f}")
        print(f"  A_log = {pred['A_log']:.6f}")
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    print("""
    DISCOVERED SCALING LAWS:
    
    A(n)     = {:.4f}·ln(n) + {:.4f}
    B(n)     = {:.4f}/ln(n) + {:.4f}
    A_log(n) = {:.4f}·ln(ln(n)) + {:.4f}
    
    These scaling laws allow extrapolation of coefficients
    to any desired range n_max!
    """.format(
        scaling['scaling']['A'][0], scaling['scaling']['A'][1],
        scaling['scaling']['B'][0], scaling['scaling']['B'][1],
        scaling['scaling']['A_log'][0], scaling['scaling']['A_log'][1]
    ))
    
    # Save results
    np.save('spectral_law_scaling.npy', results)
    print("✓ Results saved to 'spectral_law_scaling.npy'")