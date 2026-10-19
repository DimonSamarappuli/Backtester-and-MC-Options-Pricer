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

1. Random Walks

A simple random walk is a sum of independent steps. Its variance grows linearly with the number of steps. As time is sped up by a factor of n, the walk rescales and converges to a continuous random process, Brownian motion. The scaling limit is why variance growing in proportion to time, and standard deviation growing like √T, is the foundational feature of everything to follow.
<img width="928" height="323" alt="image" src="https://github.com/user-attachments/assets/976d3af0-24fb-4d38-a699-fcf30940e2c6" />

2. Brownian Motion (the Wiener process)

<img width="874" height="524" alt="image" src="https://github.com/user-attachments/assets/c1e417e0-a472-4912-a6ca-20dd0b48004c" />

3. Arithmetic Brownian Motion (ABM)

<img width="539" height="474" alt="image" src="https://github.com/user-attachments/assets/76eadb60-82ca-4ade-988b-1b3d8060da47" />

<img width="597" height="512" alt="image" src="https://github.com/user-attachments/assets/3575b111-a323-4394-85bf-f8e6e41056fa" />

The change in X is additive and normally distributed, so X can become negative, which makes it a poor model for stock pricing, which is the motivation for GBM.

<img width="487" height="190" alt="image" src="https://github.com/user-attachments/assets/5a4e4184-d718-425a-adf7-b5ca7e8387ec" />

4. Geometric Brownian Motion (GBM)

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

5. Risk-neutral options pricing
The price of a derivative is not the discounted real-world expected payoff. The actual price is given by:
<img width="157" height="33" alt="image" src="https://github.com/user-attachments/assets/8a24ffa6-772d-4536-9f95-ba87e4253c9d" />
where under the risk neutral measure Q, the stock drifts at the risk free rate r rather than at μ.

<img width="811" height="215" alt="image" src="https://github.com/user-attachments/assets/77697adf-e27e-4073-8a7a-a15bbb3c7dff" />

<img width="823" height="496" alt="image" src="https://github.com/user-attachments/assets/c05cac74-dd70-41c4-a351-5360e4a16696" />

<img width="839" height="506" alt="image" src="https://github.com/user-attachments/assets/1d33ebe7-e124-45f9-8f84-224ff2db3b89" />
<img width="1004" height="162" alt="image" src="https://github.com/user-attachments/assets/608dffc9-8a8a-46d4-8e0b-e5cf9f61d360" />



