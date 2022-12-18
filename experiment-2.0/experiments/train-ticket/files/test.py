from analysis import TraceRcaAnalysis
from pprint import pprint
def main():
    tra = TraceRcaAnalysis(experiment_name='microservice_faults_filtered')
    tra.format_data()

if __name__ == "__main__":
    main()
