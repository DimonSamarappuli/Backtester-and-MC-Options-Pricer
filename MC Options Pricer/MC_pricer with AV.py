import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

n_sims = 1000000
bins = 100

def main():
    option_type = input("Select option type (call or put): ")
    MC_price_av, low_ci_av, high_ci_av, discounted_av = mc_pricer_av(100, 0.08, 1, n_sims, option_type)

    MC_price_no_av, low_ci_no_av, high_ci_no_av, discounted_no_av = mc_pricer_no_av(100, 0.08, 1, n_sims, option_type)

    BS_price = black_scholes_price(100, 100, 0.08, 0.2, 1, option_type)

    paths = simulate_gbm_paths(100, 0.08, 0.2, 1, n_steps=252, n_paths=250, seed=42)
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(13, 9))
    t = np.linspace(0, 1, 253)

    # t has to match 253: evenly spaced times from 0 to T.
    # paths.T flips array to (253, 100) through the T because plt.plot draws each column as one line, and you want one line per path.

    ax1.plot(t, paths.T, linewidth=0.8, alpha=0.6)
    ax1.axhline(100, color="black", linestyle="--", label="Strike, K")
    ax1.set_xlabel("Time / years")
    ax1.set_ylabel("Stock price")
    ax1.set_title("Simulated GBM paths")
    ax1.legend()

    simulation, theoretical_mean = gbm_hist_simulation(100, 0.08, 0.2, 1, n_sims, 42)
    simulated_mean = np.mean(simulation)
    print(f"Theoretical Mean: ${theoretical_mean:.4f}")
    print(f"Simulated Mean: ${simulated_mean:.4f}")
    print(f"Percentage Difference: "
          f"{((theoretical_mean - simulated_mean) / theoretical_mean) * 100:.4f}%")
    ax2.hist(simulation, bins=bins)
    ax2.set_xlabel("Stock Price")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Simulated GBM Price, Histogram")

    points_no_av, means_no_av, stds_no_av = plotter(n_sims, discounted_no_av)
    ax3.plot(points_no_av, means_no_av, label="MC estimation \n"
                                              "with no Antithetic Variation")
    ax3.fill_between(points_no_av, means_no_av - 1.96 * stds_no_av, means_no_av + 1.96 * stds_no_av, alpha=0.3, label="95% CI")
    ax3.axhline(BS_price, color="red", linestyle="--", label="Black-Scholes")
    ax3.set_xscale("log")
    ax3.set_xlabel("Number of simulations")
    ax3.set_ylabel(f"Option price, {option_type} option")
    ax3.set_title("MC convergence to Black-Scholes,\n no AV")
    ax3.legend()

    points_av, means_av, stds_av = plotter(n_sims, discounted_av)
    ax4.plot(points_av, means_av, label="MC estimation \n"
                                        "with Antithetic Variation")
    ax4.fill_between(points_av, means_av - 1.96 * stds_av, means_av + 1.96 * stds_av, alpha=0.3, label="95% CI")
    ax4.axhline(BS_price, color="red", linestyle="--", label="Black-Scholes")
    ax4.set_xscale("log")
    ax4.set_xlabel("Number of simulations")
    ax4.set_ylabel(f"Option price, {option_type} option")
    ax4.set_title("MC convergence to Black-Scholes,\n with AV")
    ax4.legend()

    plt.tight_layout()

    plt.savefig("mc_pricer with and without AV, and gbm paths.png", dpi=200)
    plt.show()
    # .legend() automatically detects different lines and titles them as per the "label=" given to each line


def gbm(S_0, r, sigma, T, n_sims, seed=None):
    rng = np.random.default_rng(seed=seed)
    z = rng.standard_normal(size=n_sims)
    S_plus = S_0 * np.exp((r - 0.5 * sigma**2) * T + sigma*np.sqrt(T) * z)
    S_minus = S_0 * np.exp((r - 0.5 * sigma ** 2) * T - sigma * np.sqrt(T) * z)
    drift_term = T * (r - (1 / 2) * sigma ** 2)  # From the GBM equation
    shock_term = sigma * np.sqrt(T) * z  # Also from the GBM equation
    S_T = S_0 * np.exp(drift_term + shock_term)
    return S_plus, S_minus, S_T

