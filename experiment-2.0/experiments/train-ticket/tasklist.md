# Tasks list for week 10/30
1. analysis on train-ticket results
  - get the stats for each node
    - number of inward and outward edges DONE
    - number of unique request patterns for each service DONE
      - for each request pattern, when is the particular node accessed
    - individual graphs for each request patterns
  - notes:
    - number of unique request pattern is unrealistic in history data 3 and 4 even after considering duplicate invocation and order of invocation
    - considering that only 16 unique patterns goes through the gateway, it is suspected that the history data was generated using direct access to each endopoints
