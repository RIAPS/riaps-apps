import zmq
import libs.config as cfg

grid = zmq.Context().socket(zmq.REQ)
grid.connect('tcp://%s:5555' %cfg.GRID)
print("cfg.GRID: %s" %cfg.GRID)



power = 10000

for i in range(16):

    if power < 20000:
        power = power+1000
    else:
        power = power-500

    msg = {"request":"charge",
           "ID" : str(102),
           "interval": i}
    grid.send_pyobj(msg)
    response = grid.recv_pyobj()

    # perUnitCharge = response['perUnitCharge'].split(" ")[0][1:]
    # charge = cfg.CAPACITY * float(perUnitCharge)

    perUnitCharge = response['perUnitCharge']
    charge = cfg.CAPACITY * perUnitCharge

    battCMD = response['battCMD']

    solarActual = response['solarActual']

    battActual = response['battActual']

    print("charge: %s" %charge)
    print("battCMD: %s" %battCMD)
    print("solarActual: %s" %solarActual)
    print("battActual: %s" %battActual)

    print("charge: %s" %type(charge))
    print("battCMD: %s" %type(battCMD))
    print("solarActual: %s" %type(solarActual))
    print("battActual: %s" %type(battActual))

    print('Power: %s' %power)

    msg = {"request": "postTrade",
           "interval" :i,
           "power" : power,
           "ID" : str(102)
           }
    grid.send_pyobj(msg)
    response = grid.recv_pyobj()
    print(response)

    msg = {"request": "step",
           "interval" : i}
    grid.send_pyobj(msg)
    response = grid.recv_pyobj()
    print(response)

    print("\n")
