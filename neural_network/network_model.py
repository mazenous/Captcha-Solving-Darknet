from keras.models import Sequential
from keras.src.layers import MaxPooling2D, Conv2D, Flatten, Dense, Activation, Dropout


class NetworkModel:
    @staticmethod
    def build(width, height, depth, out_size):
        # Here I should create my model to have a better structure
        model = Sequential()
        input_shape = (height, width, depth)

        model.add(Conv2D(32, (3, 3), padding='valid', input_shape=input_shape))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(2))
        model.add(Dropout(0.25))

        model.add(Conv2D(64, (3, 3)))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(2))
        model.add(Dropout(0.25))

        model.add(Conv2D(128, (3, 3)))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(2))
        model.add(Dropout(0.25))

        # Fully connected layer
        model.add(Flatten())
        model.add(Dense(1024))
        model.add(Dense(512))
        model.add(Activation('relu'))
        model.add(Dropout(0.25))
        model.add(Dense(out_size))
        model.add(Activation('softmax'))

        return model
