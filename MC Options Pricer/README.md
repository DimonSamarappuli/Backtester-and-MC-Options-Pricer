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
| Monte-Carlo (without antithetic variates) | $12.1081 | 0.0156 | [$12.0775, $12.1386] |
| Monte-Carlo (with antithetic variates) | $12.1081 | 0.0071 | [$12.0941, $12.1220] |


<img width="1127" height="673" alt="image" src="https://github.com/user-attachments/assets/d1b5519c-dd40-4942-b290-261f1ac394e8" />


| Method | Put price | Standard Error | 95% Confidence Interval |
| --- | --- | --- | --- |
| Black-Scholes | $4.42 | n/a | n/a |
| Monte-Carlo (without antithetic variates) | $4.4159 | 0.0077 | [$4.4090, $4.4263] |
| Monte-Carlo (with antithetic variates) | $4.4177 | 0.0077 | [$4.4009, $4.4309] |


<img width="1127" height="674" alt="image" src="https://github.com/user-attachments/assets/f8ab53b2-b6ae-4494-bfe7-d6640b084f77" />


Panels, left to right: 
(1) simulated GBM price paths against the strike K; 
(2) histogram of simulated terminal prices, right-skewed and strictly positive as a lognormal should be; 
(3) running Monte Carlo call/put price estimate with its 95% confidence band converging on the Black-Scholes price (dashed red line), without antithetic variates; 
(4) the same convergence plot with antithetic variates. In both convergence panels the
band narrows as N grows, consistent with the 1/√N rate, and in panel 4 the band is visibly narrower at small, N.

## Mathematical Background
This section summarises the theory the project is built on.

### Random Walks

A simple random walk is a sum of independent steps. Its variance grows linearly with the number of steps. As time is sped up by a factor of n, the walk rescales and converges to a continuous random process, Brownian motion. The scaling limit is why variance growing in proportion to time, and standard deviation growing like √T, is the foundational feature of everything to follow.
<img width="928" height="323" alt="image" src="https://github.com/user-attachments/assets/976d3af0-24fb-4d38-a699-fcf30940e2c6" />

### Brownian Motion (the Wiener process)

<img width="874" height="524" alt="image" src="https://github.com/user-attachments/assets/c1e417e0-a472-4912-a6ca-20dd0b48004c" />

### Arithmetic Brownian Motion (ABM)

<img width="539" height="474" alt="image" src="https://github.com/user-attachments/assets/76eadb60-82ca-4ade-988b-1b3d8060da47" />

<img width="597" height="512" alt="image" src="https://github.com/user-attachments/assets/3575b111-a323-4394-85bf-f8e6e41056fa" />

The change in X is additive and normally distributed, so X can become negative, which makes it a poor model for stock pricing, which is the motivation for GBM.

<img width="487" height="190" alt="image" src="https://github.com/user-attachments/assets/5a4e4184-d718-425a-adf7-b5ca7e8387ec" />

### Geometric Brownian Motion (GBM)

GBM makes the percentage change in price random rather than the absolute change.
<img width="1054" height="398" alt="image" src="https://github.com/user-attachments/assets/312757df-c2f2-42e3-bf0b-f3c235751b41" />

<img width="738" height="518" alt="image" src="https://github.com/user-attachments/assets/a19c1407-cde0-4582-80a8-f921224e855a" />

<img width="742" height="524" alt="image" src="https://github.com/user-attachments/assets/fafb4b07-57fb-4f6b-ad9a-7301a6183b3d" />

<img width="873" height="529" alt="image" src="https://github.com/user-attachments/assets/187dc289-5e5a-4df8-bf1d-7f94e4002d4c" />

<img width="655" height="498" alt="image" src="https://github.com/user-attachments/assets/76b173bd-2983-4fae-b440-a3fe49035d70" />

<img width="776" height="460" alt="image" src="https://github.com/user-attachments/assets/a260c3da-634e-4dc0-9436-59f8445791ed" />
The key properties of a GBM model is:
1) S_T is lognormal, it is always positive and skewed to the right.
2) The mean of a GBM model is given by: E[ST] = S₀eμT.
3) Due to the solution being closed-form, a price can be sampled in one step from S_0 to S_T. Time stepping schemes such as Euler-Maruyama are only needed for SDE's without a closed-form.


<img width="476" height="515" alt="image" src="https://github.com/user-attachments/assets/253aea1b-5cf3-43d2-a4b0-eaa46af8f656" />



### Risk-neutral option pricing
The price of a derivative is not the discounted real-world expected payoff. The actual price is given by:
<img width="157" height="33" alt="image" src="https://github.com/user-attachments/assets/8a24ffa6-772d-4536-9f95-ba87e4253c9d" />


where under the risk neutral measure Q, the stock drifts at the risk free rate r rather than at μ.

