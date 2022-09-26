# Experiment versions
## v1 and v2
- istio fault injection for latency and cpu stress
## v3
- chaos mesh network delay
### Fault details
- 30ms
- both directions
- 60s
### RCA details
- 3min normal
- 1min anomaly
- ad_threshold = 0.05

## v4
- chaos mesh network delay
- variational ad_threshold and alpha values
### Fault details
- 30ms
- both directions
- 60s
### RCA details
- 3min normal
- 1min anomaly
- ad_threshold = 0.01, 0.03, 0.07
- alpha = 0.55, 0.3, 0.8

