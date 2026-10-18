# Monte-Carlo Options Pricer benchmarked against the Black-Scholes Model
## Project Overview
This project is a Python implementation of a Monte-Carlo pricer for European call and put options. It simulates the stock under risk-neutral pricing, following a Geometric Brownian motion model, then computes the price as a discounted average payoff, before attaching a 95% confidence interval to it and validating the result against the price from the Black-Scholes model.

This pricer was built bottom up, which includes learning the stochastic processes, the pricing theory and the Mathematics that ties it all together, before then translating each section into NumPy code.

## Contents
- Features
- Results
- Mathematical Foundations
- Implementation Theory
- Validation
- Limitations
- Learning log and references

## Features
**GBM price simulator** : draws N prices in a single vectorised expression from a normal distribution, using NumPy, using the exact closed form GBM Solution

**Monte-Carlo Pricer** : applied on European call and put options, where they can only be exercised at expiry, with discounting under the risk-neutral measure.

**95% Confidence interval** : computed from the standard error of the discounted payoffs.

**Convergence plots, with and without antithetic variates** : MC estimate and the 95% confidence interval against the number of simulations and the Black-Scholes price as a reference line, with and without antithetic variates, side by side.

**GBM path simulator and plot** : stepwise simulation of full  price paths (only 250 paths shown) for visualisation.

**GBM Histogram simulation** : a separate function (gbm_hist_simulation) that draws the same amount of simulations as the GBM price simulator for the MC pricer and returns them as a histogram plot with the theoretical GBM mean calculated. This is used to check the lognormal nature of the simulated distribution.

**Antithetic Variates** : Variance reduction technique which employs the use of the Z as well as the -Z value drawn by the GBM simulator, and that they are negatively correlated. Two plots with and without Antithetic Variates is shown to compare the effect, at the same number of simulations.

## Results

| Parameter | Value |
| --- | --- |
| Spot price, S_0 | 100 |
| Strike price, K | 100 |
| Risk-free rate, r | 0.08 |
| Volatility, σ | 0.2 |
| Maturity T (years) | 1 |
| Simulations, N | 1 000 000 |

| Method | Call price | Standard Error | 95% Confidence Interval |
| --- | --- | --- | --- |
| Black-Scholes | $12.11 | n/a | n/a |
| Monte-Carlo (without antithetic variates) | 12.1081 | 0.0156 | [12.0775, 12.1386] |
| Monte-Carlo (with antithetic variates) | 12.1081 | 0.0071 | [12.0941, 12.1220] |

<img width="1127" height="673" alt="image" src="https://github.com/user-attachments/assets/d1b5519c-dd40-4942-b290-261f1ac394e8" />

| Method | Put price | Standard Error | 95% Confidence Interval |
| --- | --- | --- | --- |
| Black-Scholes | $4.42 | n/a | n/a |
| Monte-Carlo (without antithetic variates) | 4.4159 | 0.0077 | [4.4090, 4.4263] |
| Monte-Carlo (with antithetic variates) | 4.4177 | 0.0077 | [4.4009, 4.4309] |

<img width="1127" height="674" alt="image" src="https://github.com/user-attachments/assets/f8ab53b2-b6ae-4494-bfe7-d6640b084f77" />