The reason for this is replication. As the portfolio of the stock and a riskless bond can be continuously rebalanced to reproduce the option's payoff in every scenario, so no-arbitrage will force the option to cost the same as the portfolio. The cost of the portfolio is independent of μ so simulating it under drift r and discounting at r is the shortcut that computes the replication cost. 
<img width="811" height="215" alt="image" src="https://github.com/user-attachments/assets/77697adf-e27e-4073-8a7a-a15bbb3c7dff" />

<img width="823" height="496" alt="image" src="https://github.com/user-attachments/assets/c05cac74-dd70-41c4-a351-5360e4a16696" />

<img width="839" height="506" alt="image" src="https://github.com/user-attachments/assets/1d33ebe7-e124-45f9-8f84-224ff2db3b89" />
<img width="1004" height="162" alt="image" src="https://github.com/user-attachments/assets/608dffc9-8a8a-46d4-8e0b-e5cf9f61d360" />

### Deriving the Black-Scholes formula
For this derivation, we make the following assumptions: The GBM for the underlying has a constant σ, a constant risk-free rate r, no dividends, no transaction costs, continuous trading and no arbitrage.

<img width="997" height="527" alt="image" src="https://github.com/user-attachments/assets/2c6a4980-80e8-4dd3-a6ec-de733dba0298" />
<img width="826" height="512" alt="image" src="https://github.com/user-attachments/assets/88d2c256-b800-4d64-9108-120c03ff79cd" />
<img width="953" height="442" alt="image" src="https://github.com/user-attachments/assets/0d869b7d-a097-45f6-92da-debcd43b129e" />
<img width="596" height="491" alt="image" src="https://github.com/user-attachments/assets/b6e9d017-ab83-463c-92f4-982048df17d7" />


### Putting Black-Scholes into practice


In practice the model is therefore used in two ways:
- Forward : given an estimate of volatility, compute a theoretical fair value and compare it with the market price.
- Inverse : find the sigma value that makes the model price equal the observed market price. The implied volatility is then a market-quoted measure of expected future volatility, and comparing it with the realised volatility is the basis of many volatility trades.

<img width="917" height="332" alt="image" src="https://github.com/user-attachments/assets/396a1f92-737d-41fb-9297-9c409aa70013" />
<img width="769" height="515" alt="image" src="https://github.com/user-attachments/assets/2cb8917d-0735-4897-b9be-510053b844a3" />

This project does not implement volatility or the Greeks as it prices a single option under fixed inputs.

### Put-Call Parity

<img width="1084" height="403" alt="image" src="https://github.com/user-attachments/assets/07a453f7-ca20-4301-ac77-4c5255cffedd" />

The Put-Call parity is a risk-free identity. If it failed, buying the cheap side and selling the expensive side would guarantee a risk-free profit with zero net payoff at expiry, and trading would close the gap. 

### The Central Limit Theorem 

<img width="919" height="500" alt="image" src="https://github.com/user-attachments/assets/6cf78871-211d-48a3-8e0e-eecb6e81016c" />

<img width="755" height="456" alt="image" src="https://github.com/user-attachments/assets/f27ab33d-eddd-47fb-ab83-ee263a5bd52d" />

<img width="914" height="234" alt="image" src="https://github.com/user-attachments/assets/8cb92c36-aa06-47f0-858e-a4901c5626d6" />

### Why Monte-Carlo Simulation works

<img width="835" height="512" alt="image" src="https://github.com/user-attachments/assets/e6bc6bd7-7b6c-470b-8242-e2d40f9ff4c5" />

<img width="926" height="512" alt="image" src="https://github.com/user-attachments/assets/08e296d4-745b-4e9d-b3d7-3bad36ca27c8" />

<img width="962" height="404" alt="image" src="https://github.com/user-attachments/assets/c440bc81-a456-4043-b26d-0699f2418b71" />

### Random number generation: inverse transform and NumPy

<img width="660" height="487" alt="image" src="https://github.com/user-attachments/assets/494cc73d-4c19-4ed2-9d73-f40ecc5de4be" />

In practice, the project uses NumPy's modern Generator API:
rng = np.random.default_rng(seed=42)
z = rng.standard_normal(size=n_sims)

default_rng is recommended over the legacy interface, and a fixed seed makes draws reproducible, which was essential for debugging. NumPy's standard-normal uses a faster algorithm internally than literal inverse transform , but both produce the same distribution.

### Variance reduction using Antithetic Variates

<img width="917" height="509" alt="image" src="https://github.com/user-attachments/assets/6ac95e5e-5f0d-47ef-b22c-e50b548a2703" />

<img width="586" height="511" alt="image" src="https://github.com/user-attachments/assets/3e53adac-b21d-4af6-bc7c-74bfc296c439" />

<img width="779" height="232" alt="image" src="https://github.com/user-attachments/assets/9505b178-fa0f-491a-a025-8ddd3fdb9bdf" />

The independent units are N/2 pair averages, so the standard error must be computed from those, not from all N payoffs treated as independent.

## Implementation









