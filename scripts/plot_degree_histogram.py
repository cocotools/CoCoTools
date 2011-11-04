import pickle

import matplotlib.pyplot as plt

from cocotools import get_degree_histogram, plot_degree_histogram


with open('results/graphs/end4.pck') as f:
    end4 = pickle.load(f)

# Clear figure in case of multiple runs during the same session.
plt.clf()
degree_dict = end4.degree()
plt.hist(degree_dict.values(), 20)
plt.ylabel('Frequency')
plt.xlabel('Degree')
plt.savefig('results/figures/end4_degree.png')
plt.show()
