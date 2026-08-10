import sys
sys.path.append("src")
from scout.sources.manager import SourceManager

def test():
    print("Testing SourceManager ingestion...")
    sm = SourceManager()
    sm.run_all()

if __name__ == "__main__":
    test()
