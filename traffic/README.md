I've used various types of setting for convolutional and hidden layers and number of neurons in each layer. I got quite interesting results. 

- **At first I've used this setting,**
`1CNN laye(32 neurons) + 1hidden layer(128 neurons)`
- **the result for this setting was,**
`loss: 0.5018 - accuracy: 0.8759`

The result seemed pretty good, so I thought adding a convolution layer would increase accuracy.

- **Next I've used this setting,**
`1CNN laye(32 neurons) + 1CNN laye(64 neurons) + 1hidden layer(128 neurons) `
- **the result for this setting was,**
`loss: 0.0968 - accuracy: 0.9764`

The result for this setting seemed extremely good. But I thought maybe I should explore more, if I can do better. So I added another convolution layer.

- **Next I've used this setting,**
`1CNN laye(32 neurons) + 1CNN laye(64 neurons) + 1CNN laye(128 neurons) + 1hidden layer(128 neurons)`
- **the result for this setting was,**
`loss: 0.0969 - accuracy: 0.9724`

So It seemed to me the accuracy didn't improve from previous setting though I've used more convolution layer in this setting.

## Lastly, I've came to a realization that adding more and more layers and neurons won't necessarily keep increasing accuracies. So, I've concluded my exploration of perfect setting with the 2nd one where I've used 2 convolution layer (one with 32 and another with 64 filters and 3x3 kernels) and 2 max-pooling layers (2x2). I've also added a hidden layer consists of 128 neurons. I've also added 20% dropout in each layer to make sure that I don't overfit.