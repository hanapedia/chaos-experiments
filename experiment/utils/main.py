import pickle
import unittest
from pathlib import Path

class UtilTests(unittest.TestCase):
    def test_invo_serialization(self):
        input_dir = Path("../generated/chain_fanout") 
        variant = "chc5s"
        filename = "chain-1_delay_1.pkl"
        variant = "foc5s"
        filename = "fanout-1_delay_1.pkl"
        input_file = input_dir / variant / "datasets" / "injected" / filename

        traces = []
        with open(input_file, "rb") as f:
            traces = pickle.load(f)

        self.check_invo_serialization(traces)

    def check_invo_serialization(self, traces: list):
        for trace in traces:
            for s, t in trace["s_t"]:
                print(s, t)

if __name__ == "__main__":
    unittest.main()
