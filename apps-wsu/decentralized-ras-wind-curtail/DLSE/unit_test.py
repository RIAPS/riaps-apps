from pmu_connection import PMUConnection
import time

pmu_connection = PMUConnection()
time.sleep(3)
print(pmu_connection.get_dframes())
pmu_connection.close()
