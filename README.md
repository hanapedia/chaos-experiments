# Chaos Experiments
This project automates chaos test manifest generation and application via ansible

## Types of chaos experiments
### K8s Performance anomalies
- CPU stress
- memory stress
  - *memory stress can be distinguished from CPU stress as it does not apply read and write pressure*
- network latency delay
  - *uses Istio fault injection*
- file I/O stress
- spiked traffic
### K8s Functional Faults
- DNS wrong response
- HTTP interception
- K8s pod failure
### Physical machine anomalies/faults
- process failure
- network latency delay, packet loss
- hardware pressure
- machine shutdown

## Description
This project uses Chaos Mesh for fault injection.  
The custom resource for chaos mesh experiments are generated from templates using jinja2 templates.   
The custom resource manifests are applied via ansible
