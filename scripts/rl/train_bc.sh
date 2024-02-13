source /opt/conda/etc/profile.d/conda.sh
conda activate logicity
CONFIG=config/tasks/Nav/easy/RL/bc.yaml
python3 main.py --config $CONFIG \
    --exp train_bc \
    --log_dir log_rl \
    --use_gym