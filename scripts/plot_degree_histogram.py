import pickle

import matplotlib.pyplot as plt


with open('results/graphs/end4.pck') as f:
    end4 = pickle.load(f)

# Clear figure in case of multiple runs during the same session.
plt.clf()
degree_dict = end4.degree()
bins = 8
plt.hist(degree_dict.values(), bins)
plt.ylabel('Frequency')
plt.xlabel('Degree')
plt.savefig('results/figures/end4_degree_%d.pdf' % bins)
#plt.show()
