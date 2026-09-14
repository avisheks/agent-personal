---
title: "Supervised Fine-Tuning (SFT) - NVIDIA NeMo Framework User Guide"
source: "https://docs.nvidia.com/nemo-framework/user-guide/24.07/llms/nemotron/sft.html"
ingestedAt: "2026-05-18T00:28:23Z"
---
> # Supervised Fine-Tuning (SFT)

Please prepare the datasets according to _Data Preparation for SFT and PEFT_ section before proceeding.

## Run SFT inside NeMo Container

### Start NeMo Container

If the container is not already running, use the following command
    
    
    docker run %%gpus device=1 --shm-size=2g --net=host --ulimit memlock=-1 --rm -it -v ${PWD}:/workspace -w /workspace -v ${PWD}/results:/results nvcr.io/nvidia/nemo:24.07 bash
    

### Run SFT

  1. Set the environment variables, and pass the paths to your train, test, and validation data files
         
         MODEL="YOUR PATH TO nemotron.nemo"
         TRAIN="[YOUR PATH TO databricks-dolly-15k/train.jsonl]"
         VALID="[YOUR PATH TO databricks-dolly-15k/validation.jsonl]"
         TEST="[YOUR PATH TO databricks-dolly-15k/test.jsonl]"
         VALID_NAMES="[databricks-dolly-15k]"
         

  2. Set the concat sampling probability. This value depends on the number of files passed in the train set and the percentage of the fine-tuning data to use from each file.

The sum of the concat sampling probabilities should be 1.0.

The following example shows how to set the concat sampling probability for a train set with two jsonl files. In this example, one train file is used: `CONCAT_SAMPLING_PROBS="[1.0]"`
         
         TRAIN="[/path/to/dataset_1.jsonl,/path/to/dataset_2.jsonl]"
         CONCAT_SAMPLING_PROBS="[0.3,0.7]"
         

  3. Set the tensor parallelism and pipeline parallelism values based on the model you are using. For Nemotron 340B use the following:
         
         CONCAT_SAMPLING_PROBS="[1]"
         TP_SIZE=8
         PP_SIZE=12
         

  4. Run the SFT command and set the values for the parameters, including the number of steps, model checkpoint path, batch sizes, etc.

