# Monte-Carlo Options Pricer benchamarked against the Black-Scholes Model
## 1. Project Overview
This project is a Python implementation of a Monte-Carlo pricer for European call and put options. It simulates the stock under risk-neutral pricing, following a Geometric Brownian motion model, then computes the price as a discounted average payoff, before attaching a 95% confidence interval to it and validating the result against the price from the Black-Scholes model.

This pricer was built bottom up, which includes learning the stochastic processes, the pricing theory and the Mathematics that ties it all together, before then translating each section into vectorised NumPy code.

## 2. Contents
- Features
- Results
- Mathematical Foundations
- Implementation Theory
- Validation
- Limitations
- Learning log and references



