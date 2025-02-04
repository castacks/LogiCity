MODE=easy

# python3 main.py --config config/tasks/Nav/${MODE}/algo/random_test.yaml \
#     --exp random_${MODE}_test \
#     --log_dir log_rl \
#     --use_gym

# python3 main.py --config config/tasks/Nav/${MODE}/experts/expert_test.yaml \
#     --exp oracle_${MODE}_test2 \
#     --log_dir log_rl \
#     --use_gym --save_steps

# python3 main.py --config config/tasks/Nav/${MODE}/experts/expert_val.yaml \
#     --exp oracle_${MODE}_val \
#     --log_dir log_rl \
#     --use_gym --save_steps

# for n in 100
# do
# python3 main.py --config config/tasks/Nav/${MODE}/algo/bctest.yaml \
#     --exp bc_${n}_${MODE} \
#     --checkpoint_path checkpoints/final_models/${MODE}/bc${n}.zip \
#     --log_dir log_rl \
#     --use_gym
# done

# python3 main.py --config config/tasks/Nav/${MODE}/algo/nlmtest.yaml \
#     --exp nlmbc_${MODE}_test \
#     --checkpoint_path checkpoints/final_models/easy/nlm100.pth \
#     --log_dir log_rl \
#     --use_gym

# python3 main.py --config config/tasks/Nav/expert/algo/nlmtest.yaml \
#     --exp nlmbc_expert_test \
#     --checkpoint_path checkpoints/final_models/expert/nlm100.pth \
#     --log_dir log_rl \
#     --use_gym

# python3 main.py --config config/tasks/Nav/${MODE}/algo/dqn_test.yaml \
#     --exp dqn_${MODE} \
#     --checkpoint_path checkpoints/final_models/hard/dqn_140k.zip \
#     --log_dir log_rl \
#     --use_gym

# python3 main.py --config config/tasks/Nav/${MODE}/algo/a2c_test.yaml \
#     --exp a2c_${MODE} \
#     --checkpoint_path checkpoints/final_models/${MODE}/a2c_140k.zip \
#     --log_dir log_rl \
#     --use_gym

# python3 main.py --config config/tasks/Nav/${MODE}/algo/ppo_test.yaml \
#     --exp ppo_${MODE} \
#     --checkpoint_path checkpoints/final_models/hard/ppo_60k.zip \
#     --log_dir log_rl \
#     --use_gym

# python3 main.py --config config/tasks/Nav/${MODE}/algo/hri_test.yaml \
#     --exp hri_${MODE} \
#     --log_dir log_rl \
#     --use_gym

# for n in 50 100
# do
# python3 main.py --config config/tasks/Nav/${MODE}/algo/nlm_test.yaml \
#     --exp nlmbc_${n}_${MODE} \
#     --checkpoint_path checkpoints/final_models/hard/nlmbc_${n}.pth \
#     --log_dir log_rl \
#     --use_gym
# done

# for iter in {5000..60000..5000}
# do
# python3 main.py --use_gym --config config/tasks/Nav/transfer/medium/algo/dqn_test.yaml --exp transfer_easy2medium_dqn_test_${iter} \
#     --checkpoint_path checkpoints/transfer_dqn_medium_transfer_${iter}_steps.zip
# done

# for iter in 2800 3600
# do
# python3 main.py --config config/tasks/Nav/easy/algo/gnnbctest.yaml --exp gnn_easy_test_${iter} \
#     --checkpoint_path checkpoints/easy_gnnbc_100_${iter}_steps.zip --use_gym
# done

# for iter in 2400 3600 
# do
# python3 main.py --config config/tasks/Nav/medium/algo/gnnbctest.yaml --exp gnn_medium_test_${iter} \
#     --checkpoint_path checkpoints/medium_gnn100_${iter}_steps.zip --use_gym
# done

# for iter in 800 1600 
# do
# python3 main.py --config config/tasks/Nav/hard/algo/gnnbctest.yaml --exp gnn_hard_test_${iter} \
#     --checkpoint_path checkpoints/hard_gnn100_${iter}_steps.zip --use_gym
# done

# for iter in 3200 4000
# do
# python3 main.py --config config/tasks/Nav/expert/algo/gnnbctest.yaml --exp gnn_expert_test_${iter} \
#     --checkpoint_path checkpoints/expert_gnn100_${iter}_steps.zip --use_gym
# done

python3 main.py --config config/tasks/Nav/hard/algo/dqn_test.yaml --exp dqn_hard_test_3 \
    --checkpoint_path checkpoints/final_models/spf_emp/hard/dqn.zip --use_gym

python3 main.py --config config/tasks/Nav/hard/algo/nlmdqn_test.yaml --exp nlmdqn_hard_test_3 \
    --checkpoint_path checkpoints/final_models/spf_emp/hard/nlmdqn.zip --use_gym

python3 main.py --config config/tasks/Nav/hard/experts/expert_test.yaml --exp oracle_hard_test_3 \
    --use_gym

# python3 main.py --config config/tasks/Nav/expert/algo/nlmdqn_test.yaml --exp nlmdqn_expert_test \
#     --checkpoint_path checkpoints/final_models/spf_emp/expert/nlmdqn.zip --use_gym

# for run in 0 1 2
# do
#     for data in 10 20 30 40 50
#     do
#         for iter in 1 2 3 4 5
#         do
#         python3 main.py --config config/tasks/Nav/transfer/medium/algo/nlmval.yaml --exp transfer_easy2med_nlm_val_${iter}_${run}_${data} \
#             --checkpoint_path checkpoints/logicity_transfer_medium${run}_tl${data}/checkpoints/checkpoint_${iter}.pth --use_gym
#         done
#     done
# done

# python3 main.py --config config/tasks/Nav/medium/algo/dreamertest.yaml --exp dreamer_medium_test --use_gym

# python3 main_es.py --config config/tasks/Nav/hard/algo/dqn_estest.yaml --exp hard_dqnes_test

# python3 main_es.py --config config/tasks/Nav/hard/algo/mbrl_estest.yaml --exp hard_mbrles_test

# python3 main.py --config config/tasks/Nav/expert/algo/dreamer5_test.yaml --exp dreamer_expert_test --use_gym

# python3 main.py --config config/tasks/Nav/transfer/easy/algo/nlmdqn_test_train.yaml --exp transfer_easy_nlmdqn_test_train --use_gym
# for iter in 1200 1600 2400 3600 5000 8000 10000 13000 16000 18000 20000 22000 24000 26000 28000
# do
# python3 main.py --config config/tasks/Nav/transfer/medium/algo/dqn_test.yaml --exp transfer_easy2medium_dqn_test_${iter} \
#     --checkpoint_path checkpoints/transfer_dqn_medium_transfer_${iter}_steps.zip --use_gym
# # python3 main.py --config config/tasks/Nav/transfer/medium/algo/dqn_test_train.yaml --exp transfer_easy2medium_dqn_test_train_${iter} \
# #     --checkpoint_path checkpoints/transfer_dqn_medium_transfer_${iter}_steps.zip --use_gym
# done
# for iter in 100000
# do
# python3 main.py --config config/tasks/Nav/transfer/easy/algo/dqn_test.yaml --exp transfer_easy_dqn_test_${iter} \
#     --checkpoint_path checkpoints/transfer_dqn_easy_initial_${iter}_steps.zip --use_gym
# done
