# Test file to check recent functionality
import datetime

def test_function():
    """This is a test function created recently"""
    now = datetime.datetime.now()
    print(f"Current time: {now}")
    return now

if __name__ == "__main__":
    test_function()