import matplotlib.pyplot as plt

# Clear the figure in case of multiple runs in the same session.
plt.clf()

end4 = plt.plot(2.1240, 0.5243, 'ro')
rand3 = plt.plot(1.8926, 0.1501, 'bo')
plt.errorbar(1.8926, 0.1501, xerr=0.0029, yerr=0.0017)
latt3 = plt.plot(4.7407, 0.7341, 'ko')
plt.errorbar(4.7407, 0.7341, xerr=0.0111, yerr=3.1783 * 10 ** -4)
plt.ylabel('Clustering coefficient')
plt.xlabel('Characteristic path length')
plt.legend((end4, rand3, latt3),
           ('CoCoMac in PHT00 space', 'Random', 'Lattice'), 'right',
           numpoints=1)
plt.savefig('results/figures/smallworld_end4.pdf')
plt.show()
