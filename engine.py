import numpy as np
import matplotlib.pyplot as plt
import h5py
import skimage.io as skimageIO
import skimage.transform as skimageTransform
import tkinter.filedialog as tk
import pickle
import os
import sys

d = None

def load_dataset():
    train_dataset = h5py.File('cat-vs-noncat-classification-logistic/datasets/train_catvnoncat.h5', "r")
    train_set_x_orig = np.array(train_dataset["train_set_x"][:]) 
    train_set_y_orig = np.array(train_dataset["train_set_y"][:])

    test_dataset = h5py.File('cat-vs-noncat-classification-logistic/datasets/test_catvnoncat.h5', "r")
    test_set_x_orig = np.array(test_dataset["test_set_x"][:])
    test_set_y_orig = np.array(test_dataset["test_set_y"][:])

    classes = np.array(test_dataset["list_classes"][:])
    
    train_set_y_orig = train_set_y_orig.reshape((1, train_set_y_orig.shape[0]))
    test_set_y_orig = test_set_y_orig.reshape((1, test_set_y_orig.shape[0]))
    
    return train_set_x_orig, train_set_y_orig, test_set_x_orig, test_set_y_orig, classes

train_set_x_orig, train_set_y, test_set_x_orig, test_set_y, classes = load_dataset()

m_train = train_set_x_orig.shape[0]
m_test = test_set_x_orig.shape[0]
num_px = train_set_x_orig.shape[1]

train_set_x_flatten = train_set_x_orig.reshape(train_set_x_orig.shape[0], -1).T
test_set_x_flatten = test_set_x_orig.reshape(test_set_x_orig.shape[0], -1).T

train_set_x = train_set_x_flatten/255.
test_set_x = test_set_x_flatten/255.

def sigmoid(z):
    
    s = 1/(1 + np.exp(- z))
        
    return s

def initialize_with_zeros(dim):
   
    w = np.zeros((dim, 1))
    b = 0
    

    assert(w.shape == (dim, 1))
    assert(isinstance(b, float) or isinstance(b, int))
    
    return w, b

def propagate(w, b, X, Y):
    
    m = X.shape[1]
    A = sigmoid( np.dot(w.T, X) + b)                         
    cost = (- 1/ m) * np.sum(Y * np.log(A) + (1 - Y) * np.log(1 - A))                                  # compute cost
    dw = (1/ m) * np.dot(X, (A - Y).T)
    db = (1/ m) * np.sum(A - Y)
    
    assert(dw.shape == w.shape)
    assert(db.dtype == float)
    cost = np.squeeze(cost)
    assert(cost.shape == ())
    
    grads = {"dw": dw,
             "db": db}
    
    return grads, cost

def optimize(w, b, X, Y, num_iterations, learning_rate, print_cost = False):
    
    costs = []
    
    for i in range(num_iterations):
        grads, cost = propagate(w, b, X, Y)
        
        dw = grads["dw"]
        db = grads["db"]
        
        w = w - learning_rate * dw
        b = b - learning_rate * db
        if i % 100 == 0:
            costs.append(cost)
        if print_cost and i % 100 == 0:
            print ("Cost after iteration %i: %f" %(i, cost))
    
    params = {"w": w,
              "b": b}
    
    grads = {"dw": dw,
             "db": db}
    
    return params, grads, costs

def predict(w, b, X):
    
    
    m = X.shape[1]
    Y_prediction = np.zeros((1,m))
    w = w.reshape(X.shape[0], 1)
    A = sigmoid(np.dot((w.T), X) + b)
    
    for i in range(A.shape[1]):
        if(A[0, i] <= 0.5):
            Y_prediction[0, i] = 0
        else:
            Y_prediction[0, i] = 1
    
    assert(Y_prediction.shape == (1, m))
    
    return Y_prediction

def model(X_train, Y_train, X_test, Y_test, num_iterations = 2000, learning_rate = 0.5, print_cost = False):
    w, b = initialize_with_zeros(X_train.shape[0])
    parameters, grads, costs = optimize(w, b, X_train, Y_train, num_iterations= 2000, learning_rate = 0.5, print_cost = False)
    
    w = parameters["w"]
    b = parameters["b"]
    Y_prediction_test = predict(w, b, X_test)
    Y_prediction_train = predict(w, b, X_train)
    print("train accuracy: {} %".format(100 - np.mean(np.abs(Y_prediction_train - Y_train)) * 100))
    print("test accuracy: {} %".format(100 - np.mean(np.abs(Y_prediction_test - Y_test)) * 100))

    
    d = {"costs": costs,
         "Y_prediction_test": Y_prediction_test, 
         "Y_prediction_train" : Y_prediction_train, 
         "w" : w, 
         "b" : b,
         "learning_rate" : learning_rate,
         "num_iterations": num_iterations}
    
    return d



def brainer():
    #load brain
    global d
    if os.path.exists("/brain.d") == True:
        with open("/brain.d", "rb") as f:
            d = pickle.load(f)
    else:
        d = model(train_set_x, train_set_y, test_set_x, test_set_y, num_iterations = 2000, learning_rate = 0.005, print_cost = True)
        with open("/brain.d", "wb") as f:
            pickle.dump(d, f)
        sys.exit()
        


def judge(images):
    image = np.array(skimageIO.imread(images))
    my_image = skimageTransform.resize(image, (num_px,num_px)).reshape((1, num_px*num_px*3)).T

    my_predicted_image = predict(d["w"], d["b"], my_image)

    plt.imshow(image)

    ans = classes[int(np.squeeze(my_predicted_image)),].decode("utf-8")

    print("y = " + str(np.squeeze(my_predicted_image)) + ", your algorithm predicts a \"" + ans +  "\" picture.")

    if ans == "cat":
        return 1
    elif ans == "non-cat":
        return 0
    else:
        return -1

