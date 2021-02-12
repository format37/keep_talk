import argparse
import json
import logging
import sys
import time
from functools import partial
from pathlib import Path

import tensorflow as tf
#import tensorflow.compat.v1 as tf
#tf.disable_v2_behavior()

from inputs import *
from model_fns import *
from predict_fns import *

from lex import send_to_telegram
from language_translate import detect_language, translate_text
from sql_lib import sql_read, sql_remove
import pymysql.cursors

# This program was designed to function with multiple kinds of models, but currently only GPT2 is supported
# The first element in the tupel is the model function, the second is the function called when predicting
models = {
    "GPT2": (gpt2_model, gpt2_predict)
}

inputs = {
    "openwebtext": openwebtext, # Standard OpenWebtext input
    "openwebtext_longbiased": openwebtext_longbiased, # OpenWebtext with a bias towards showing more long (>512 tokens) examples
    "openwebtext_long": openwebtext_long, # Openwebtext that only shows long examples
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--tpu', type=str) # Name of TPU to train on, if any
    parser.add_argument('--model', type=str) # JSON file that contains model parameters
    parser.add_argument("--predict_file", type=str) # File to take as input for predict
    parser.add_argument("--predict_text", type=str) # Take string directly from args
    parser.add_argument("--top_k", type=int) # Top K truncation parameter for text generation
    args = parser.parse_args()

    # Get prediction text
    predict_mode = False
    if args.predict_file is not None:
        predict_mode = True
        with open(args.predict_file) as f:
            text = f.read()
    elif args.predict_text is not None:
        predict_mode = True
        text = args.predict_text
    elif args.predict_file is not None and args.predict_text is not None:
        print("ERROR: Specify exactly one of --predict_file and --predict_text!")
        sys.exit()

    # Setup logging
    Path("logs").mkdir(exist_ok=True)
    tf.compat.v1.logging.set_verbosity(logging.INFO)
    handlers = [
        logging.FileHandler('logs/{}.log'.format(args.model)),
        logging.StreamHandler(sys.stdout)
    ]
    logger = logging.getLogger('tensorflow')
    logger.handlers = handlers

    # Read params of model
    with open(args.model, "r") as f:
        params = json.load(f)

    if not args.tpu is None:
        params["use_tpu"] = True
    else:
        params["use_tpu"] = False

    if args.top_k is not None:
        params["top_k"] = args.top_k

    if not "precision" in params.keys():
        params["precision"] = "float32" # Doesn't actually do anything since float32 is the default anyways. Only recognized other dtype is "bfloat16"

    if not "iterations" in params.keys():
        params["iterations"] = 1 # Because this controls how many samples are prefetched

    logger.info(params)

    model_fn = models[params["model"]][0]
    predict_fn = models[params["model"]][1]
    input_fn = inputs[params["input"]]

    if params["use_tpu"] and not predict_mode:
        # Resolve TPU cluster and runconfig
        tpu_cluster_resolver = tf.distribute.cluster_resolver.TPUClusterResolver(args.tpu)

        run_config = tf.compat.v1.estimator.tpu.RunConfig(
            model_dir=params["model_path"],
            cluster=tpu_cluster_resolver,
            save_checkpoints_secs=60*30,
            session_config=tf.compat.v1.ConfigProto(
                # allow_soft_placement=True,
                # log_device_placement=True
                ),
                tpu_config=tf.compat.v1.estimator.tpu.TPUConfig(iterations_per_loop=params["iterations"])
        )

        # Set up network
        network = tf.compat.v1.estimator.tpu.TPUEstimator(
                model_fn=model_fn,
                use_tpu=True,
                train_batch_size=params["train_batch_size"], # These are the global sizes, must be divisible by replicas
                eval_batch_size=params["eval_batch_size"],
                predict_batch_size=params["predict_batch_size"],
                config=run_config,
                params=params)

    else:
        # Non TPU setup
        if not predict_mode:
            params["batch_size"] = params["train_batch_size"]
        else:
            params["batch_size"] = params["predict_batch_size"]

            from models.gpt2 import encoder
            enc = encoder.get_encoder(params["encoder_path"])
            tokens = enc.encode(text)
            params["text_len"] = len(tokens)
            if params["text_len"] > 1024:
                params["text_len"] = 1024

        run_config = tf.estimator.RunConfig(
            model_dir=params["model_path"],
            session_config=tf.compat.v1.ConfigProto(
                # log_device_placement=True,
                # allow_soft_placement=True
            ),
        )

        network = tf.estimator.Estimator(
            model_fn=model_fn,
            config=run_config,
            params=params)

    if predict_mode:
        #lex++
        con = pymysql.connect('localhost', 'root', '9878987', 'mysql')
        print('waiting..')
        #group='106129214'
        while True:
            lex_source=''
            #with open("source.txt",'r') as lex_file:
            #    lex_source=lex_file.read()
            #con = pymysql.connect('localhost', 'root', '9878987', 'mysql')
            row=sql_read(con)
            if len(row):
            #if lex_source!='':
                request_id,chat,message_id,lex_source=row[0][0],row[0][2],row[0][3],row[0][4]
                sql_remove(con,request_id)
                #clear result:
                open('logs/predictions_SortaBig.txt', 'w').close()
                #translate
                source_language=detect_language(lex_source)
                if source_language!='en':
                    lex_source=translate_text('en', lex_source)
                    print('source language:',source_language)
                #prediction start
                text=lex_source
                #text=lex_source+" it's all a piece of shit"
                #text=lex_source+" with which I strongly disagree"
                #with open("source.txt",'w') as lex_file:
                #    lex_file.write('')				
                print('received: '+text)
                tokens = enc.encode(text)
                params["text_len"] = len(tokens)
                if params["text_len"] > 1024:
                    params["text_len"] = 1024
                logger.info("Generating predictions...")
                predict_fn(network, text, params)

                with open("logs/predictions_SortaBig.txt",'r') as lex_file:
                    lex_result=lex_file.read()                
				 
                lex_result=lex_result.replace('======================================== SAMPLE 0 ========================================', '')
                lex_result=lex_result.replace('================================================================================', '')
                lex_result=lex_result.replace(lex_source, '')
                lex_result=lex_result.replace('@gpt2robot', '')
                lex_result='.'.join(lex_result.split('.')[:3])+'.' #crop left 4 sentences
                #translate
                if source_language!='en':
                    lex_result=translate_text(source_language, lex_result)
                #send to telegram
                #with open("chat.txt",'r') as lex_file:
                #    chat=lex_file.read()
                send_to_telegram(chat,lex_result,message_id)
                print('waiting..')
            #else:
            #    lex_file.close()
        #lex--
        #logger.info("Generating predictions...")
        #predict_fn(network, text, params)
        sys.exit()

    # Train eval loop
    while True:
        start = time.time()

        network.train(
                input_fn=partial(input_fn, eval=False),
                steps=params["train_steps"])


        end = time.time()
        logger.info("\nTrain loop took {:.2f}s\n".format(end-start))

        eval_result = network.evaluate(
           input_fn=partial(input_fn, eval=True),
           steps=params["eval_steps"])

        logger.info("\nEval Results: {}\n".format(str(eval_result)))

        if network.get_variable_value("global_step") > params["max_steps"]:
            logger.info("Done!")
            break