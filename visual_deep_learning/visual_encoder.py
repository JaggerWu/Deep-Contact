# using tensorflow stuff
from __future__ import division

import tensorflow as tf
import numpy as np


def conv_variable(weight_shape):
    '''
    parameters:
        weight_shape: a list with
            [width, hight, input_channels, output_channels]

    return:
        weight, bias
    '''
    w = weight_shape[0]
    h = weight_shape[1]
    input_channels = weight_shape[2]
    output_channels = weight_shape[3]
    d = 1.0 / np.sqrt(input_channels * w * h)
    bias_shape = [output_channels]
    weight = tf.Variable(
        tf.random_uniform(weight_shape, minval=-d, maxval=d))
    bias = tf.Variable(
        tf.random_uniform(bias_shape, minval=-d, maxval=d))

    return weight, bias


def conv2d(x, W, stride):
    return tf.nn.conv2d(
        x, W, strides=[1, stride, stride, 1], padding="SAME")


def maxpool2d(x, k=2):
    return tf.nn.max_pool(
        x, ksize=[1, k, k, 1], strides=[1, k, k, 1], padding='SAME')


def frame_2_pair(F1F2, F2F3, F3F4, F4F5, F5F6, x_cor, y_cor, FLAGS):
    fil_num = FLAGS.fil_num

    img_pair = tf.concat(
      [F1F2, F2F3, F3F4, F4F5, F5F6], 0)

    # First 2 layer conv(kernel size 3 and 4 channel)
    w_1_1, b_1_1 = conv_variable([10, 10, FLAGS.col_dim*2, 4])
    h_1_1 = tf.nn.relu(conv2d(img_pair, w_1_1, 1) + b_1_1)
    w_1_2, b_1_2 = conv_variable([10, 10, 4, 4])
    h_1_2 = tf.nn.relu(conv2d(h_1_1, w_1_2, 1) + b_1_2)

    # Second 2 layer conv (kernel size 3 and 16 channels)
    w_2_1, b_2_1 = conv_variable([3, 3, FLAGS.col_dim*2, 16])
    h_2_1 = tf.nn.relu(conv2d(img_pair, w_2_1, 1) + b_2_1)
    w_2_2, b_2_2 = conv_variable([3, 3, 16, 16])
    h_2_2 = tf.nn.relu(conv2d(h_2_1, w_2_2, 1) + b_2_2)
    en_pair = tf.concat([h_1_2, h_2_2], 3)

    # Third 2 layer conv (kernel size 3 and 16 channels)
    w_3_1, b_3_1 = conv_variable([3, 3, 20, 16])
    h_3_1 = tf.nn.relu(conv2d(en_pair, w_3_1, 1) + b_3_1)
    w_3_2, b_3_2 = conv_variable([3, 3, 16, 16])
    h_3_2 = tf.nn.relu(conv2d(h_3_1, w_3_2, 1) + b_3_2)
    h_3_2_x_y = tf.concat([h_3_2, x_cor, y_cor], 3)

    # Fourth conv and max-pooling layers to unit height and width
    w_4_1, b_4_1 = conv_variable([3, 3, 10, fil_num])
    h_4_1 = tf.nn.relu(conv2d(h_3_2_x_y, w_4_1, 1) + b_4_1)
    h_4_1 = maxpool2d(h_4_1)

    w_4_2, b_4_2 = conv_variable([3, 3, fil_num, fil_num])
    h_4_2 = tf.nn.relu(conv2d(h_4_1, w_4_2, 1) + b_4_2 + h_4_1)
    h_4_2 = maxpool2d(h_4_2)

    w_4_3, b_4_3 = conv_variable([3, 3, fil_num, fil_num])
    h_4_3 = tf.nn.relu(conv2d(h_4_2, w_4_3, 1) + b_4_3 + h_4_2)
    h_4_3 = maxpool2d(h_4_3)

    w_4_4, b_4_4 = conv_variable([3, 3, fil_num, fil_num])
    h_4_4 = tf.nn.relu(conv2d(h_4_3, w_4_4, 1) + b_4_4 + h_4_3)
    h_4_4 = maxpool2d(h_4_4)

    w_4_5, b_4_5 = conv_variable([3, 3, fil_num, fil_num])
    h_4_5 = tf.nn.relu(conv2d(h_4_4, w_4_5, 1) + b_4_5 + h_4_4)
    h_4_5 = maxpool2d(h_4_5)

    res_pair = tf.reshape(h_4_5, [-1, fil_num])
    pair1 = tf.slice(res_pair, [0, 0], [FLAGS.batch_num, -1])
    pair2 = tf.slice(res_pair, [FLAGS.batch_num, 0], [FLAGS.batch_num, -1])
    pair3 = tf.slice(res_pair, [FLAGS.batch_num*2, 0], [FLAGS.batch_num, -1])
    pair4 = tf.slice(res_pair, [FLAGS.batch_num*3, 0], [FLAGS.batch_num, -1])
    pair5 = tf.slice(res_pair, [FLAGS.batch_num*4, 0], [FLAGS.batch_num, -1])

    return pair1, pair2, pair3, pair4, pair5


