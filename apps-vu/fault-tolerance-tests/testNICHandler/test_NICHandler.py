"""RIAPS NIC Handler test
"""
from riaps_testing import runTest

def verifyResults(results):
    """Verify that test results match the expected behavior of the Pub Sub model

    Parses the returned log files to find all messages send by each publisher. Then asserts that
    each message sent by each publisher was received by each subscriber.

    Args:
        results (dictionary): A dictionary in the format provided by riaps_testing.runTest(...)
        numPub  (int): The number of expected publishers
        numSub  (int): The number of expected subscribers

    """
    # Parse log files
    numNICcalls = 0
    for key in results.keys():
        keyword = ""
        if key.find("Req") != -1:
            keyword = "Request"
        elif key.find("Nic") != -1:
            keyword = "RESULT"
        else:
            assert(False), "Unknown key %s" % key
        if keyword != "":
            assert results[key][0].find("Starting") != -1, "First line of %s isn't starting!" % key
            assert results[key][-1].find("Stopping") != -1, "Last line of %s isn't stopping!" % key
        if keyword == "Request":
            for line in results[key]:
                if line.find("NIC State Change") != -1:
                    numNICcalls += 1

    assert numNICcalls > 0, "NIC Handler not called!"


def test_NICHandler():
    verifyResults(runTest("TestNICHandler", "testNICHandler", "nic.riaps", "nic.depl"))
