from datetime import datetime

from sklearn.model_selection import train_test_split

from consts import *
from neural_network.data_helper import fig_model_accuracy_over_epochs, load_data, prepare_data
from neural_network.network_model import NetworkModel


def train_network(train_images, train_labels, test_images, test_labels, batch_size, epochs):
    model = NetworkModel.build(image_width, image_height, image_depth, len(allowed_chars))
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    history = model.fit(train_images, train_labels, epochs=epochs,
                        batch_size=batch_size,
                        validation_data=(test_images, test_labels))

    fig = fig_model_accuracy_over_epochs(history, epochs)
    fig.show()

    test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)
    print(test_acc)

    now = int(datetime.now().timestamp())
    #fig.savefig(f"{models_path}/{now}")
    model.save(f"{models_path}/{now}.keras")


# prepare and load data
prepare_data()

imgs, data, encoded_labels = load_data()

# split data
# the data aren't shuffled to keep the images clustered
# in its six image-group which gives much better results
train_images, test_images, train_labels, test_labels = train_test_split(data, encoded_labels, test_size=test_size,
                                                                        shuffle=False)

# normalize data
train_images, test_images = train_images / 255.0, test_images / 255.0

train_network(train_images, train_labels, test_images, test_labels, batch_size, epochs)
