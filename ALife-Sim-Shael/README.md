This is a summary of the repo.


I learned how the repo worked by generating a robot with run.py and visualizing its success with the visualize.

In Play with Alife-Sim.mov, I experiment with using the simulator to generate and visualize a robot. This robot is not evoloved or trained to be fit, and represents a "baseline" before the evolution done later.

In Parallel Hill Climber, I write code to locally evolve a set of randomly generated robots independent from one another. Evolution is accomplished using a random mutation algorithm. The fitness of each family is plotted over time, and a video of the fittest final robot is enclosed.

In Genetic Algorithm, I write code to evolve randomly generated robots against one another, similar to natural selection. Evolution is accomplished by mutating and then discarding a bottom percentage (evaluated on fitness). The fitness of the best, mean, and worst robots is plotted over time, and a video of the fittest final robot is enclosed.