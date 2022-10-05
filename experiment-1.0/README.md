# Fault injection version 1.0
## Details
### Injected faults
<!-- - Http network delay for services with http endpoints -->
<!--   - 200ms delay -->
<!-- - CPU or memory stress for services without http endpoints -->
<!--   - 95% CPU usage -->
- network delay

### Duration
- 4 minutes per fault
  - 1 minute for fault injection
  - 3 minutes without faults

### Additional Information
- save fault service and timestamps for experiment start and end time in separate text files
  - use them for root cause analysis
- use ansible for generating ansible playbook for the experiment
