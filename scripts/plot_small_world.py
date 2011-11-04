import matplotlib.pyplot as plt

# Clear the figure in case of multiple runs in the same session.
plt.clf()

end4 = plt.plot(2.1240, 0.5243, 'ro')
rand4_con = plt.plot(2.0166, 0.3973, 'bo')
plt.errorbar(2.0166, 0.3973, xerr=0.0098, yerr=0.0095)
lat4_con = plt.plot(2.0332, 0.4933, 'ko')
plt.errorbar(2.0332, 0.4933, xerr=0.0097, yerr=0.0109)
plt.ylabel('Clustering coefficient')
plt.xlabel('Characteristic path length')
plt.legend((end4, rand4_con, lat4_con),
           ('CoCoMac in PHT00 space', 'Random', 'Lattice'), 'right',
           numpoints=1)
plt.savefig('results/figures/smallworld_end4.png')
plt.show()
