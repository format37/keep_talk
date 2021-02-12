import tensorflow as tf

def perplexity_metric(loss):
    loss = tf.reduce_mean(input_tensor=loss)
    perplexity = tf.exp(loss)
    return {"perplexity": tf.compat.v1.metrics.mean(perplexity)}
