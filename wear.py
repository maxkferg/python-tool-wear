import pandas
import numpy as np
import matplotlib.pyplot as plt

wear = {}
wear[1] = [0,40,80] # Done
wear[2] = [0,60,70,80,90,95,96,97,98,99,100] # Done
wear[3]= [0,20,40,45,50,55,65,70,75,80,86,90,94] # Done
wear[4] = [0,8,16,24,35,60,65,70,82] # Done
wear[5] = [0,50,80] # Done
wear[6] = [0,40,60,80] # Done
wear[7] = [0,50,60,70,75,85] # Done
wear[8] = [0,7,15,20,30,33,34,35,36,38,40,43,46,49,52,55] # Done
wear[9] = [0,100]
wear[10] = [0,20,25,30,35,37,39,43,45,47,50,55] # Done
wear[11] = [0,10,20,25,30,35,50,60,65,80,85,90] # Done
wear[12] = [0,10,20,30,35,60,70,80] # Done
wear[13] = [0,40] # Done
wear[14] = [0,10,50] # Done
wear[15] = [0,30,60]
wear[17] = [0,10,40]
wear[18] = [0,20,50,65]
wear[19] = [0,10,20,40,55,60,65,80]
wear[20] = [0,11,30,60,70,75] # Strange behavior at 20
wear[21] = [0,25,50,80,90,95]
wear[22] = [0,13,40,65,70,80]
wear[23] = [0,12,20,50,55,60]
wear[25] = [0,10,70] # Done
wear[26] = [0,5,10,20,90] # Done
wear[27] = [80,90] # Done. Broken from start
wear[28] = [0,10,35,50,75] # Done
wear[29] = [0,10,40,60,70,85] # Done


def get_wear(tool,n):
    xp = range(len(wear[tool]))
    fp = wear[tool]
    x = np.linspace(0,max(xp),n)
    return np.interp(x, xp, fp)


for tool in wear.keys():
    filename = "data/Metadata/metadata{tool}.csv".format(tool=tool)
    metadata = pandas.read_csv(filename,index_col='index')
    n = len(metadata.index)
    toolwear = get_wear(tool,n)
    metadata['tool_wear'] = toolwear
    # Plotting
    plt.figure()
    plt.plot(metadata.index, metadata.tool_wear)
    plt.xlabel('Cut Number')
    plt.ylabel('Tool Wear')
    plt.title('Tool Wear for Tool %i'%tool)
    plt.ylim([0,100])
    print(metadata)
    # Uncomment to write new tool wear values to the metadata files
    metadata.to_csv(filename+'x',index_label='index')

plt.show()



