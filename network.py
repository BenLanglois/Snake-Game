import numpy as np
import math, json

# ------------------------------------------------------------------------------

class Network:
    def __init__(self, *args):
        # The Network will be loaded if args[0] else a new Network will be created
        if args[0] == True:
            # Load Network
            self.weights, self.biases, self.score = [np.array(x) for x in args[1]], [np.array(x) for x in args[2]], args[3]

        else:
            # New Network
            if len(args) not in (4, 5):
                raise SyntaxError("If not loading from file, must specify number of inputs, outputs, and hidden_layers (and hidden_nodes if hidden_layers > 0)")
            inputs, outputs, hidden_layers = args[1:4]
            hidden_nodes = args[4] if len(args) == 5 else 0
            # inputs: The number of input nodes
            # outputs: The number of output nodes
            # hidden_layers: The number of hidden layers
            # hidden_nodes: The number of nodes per hidden layer

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

    # TODO: Replace set_zero and set_rand methods with initialization in __init__

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

    # Activation function
    sigmoid = np.vectorize(lambda x: 1 / (1 + math.exp(-x)))

    def run(self, inputs):
        # Run the network
        values = np.array(inputs)
        for weights, biases in zip(self.weights, self.biases):
            values = Network.sigmoid(np.matmul(values, weights) + biases)
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

# ------------------------------------------------------------------------------

class Species:
    # A Species is just a list of Networks, but with some extra logic to make running/evolving them easier

    def __init__(self, *args):
        if args[0] == True:
            # Load from file
            self.num_networks, self.domination_rate, self.mutation_rate, input_file_name = args[1:5]
            self.output_file = args[5] if len(args) == 6 else None
            self.curr_network = 0

            with open(input_file_name, 'r') as input_file:
                input_string = input_file.read()

            split_input = input_string.split("!")

            self.generation = int(split_input[0])
            score = float(split_input[1])

            if split_input[2] != 'w':
                raise ValueError("Invalid input file")
            i = 3
            weights = []
            while i < len(split_input) and split_input[i] != 'b':
                # Read weights
                weights.append(json.loads(split_input[i]))
                i += 1

            if split_input[i] != 'b':
                raise ValueError("Invalid input file")
            i += 1
            biases = []
            while i < len(split_input) and split_input[i][0] != '#':
                biases.append(json.loads(split_input[i]))
                i += 1

            self.networks = [Network(True, weights, biases, score) for _ in range(self.num_networks)]

            for i in range(1, self.num_networks):
                # Fill all other networks with random data
                self.networks[i].set_rand()

        else:
            # Create new Species
            self.num_networks, self.domination_rate, self.mutation_rate, inputs, outputs, hidden_layers = args[1:7]
            hidden_nodes = args[7] if len(args) > 7 else 0
            initialization = args[8] if len(args) > 8 else "rand"
            seed = args[9] if len(args) > 9 else None
            self.output_file = args[10] if len(args) > 10 else None
            # num_networks: The number of networks in the species
            # domination_rate: The likelihood that the fittest parent will pass on their weights. Between 0 and 1
            # mutation_rate: The likelihood that a weight will mutate after being passed on to a child. Between 0 and 1
            # initialization: How to initialize the values of the neural network. One of "rand", "zero"
            # seed: The seed used for "rand" initialization
            # output_file: The file to output each generation's fittest network
            # All other parameters are the same as Network.__init__

            self.networks = [Network(False, inputs, outputs, hidden_layers, hidden_nodes) for _ in range(self.num_networks)]
            self.curr_network = 0
            self.generation = 1
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
            if self.generation%10 == 0:
                for i in range(1, self.num_networks):
                    # Fill all other networks with random data
                    self.networks[i].set_rand()

    def evolve(self):
        # Takes a list of networks and evolves them
        self.networks.sort(reverse=True, key = lambda x: x.score)
        fittest = self.networks[0]
        for i, network in enumerate(self.networks):
            if i == 0: continue # Don't modify fittest network
            self.networks[i] = fittest.breed(network, self.domination_rate, self.mutation_rate)
        self.generation += 1
        if self.output_file:
            # Output fittest neural network
            with open(self.output_file, 'w') as output_file:
                output_file.write(str(self.generation) + "!" + str(fittest.score) + "!w!" + "!".join(str(matrix.tolist()) for matrix in fittest.weights)+ "!b!" + "!".join(str(matrix.tolist()) for matrix in fittest.biases))