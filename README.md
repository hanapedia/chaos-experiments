# Chaos Experiments
This project automates chaos test manifest generation and application via ansible

## Usage for experiment-1.0
1. create  experiment configuration files in yaml
2. Generate experiment
```
cd experiment-1.0
ansible-playbook generate_experiment.yaml --extra-vars "config_file=./path/to/config.yaml"
cd ./path/to/generated-experiment
ansible-playbook experiment_script.yaml
```

## Types of chaos experiments
*only network delay is implemented*
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
