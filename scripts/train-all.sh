for p in 'contra-article_1' 'contra-self_1' 'convince_1' 'new_1'
do
  for s in '@0.75excluding' '' '_chatgpt'
  do
    for m in 'base' 'xxlarge'
    do 
      if [[ $m == 'base' ]]; then
      LR=3e-5
      else
      LR=3e-6
      fi
      LABEL_COLUMN=$p$s
      MODEL_NAME=$m
      OUTDIR=$MODEL_NAME-$LABEL_COLUMN
      echo $LABEL_COLUMN
      echo $OUTDIR
      echo $LR
      echo ----
      WANDB_PROJECT='smaite' WANDB_NAME=$OUTDIR 
    done 
  done
done

# python classify.py \
#   --model_name_or_path bert-base-cased \
#   --train_file data-main-no-answers.json \
#   --validation_file data-main-no-answers.json \
#   --do_train \
#   --label_column rate_1@0.75 \
#   --input_column claim verdict text \
#   --max_seq_length 128 \
#   --per_device_train_batch_size 1 \
#   --learning_rate 2e-5 \
#   --num_train_epochs 3 \
#   --output_dir /tmp/test/ \
#   --no_cuda \
#   --max_train_samples 3 \