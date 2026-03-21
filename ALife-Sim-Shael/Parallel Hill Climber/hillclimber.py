# # Derived from run.py
# # Uses a parallel hill climber scheme to evolve robots into fitter robots 


from simulator import Simulator
from utils import load_config
from argparse import ArgumentParser
from robot import load_robots, mutate_robot   # ===== MODIFIED =====
import numpy as np
import matplotlib.pyplot as plt

n_iterations = 4


# ===== NEW =====
def evaluate_robots(robots, config):
    """
    Runs simulator training and returns final fitness for each robot.
    """

    num_masses = [robot["n_masses"] for robot in robots]
    num_springs = [robot["n_springs"] for robot in robots]

    max_num_masses = max(num_masses)
    max_num_springs = max(num_springs)

    config["simulator"]["n_masses"] = max_num_masses
    config["simulator"]["n_springs"] = max_num_springs

    simulator = Simulator(
        sim_config=config["simulator"],
        taichi_config=config["taichi"],
        seed=config["seed"],
        needs_grad=True
    )

    masses = [robot["masses"] for robot in robots]
    springs = [robot["springs"] for robot in robots]

    simulator.initialize(masses, springs)

    fitness_history = simulator.train()

    fitness = fitness_history[:, -1]

    return fitness


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--config", type=str, default="config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)

    np.random.seed(config["seed"])

    # ===== INITIAL POPULATION =====
    parents = load_robots(num_robots=config["simulator"]["n_sims"])

    print("Evaluating initial parents...")
    parent_fitness = evaluate_robots(parents, config)

    # Store fitness history for plotting
    fitness_history = [parent_fitness.copy()]

    # ===== EVOLUTION LOOP =====
    for iteration in range(n_iterations):

        print(f"\n=== ITERATION {iteration} ===")
        print("Parent fitness:", parent_fitness)

        # ---- Create children ----
        children = [mutate_robot(robot) for robot in parents]

        print("Evaluating children...")
        child_fitness = evaluate_robots(children, config)

        # ---- Selection (parallel hill climbing) ----
        for i in range(len(parents)):
            if i == 0:
                print(f"Robot 0 parent fitness: {parent_fitness[i]:.6f}")
                print(f"Robot 0 child fitness:  {child_fitness[i]:.6f}")

            if child_fitness[i] > parent_fitness[i]:
                if i == 0:
                    print("Robot 0 ACCEPTED child")
                parents[i] = children[i]
                parent_fitness[i] = child_fitness[i]
            else:
                if i == 0:
                    print("Robot 0 rejected child")

        print("Best fitness this iteration:", np.max(parent_fitness))
        print("Stored fitness robot 0:", parent_fitness[0])

        fitness_history.append(parent_fitness.copy())

    # ===== END EVOLUTION LOOP =====

    # ===== FINAL EVALUATION =====
    print("\nFinal evaluation of population...")
    final_fitness = evaluate_robots(parents, config)

    # Rank robots
    ranking = np.argsort(final_fitness)[::-1]
    ranked_robots = [parents[i] for i in ranking]

    top_3_idxs = ranking[:3]
    top_3_robots = [parents[i] for i in top_3_idxs]

    # ===== TRAIN SIMULATOR ON FULL POPULATION (for control params) =====
    simulator = Simulator(
        sim_config=config["simulator"],
        taichi_config=config["taichi"],
        seed=config["seed"],
        needs_grad=True
    )

    simulator.initialize(
        [r["masses"] for r in parents],
        [r["springs"] for r in parents]
    )
    simulator.train()

    # ===== SAVE TOP 3 ROBOTS (existing behavior) =====
    top_3_control_params = simulator.get_control_params(top_3_idxs)

    for i in range(3):
        robot = top_3_robots[i]
        control_params = top_3_control_params[i]

        robot["control_params"] = control_params
        robot["max_n_masses"] = config["simulator"]["n_masses"]
        robot["max_n_springs"] = config["simulator"]["n_springs"]

        np.save(f"robot_{i}.npy", robot)

    # =========================================================
    # ===== NEW: SAVE BEST-PERFORMING ROBOT ===================
    # =========================================================

    # Find best robot index based on final fitness
    best_idx = np.argmax(final_fitness)
    best_robot = parents[best_idx]

    print(f"\nBest robot index: {best_idx}")
    print(f"Best fitness: {final_fitness[best_idx]:.6f}")

    # Extract its control parameters (already trained simulator)
    best_control_params = simulator.get_control_params([best_idx])[0]

    # Attach metadata
    best_robot["control_params"] = best_control_params
    best_robot["max_n_masses"] = config["simulator"]["n_masses"]
    best_robot["max_n_springs"] = config["simulator"]["n_springs"]
    best_robot["fitness"] = final_fitness[best_idx]

    # Save to file
    np.save("best_robot.npy", best_robot)

    print("Best robot saved to best_robot.npy")

    # =========================================================

    print("\nEvolution complete.")

    # ===== PLOTTING =====
    fitness_history = np.array(fitness_history)
    iterations = np.arange(fitness_history.shape[0])

    plt.figure()

    for i in range(fitness_history.shape[1]):
        plt.plot(iterations, fitness_history[:, i], label=f"Robot {i}")

    plt.xlabel("Iteration")
    plt.ylabel("Fitness")
    plt.title("Parallel Hill Climber Fitness Over Time")
    plt.legend()
    plt.grid(True)

    if n_iterations >= 20:
        plt.xticks(np.arange(0, len(iterations), 5))
    else:
        plt.xticks(iterations)

    plt.show()

    print('Fitness plot generated.')