def visual_encoder(F1, F2, F3, F4, F5, F6, x_cor, y_cor, FLAGS):
    '''
    parameters:
        Fn: Consecutive input frame
        x_cor: x-coordinate
        y_cor: y-coordinate
        (
            an x- and y-coordinate meshgrid over the image, which allows
            positions to be incorporated throughout much of processing.
            Without the coordinate channels, such a CNN would have to infer
            position from boundaries of the image, a more challenging task.
        )
        FLAGS: Learning settings

    return:
        state_code(1, 2, 3, 4)
    '''
    F1F2 = tf.concat([F1, F2], 3)
    F2F3 = tf.concat([F2, F3], 3)
    F3F4 = tf.concat([F3, F4], 3)
    F4F5 = tf.concat([F4, F5], 3)
    F5F6 = tf.concat([F5, F6], 3)

    pair1, pair2, pair3, pair4, pair5 = frame_2_pair(
        F1F2, F2F3, F3F4, F4F5, F5F6, x_cor, y_cor, FLAGS)

    concated_pair = tf.concat([pair1, pair2, pair3, pair4, pair5], 0)

    # shared a linear layer
    fil_num = FLAGS.fil_num
    w0 = tf.Variable(
        tf.truncated_normal(
            [fil_num, FLAGS.No*FLAGS.Ds], stddev=0.1), dtype=tf.float32)
    b0 = tf.Variable(
        tf.zeros([FLAGS.No*FLAGS.Ds]), dtype=tf.float32)
    h0 = tf.matmul(concated_pair, w0) + b0

    enpair1 = tf.reshape(
        tf.slice(h0, [0, 0], [FLAGS.batch_num, -1]),
        [-1, FLAGS.No, FLAGS.Ds],
    )
    enpair2 = tf.reshape(
        tf.slice(h0, [FLAGS.batch_num, 0], [FLAGS.batch_num, -1]),
        [-1, FLAGS.No, FLAGS.Ds],
    )
    enpair3 = tf.reshape(
        tf.slice(h0, [FLAGS.batch_num * 2, 0], [FLAGS.batch_num, -1]),
        [-1, FLAGS.No, FLAGS.Ds],
    )
    enpair4 = tf.reshape(
        tf.slice(h0, [FLAGS.batch_num * 3, 0], [FLAGS.batch_num, -1]),
        [-1, FLAGS.No, FLAGS.Ds],
    )
    enpair5 = tf.reshape(
        tf.slice(h0, [FLAGS.batch_num * 4, 0], [FLAGS.batch_num, -1]),
        [-1, FLAGS.No, FLAGS.Ds],
    )

    three1 = tf.concat([enpair1, enpair2], 2)
    three2 = tf.concat([enpair2, enpair3], 2)
    three3 = tf.concat([enpair3, enpair4], 2)
    three4 = tf.concat([enpair4, enpair5], 2)

    # shared MLP
    three = tf.concat([three1, three2, three3, three4], 0)
    three = tf.reshape(three, [-1, FLAGS.Ds * 2])

    w1 = tf.Variable(
        tf.truncated_normal([FLAGS.Ds * 2, 64], stddev=0.1), dtype=tf.float32)
    b1 = tf.Variable(
        tf.zeros([64]), dtype=tf.float32)
    h1 = tf.nn.relu(
        tf.matmul(three, w1) + b1)
    w2 = tf.Variable(
        tf.truncated_normal([64, 64], stddev=0.1), dtype=tf.float32)
    b2 = tf.Variable(
        tf.zeros([64]), dtype=tf.float32)
    h2 = tf.nn.relu(
        tf.matmul(h1, w2) + b2 + h1)
    w3 = tf.Variable(
        tf.truncated_normal([64, FLAGS.Ds], stddev=0.1), dtype=tf.float32)
    b3 = tf.Variable(
        tf.zeros([FLAGS.Ds]), dtype=tf.float32)
    h3 = tf.matmul(h2, w3) + b3 + h2
    h3 = tf.reshape(h3, [-1, FLAGS.No, FLAGS.Ds])

    S1 = tf.slice(h3, [0, 0, 0], [FLAGS.batch_num, -1, -1])
    S2 = tf.slice(h3, [FLAGS.batch_num, 0, 0], [FLAGS.batch_num, -1, -1])
    S3 = tf.slice(h3, [FLAGS.batch_num*2, 0, 0], [FLAGS.batch_num, -1, -1])
    S4 = tf.slice(h3, [FLAGS.batch_num*3, 0, 0], [FLAGS.batch_num, -1, -1])

    return S1, S2, S3, S4


def state_decoder(output, FLAGS):
    '''
    '''
    input_sd = tf.reshape(output, [-1, FLAGS.Ds])
    w1 = tf.Variable(tf.truncated_normal([FLAGS.Ds, 4], stddev=0.1),
                     dtype=tf.float32)
    b1 = tf.Variable(tf.zeros([4], dtype=tf.float32))
    h1 = tf.matmul(input_sd, w1) + b1
    h1 = tf.reshape(h1, [-1, FLAGS.No, 4])

    return h1
