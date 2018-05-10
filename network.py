import numpy as np
import math

# ------------------------------------------------------------------------------

class Network:
    def __init__(self, activation, inputs, outputs, hidden_layers, hidden_nodes=0):
        # activation: The activation function to be used
        # inputs: The number of input nodes
        # outputs: The number of output nodes
        # hidden_layers: The number of hidden layers
        # hidden_nodes: The number of nodes per hidden layer
        self.activation = activation
        self.score = 0

        if inputs < 1 or outputs < 1 or hidden_layers < 0:
            raise ValueError

        if hidden_layers == 0:
            # Connect inputs to outputs
            self.weights = [np.empty((inputs, outputs))]
            self.biases = [np.empty((1, outputs))]

        else:
            if hidden_nodes < 1:
                raise ValueError("hidden_nodes must be a positive integer if hidden_layers > 0")
            self.weights = [np.empty((inputs, hidden_nodes))]
            self.biases = [np.empty((1, hidden_nodes))]
            for _ in range(hidden_layers-1):
                self.weights.append(np.empty((hidden_nodes, hidden_nodes)))
                self.biases.append(np.empty((1, hidden_nodes)))
            self.weights.append(np.empty((hidden_nodes, outputs)))
            self.biases.append(np.empty((1, outputs)))

    def set_zero(self):
        # Fill all values in network with zeros
        for layer in self.weights:
            layer.fill(0)
        for layer in self.biases:
            layer.fill(0)

    def set_rand(self):
        # Set all values to random numbers
        for i, layer in enumerate(self.weights):
            self.weights[i] = 2 * np.random.random_sample(layer.shape) - 1
        for i, layer in enumerate(self.biases):
            self.biases[i] = 2 * np.random.random_sample(layer.shape) - 1

    # Activation Functions
    sigmoid = np.vectorize(lambda x: 1 / (1 + math.exp(-x)))

    def run(self, inputs):
        # Run the network with the given activation function
        values = np.array(inputs)
        for weights, biases in zip(self.weights, self.biases):
            values = self.activation(np.matmul(values, weights) + biases)
        return values.tolist()[0]

    def breed(self, other, domination_rate, mutation_rate):
        # Change other to become a combination of self and other
        for n, matrix in enumerate(self.weights):
            for i in range(matrix.shape[0]):
                for j in range(matrix.shape[1]):
                    if np.random.random() < mutation_rate:
                        # Assign random weight
                        other.weights[n][i,j] = 2 * np.random.random() - 1
                    elif np.random.random() < domination_rate:
                        # Take weights from self
                        other.weights[n][i,j] = self.weights[n][i,j]
        for n, matrix in enumerate(self.biases):
            for i in range(matrix.shape[1]):
                if np.random.random() < mutation_rate:
                    # Assign random weight
                    other.biases[n][0,i] = 2 * np.random.random() - 1
                elif np.random.random() < domination_rate:
                    # Take weights from self
                    other.biases[n][0,i] = self.biases[n][0,i]
        return other

    def output(self):
        return str(self.weights) + str(self.biases)

# ------------------------------------------------------------------------------

class Species:
    # A Species is just a list of Networks, but with some extra logic to make running/evolving them easier

    def __init__(self, num_networks, domination_rate, mutation_rate, activation, inputs, outputs,
    hidden_layers, hidden_nodes=0, initialization="rand", seed=None, output_file=None):
        # num_networks: The number of networks in the species
        # domination_rate: The likelihood that the fittest parent will pass on their weights. Between 0 and 1
        # mutation_rate: The likelihood that a weight will mutate after being passed on to a child. Between 0 and 1
        # initialization: How to initialize the values of the neural network. One of "rand", "zero"
        # seed: The seed used for "rand" initialization
        # output_file: The file to output each generation's fittest network
        # All other parameters are the same as Network.__init__

        self.networks = [Network(activation, inputs, outputs, hidden_layers, hidden_nodes) for _ in range(num_networks)]
        self.num_networks = num_networks
        self.curr_network = 0
        self.generation = 1
        self.domination_rate = domination_rate
        self.mutation_rate = mutation_rate
        self.output_file = output_file
        if initialization == "rand":
            if seed:
                np.random.seed(seed)
            for network in self.networks:
                network.set_rand()
        elif initialization == "zero":
            for network in self.networks:
                network.set_zero()
        else:
            raise ValueError

    def run(self, inputs):
        # Runs the current network
        return self.networks[self.curr_network].run(inputs)

    def next(self, score):
        # Progresses to the next network. Evolves if neccesary
        self.networks[self.curr_network].score = score
        self.curr_network += 1
        if self.curr_network == self.num_networks:
            self.curr_network = 0
            self.evolve()

    def evolve(self):
        # Takes a list of networks and evolves them
        self.networks.sort(reverse=True, key = lambda x: x.score)
        fittest = self.networks[0]
        for i, network in enumerate(self.networks):
            if i == 0:
                continue # Don't modify fittest network
            self.networks[i] = fittest.breed(network, self.domination_rate, self.mutation_rate)
        self.generation += 1
        if self.output_file:
            with open(self.output_file, 'w') as output_file:
                output_file.write(str(self.generation) + " " + fittest.output() + "\n")