For a full reference of parameter settings refer to the [config file](https://github.com/NVIDIA-NeMo/Automodel/blob/main/examples/llm_finetune/llama3_2/llama3_2_1b_squad.yaml) :
         
         torchrun --nproc_per_node=8 \
         /opt/NeMo/examples/nlp/language_modeling/tuning/megatron_gpt_finetuning.py \
            trainer.precision=bf16 \
            trainer.devices=8 \
            trainer.num_nodes=1 \
            trainer.val_check_interval=0.1 \
            trainer.max_steps=50 \
            model.restore_from_path=${MODEL} \
            model.peft.peft_scheme=none \
            model.micro_batch_size=1 \
            model.global_batch_size=128 \
            model.tensor_model_parallel_size=${TP_SIZE} \
            model.pipeline_model_parallel_size=${PP_SIZE} \
            model.megatron_amp_O2=True \
            model.sequence_parallel=True \
            model.activations_checkpoint_granularity=selective \
            model.activations_checkpoint_method=uniform \
            model.optim.name=distributed_fused_adam \
            model.optim.lr=1e-6 \
            model.answer_only_loss=True \
            model.data.train_ds.file_names=${TRAIN_DS} \
            model.data.validation_ds.file_names=${VALID_DS} \
            model.data.test_ds.file_names=${TEST_DS} \
            model.data.train_ds.concat_sampling_probabilities=${CONCAT_SAMPLING_PROBS} \
            model.data.train_ds.max_seq_length=4096 \
            model.data.train_ds.add_bos=True \
            model.data.validation_ds.max_seq_length=4096 \
            model.data.train_ds.micro_batch_size=1 \
            model.data.train_ds.global_batch_size=128 \
            model.data.validation_ds.micro_batch_size=1 \
            model.data.validation_ds.global_batch_size=128 \
            model.data.test_ds.micro_batch_size=1 \
            model.data.test_ds.global_batch_size=256 \
            model.data.train_ds.num_workers=0 \
            model.data.validation_ds.num_workers=0 \
            model.data.test_ds.num_workers=0 \
            model.data.validation_ds.metric.name=loss \
            model.data.test_ds.metric.name=loss \
            exp_manager.create_wandb_logger=False \
            exp_manager.explicit_log_dir=/results \
            exp_manager.resume_if_exists=True \
            exp_manager.resume_ignore_no_checkpoint=True \
            exp_manager.create_checkpoint_callback=True \
            exp_manager.checkpoint_callback_params.monitor=validation_loss \
            exp_manager.checkpoint_callback_params.save_best_model=False \
            exp_manager.checkpoint_callback_params.save_nemo_on_train_end=True \
            ++cluster_type=BCP \
            model.sequence_parallel=True \
            ++model.bias_activation_fusion=True \
         ++model.apply_rope_fusion=True
         




Note

For running SFT on multiple nodes (for example on a Slurm cluster, replace the `torchrun --nproc_per_node=8` with `python`.

**Tuning with packed dataset:**

To enable training with packed sequences, you need to adjust the configs. In addition, you need to reduce both the micro batch size and global batch size due to packing.

In this example, `global_batch_size=1` is set to sequence length 4096:
    
    
    model.data.train_ds.file_names=/path/to/dolly/packed_4096_seed0.npy \
    +model.data.train_ds.packed_sequence=True \
    model.micro_batch_size=1 \
    model.global_batch_size=8
    

**Tuning with FP8:**

To enable training with FP8, adjust the configs as follows:

### Run Evaluation

  1. Run evaluation using [megatron_gpt_generate.py](https://github.com/NVIDIA/NeMo/blob/main/examples/nlp/language_modeling/tuning/megatron_gpt_generate.py) **This link has been archived**

  2. Set the appropriate model checkpoint path, test file path, batch sizes, number of tokens etc. and run evaluation on the test file :
         
         PATH_TO_TRAINED_MODEL=/results/megatron_gpt_peft_none_tuning/checkpoints/megatron_gpt_peft_none_tuning.nemo
         TEST_DS="[YOUR PATH TO test.jsonl]"
         python /opt/NeMo/examples/nlp/language_modeling/tuning/megatron_gpt_generate.py \
               model.restore_from_path=${PATH_TO_TRAINED_MODEL} \
               trainer.devices=8 \
               model.data.test_ds.file_names=${TEST_DS} \
               model.data.test_ds.names=['dolly-15k_test'] \
               model.data.test_ds.global_batch_size=16 \
               model.data.test_ds.micro_batch_size=2 \
               model.data.test_ds.tokens_to_generate=20 \
               model.tensor_model_parallel_size=1 \
               model.pipeline_model_parallel_size=1 \
               inference.greedy=True \
               model.data.test_ds.output_file_path_prefix=/results/sft_results \
               model.data.test_ds.write_predictions_to_file=True
         




Sample Output
    
    
    $ tail -n 4 sft_results.jsonl
    
    {"sentence": "What is Azure HDInsight? Azure HDInsight is a cloud service that provides a high-performance, scalable, and cost-effective way to run Apache Hadoop on the"}
    {"sentence": "What is carnitine? Carnitine is a fatty acid that is found in the body. It is used to produce energy in the mitochondria of the cells. Carnit"}
    {"sentence": "List some TV shows that Canadian actor William B. Davis has been in."}
    {"sentence": "Identify which instrument is string or percussion: Handbell, Dobro, Drum"}
    

Note

This is only a sample output (based of a toy SFT example) and your output may vary. The performance can be further improved by fine-tuning the model for more steps.

## Run SFT with NeMo Launcher

Please refer to `Launcher Guide` section to understand the NeMo Launcher basics.

  1. To run SFT update `conf/config.yaml`:
         
         defaults:
         - peft: nemotron/sft
         
         stages:
         - peft
         

  2. Execute the launcher pipeline: `python3 main.py`.




### Configure SFT with NeMo Launcher

You an find the default configurations for SFT with squad in `conf/peft/nemotron/sft.yaml`.

Fine-tuning configuration is divided into four sections `run`, `trainer`, `exp_manger` and `model`.
    
    
    run:
      name: sft_nemotron
      time_limit: "04:00:00"
      dependency: "singleton"
      model_train_name: nemotron
      convert_dir: ${base_results_dir}/${peft.run.model_train_name}/${peft.run.convert_name}
      task_name: "squad"
      results_dir: ${base_results_dir}/${.model_train_name}/peft_${.task_name}
    

  1. Set the number of nodes and devices for fine-tuning:
         
         trainer:
         num_nodes: 12
         devices: 96
         

  2. Set the appropriate model parallel sizes. For nemotron 340B, use the following values.
         
         model:
         restore_from_path: /path/to/nemotron-340b.nemo
         tensor_model_parallel_size: 8
         pipeline_model_parallel_size: 16
         

`restore_from_path` sets the path to the `.nemo` checkpoint to run fine-tuning.

  3. Use a smaller learning rate for full parameter fine-tuning.
         
         optim:
         name: distributed_fused_adam
         lr: 1e-6