def mc_pricer_av(K, r, T, n_sims, option_type="call"):
    S_plus, S_minus, S_T = gbm(100, 0.08, 0.2, 1, n_sims, 42)
    if option_type.capitalize() == "Call":
        payoff_plus = np.exp(-r * T) * np.maximum(S_plus - K, 0)
        payoff_minus = np.exp(-r * T) * np.maximum(S_minus - K, 0)
    elif option_type.capitalize() == "Put":
        payoff_plus = np.exp(-r * T) * np.maximum(K - S_plus, 0)
        payoff_minus = np.exp(-r * T) * np.maximum(K - S_minus, 0)
    else:
        raise ValueError("option_type must be either 'call' or 'put'")

    pair_avg = (payoff_minus + payoff_plus) / 2
    price = pair_avg.mean()
    std_error = pair_avg.std(ddof=1) / np.sqrt(n_sims)

    # .std returns the standard deviation of an array
    # .std(ddof=1) divides by N-1 (√[ Σ(xᵢ − x̄)² / (N − 1) ])
    # This gives us the sample std rather than the population std

    low_ci = price - 1.96 * std_error
    high_ci = price + 1.96 * std_error

    print(f"Correlation Coefficient, p = {np.corrcoef(payoff_plus, payoff_minus)[0,1]:.4f}")
    return price, low_ci, high_ci, pair_avg

def mc_pricer_no_av(K, r, T, n_sims, option_type="call"):
    S_plus, S_minus, S_T = gbm(100, 0.08, 0.2, 1, n_sims, 42)
    if option_type.capitalize() == "Call":
        payoff = np.maximum(S_T - K, 0)
    elif option_type.capitalize() == "Put":
        payoff = np.maximum(K - S_T, 0)
    else:
        raise ValueError("option_type must be either 'call' or 'put'")

    discounted = np.exp(-r * T) * payoff
    price = discounted.mean()

    std_error = discounted.std(ddof=1) / np.sqrt(n_sims)

    # .std returns the standard deviation of an array
    # .std(ddof=1) divides by N-1 (√[ Σ(xᵢ − x̄)² / (N − 1) ])
    # This gives us the sample std rather than the population std

    low_ci = price - 1.96 * std_error
    high_ci = price + 1.96 * std_error

    return price, low_ci, high_ci, discounted

def black_scholes_price(S_0, K, r, sigma, T, option_type="call"):
    d1 = (np.log(S_0 / K) + T * (r + 1/2 * sigma**2)) / sigma * np.sqrt(T)
    d2 = (np.log(S_0 / K) + T * (r - 1/2 * sigma**2)) / sigma * np.sqrt(T)
    if option_type == "call":
        C_0 = S_0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return C_0
    elif option_type == "put":
        P_0 = K * np.exp(-r * T) * norm.cdf(-d2) - S_0 * norm.cdf(-d1)
        return P_0
    else:
        raise ValueError("option_type must be either 'call' or 'put'")

def plotter(n_sims, discounted):
    points = np.logspace(2, np.log10(n_sims), 50).astype(int)
    payoff_means = []
    payoff_stds = []
    for n in points:
        payoff_means.append(discounted[:n].mean())
        payoff_stds.append(discounted[:n].std(ddof=1) / np.sqrt(n))

    means = np.array(payoff_means)
    stds = np.array(payoff_stds)
    return points, means, stds

def simulate_gbm_paths(S_0, mu, sigma, T, n_steps, n_paths, seed=None):
    rng = np.random.default_rng(seed) # creates a random number generator object that can later be called
    dt = T / n_steps
    # What we are going to do is build the price path by chaining many small exact GBM steps together.
    # The GBM expression works over any time span so we reduce it to a shorter time span of dt of length T / n_steps
    # We then multiply the stock price, S_0, by the factor exp[(μ − σ²/2)·dt + σ √dt·Z]

    z = rng.standard_normal(size=(n_paths, n_steps))
    # A 2D array of independent Z draws are made as z, one row per path, one column per time step, giving 25,200 random numbers

    log_increments = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
    # The price at any time is S_0 multiplied by all exponents until then.
    # As exponent multiplication is addition, we can use cumsum

    paths = S_0 * np.exp(np.cumsum(log_increments, axis=1))
    # cumsum sums each increment from dt along each path

    return np.hstack([np.full((n_paths, 1), S_0), paths])
    # np.full((rows, columns), fill_value)
    # np.full makes an array of designated rows and columns, and fills each value with the fill value
    # np.hstack(tuple) takes in a list, array or tuple, and joins them side by side horizontally.
    # the h in the name stands for horizontal

def gbm_hist_simulation(S_0, mu, sigma, T, n_sims, seed=None):
    rng = np.random.default_rng(seed=seed)
    z = rng.standard_normal(size=n_sims)
    drift_term = T * (mu - (1 / 2) * sigma ** 2) # From the GBM equation
    shock_term = sigma * np.sqrt(T) * z # Also from the GBM equation
    S_T = S_0 * np.exp(drift_term + shock_term)
    theoretical_mean = S_0 * np.exp(mu * T) # Mean of GBM
    return S_T, theoretical_mean

if __name__ == "__main__":
    main()