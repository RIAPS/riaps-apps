#What do we need to do?
#We have dataframes from all the PMUs. Now we need to return a matrix of V and I, containing the measurements of V and I for all the required thaings

V_LEN = 14
I_LEN = 25

PMU_PHASOR_MAP = {1: ([1, 10, 11], [1, 2, 3]), 2: ([2, 12, 13], [4, 5, 6]), 3: ([3, 14], [7, 8, 9]), 4: ([4], [10, 11, 12]), 5: ([5], [13, 14, 15]), 6: ([6], [16, 17, 18]), 7: ([7], [19, 20, 22]), 8: ([8], [23, 24, 25]), 9: ([9], [21])}


def get_V_I(dataframes):
    #Data frames of all the PMUs as input
    V = [None for i in range(V_LEN)]
    I = [None for i in range(I_LEN)]
    for j in range(len(dataframes)):
        #We have a funtion get_phasor(frame, phasor_num) that can get a phasor from the frame
        pmu_id = j + 1
        frame = dataframes[j]
        # Now get all the voltage phasors from this dataframe
        # How do we do this?
        # First, which voltage phasors are in this dataframe?
        # Create a dict that helps find this
        # then, extract these phasors and put them in the arrays
        voltage_phasors, current_phasors = PMU_PHASOR_MAP[pmu_id]
        for i in range(len(voltage_phasors)):
            V_index = voltage_phasors[i]
            V[V_index] = get_phasor(dataframe, i)

        for i in range(len(current_phasors)):
            I_index = current_phasors[i]
            I[I_index] = get_phasor(dataframe, i + len(voltage_phasors))

    return V, I
