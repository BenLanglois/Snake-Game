import numpy as np

# Class definitions ------------------------------------------------------------

class Network:
    def __init__(self, inputs, outputs, hidden_layers, hidden_nodes=0):
        # Set up neural network without initializing values
        if inputs < 1 or outputs < 1 or hidden_layers < 0:
            raise ValueError()

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

    def set_rand(self, seed=None):
        if seed:
            np.random.seed(seed)
        for i, layer in enumerate(self.weights):
            self.weights[i] = 2 * np.random.random_sample(layer.shape) - 1
        for i, layer in enumerate(self.biases):
            self.biases[i] = 2 * np.random.random_sample(layer.shape) - 1

    def run(self, inputs):
        values = np.array(inputs)
        for weights, biases in zip(self.weights, self.biases):
            values = np.matmul(values, weights) + biases
        return values