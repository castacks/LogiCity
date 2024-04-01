MODE=hard

python3 main.py --config config/tasks/Nav/hard/algo/random_test.yaml \
    --exp random_${MODE} \
    --log_dir log_rl \
    --use_gym

python3 main.py --config config/tasks/Nav/hard/experts/expert_test.yaml \
    --exp oracle_${MODE} \
    --log_dir log_rl \
    --use_gym

for n in 50 100
do
python3 main.py --config config/tasks/Nav/${MODE}/algo/bc_test.yaml \
    --exp bc_${n}_${MODE} \
    --checkpoint_path checkpoints/final_models/hard/bc${n}.zip \
    --log_dir log_rl \
    --use_gym
done

for n in 50 100
do
python3 main.py --config config/tasks/Nav/${MODE}/algo/nlm_test.yaml \
    --exp nlmbc_${n}_${MODE} \
    --checkpoint_path checkpoints/final_models/hard/nlmbc_${n}.pth \
    --log_dir log_rl \
    --use_gym
done

python3 main.py --config config/tasks/Nav/${MODE}/algo/dqn_test.yaml \
    --exp dqn_${MODE} \
    --checkpoint_path checkpoints/final_models/hard/dqn_140k.zip \
    --log_dir log_rl \
    --use_gym

python3 main.py --config config/tasks/Nav/${MODE}/algo/a2c_test.yaml \
    --exp a2c_${MODE} \
    --checkpoint_path checkpoints/final_models/hard/a2c_140k.zip \
    --log_dir log_rl \
    --use_gym

python3 main.py --config config/tasks/Nav/${MODE}/algo/ppo_test.yaml \
    --exp ppo_${MODE} \
    --checkpoint_path checkpoints/final_models/hard/ppo_60k.zip \
    --log_dir log_rl \
    --use_gym

python3 main.py --config config/tasks/Nav/${MODE}/algo/hri_test.yaml \
    --exp hri_${MODE} \
    --log_dir log_rl \
    --use_gym