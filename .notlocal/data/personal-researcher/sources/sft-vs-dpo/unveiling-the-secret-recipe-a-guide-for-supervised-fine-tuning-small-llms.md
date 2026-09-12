---
title: "Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs"
source: "https://arxiv.org/html/2412.13337v1"
ingestedAt: "2026-05-18T00:36:35Z"
---
####  A.5.1 Stacked Training vs. Sequential Phased Training

Contrary to our initial hypothesis that stacked training might underperform at smaller batch sizes due to insufficient gradient stability, our results show that stacked training achieves better or comparable performance to phased training consistently at both 128 and 4,000 batch sizes. The performance comparison across MTBench and MMLU benchmarks indicates that stacked training slightly outperforms phased training at each batch size, suggesting that batch size does not significantly impact the difference between the two training strategies. Instead, stacked training’s exposure to the entire dataset in each epoch, even at smaller batch sizes, may help maintain stability in learning, effectively supporting generalization across diverse types of data without requiring phased partitioning.

In Figure [3](https://arxiv.org/html/2412.13337v1#A1.F3 "Figure 3 ‣ A.5.1 Stacked Training vs. Sequential Phased Training ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs"), we compare the performance of both training strategies using the LAB hyperparameter configuration, which provided the best overall results for both approaches. Figure [3](https://arxiv.org/html/2412.13337v1#A1.F3 "Figure 3 ‣ A.5.1 Stacked Training vs. Sequential Phased Training ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs")a shows the final MTBench performance, where stacked training outperformed phased training by 0.01 points. Figure [3](https://arxiv.org/html/2412.13337v1#A1.F3 "Figure 3 ‣ A.5.1 Stacked Training vs. Sequential Phased Training ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs")b illustrates that stacked training is also more sample-efficient, with the best performance points annotated by the number of samples required to reach them. Note that the line for phased training begins partway through, as samples from Phases 00 and 05 were already included. This applies consistently to all similar figures presented in this paper.

(a) Final Performance on MTBench

(b) Sample Efficiency on MTBench

Figure 3: Comparison of stacked and phased training strategies on MTBench using LAB hyperparameters.

In addition to the MTBench results, we include the MMLU performance comparisons here. MMLU is split into two plots for clarity and readability. Figure [4](https://arxiv.org/html/2412.13337v1#A1.F4 "Figure 4 ‣ A.5.1 Stacked Training vs. Sequential Phased Training ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs") shows the final MMLU performance using LAB hyperparameters for both stacked and phased training strategies. Stacked training outperformed phased training on the MMLU benchmark by 0.01 points, consistent with the observations from MTBench.

Figure 4: Final MMLU Performance comparison using LAB hyperparameters: stacked vs. phased training.

Figure [5](https://arxiv.org/html/2412.13337v1#A1.F5 "Figure 5 ‣ A.5.1 Stacked Training vs. Sequential Phased Training ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs") illustrates the sample efficiency comparison for MMLU. Similar to the MTBench results, stacked training achieves higher MMLU performance more quickly than phased training. These results reinforce our findings that stacked training not only improves performance but also enhances sample efficiency on both MMLU and MTBench benchmarks.

Figure 5: MMLU Sample efficiency comparison between stacked and phased training.

To investigate whether phased training might be effective when phases are split based on difficulty, we conducted an additional experiment. In this setup, we partitioned the dataset into two phases based on difficulty, using the length of free-form answers as a proxy for difficulty.

  * •

Phase I: The bottom 50% of the data containing short sentences.

  * •

Phase II: The top 50% of the data containing long sentences, plus a 1% subset of the short sentences as a replay buffer when transitioning to long sentences.




Figure 6: Performance comparison of stacked vs. phased training on difficulty-partitioned data (by answer length) across comprehensive benchmarks.

We fine-tuned the Granite 7B base model using the same hyperparameters—a batch size of 4,000 and a learning rate of 2×10−52\times 10^{-5}—under both the phased and stacked training strategies. Our results (Figure [6](https://arxiv.org/html/2412.13337v1#A1.F6 "Figure 6 ‣ A.5.1 Stacked Training vs. Sequential Phased Training ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs")) showed no significant difference between phased and stacked training in this setting. Both performed similarly, with stacked training slightly outperforming phased training across all benchmarks. This suggests that even when the data is carefully partitioned based on difficulty, phased training does not improve model performance over stacked training. Moreover, phased training remains less sample-efficient due to the additional time and samples required to determine the optimal checkpoint for phase transitions.

####  A.5.5 Effect of Learning Rate

As shown in Figure [11](https://arxiv.org/html/2412.13337v1#A1.F11 "Figure 11 ‣ A.5.5 Effect of Learning Rate ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs"), the lowest learning rate of 2×10−52\times 10^{-5} yielded the best performance on the MTBench Benchmark.

Figure 11: MTBench performance after Phase 10 training with different learning rates.

We investigated whether larger batch sizes necessitate higher learning rates, based on the premise that with a larger batch size, the model processes more samples before each gradient step, potentially benefiting from a higher learning rate to make more significant updates and to maintain the variance of the gradient when compared to smaller batch sizes. Additionally, since larger batches result in fewer gradient steps over the same number of epochs, increasing the learning rate might improve training efficiency.

Our experiments compared models trained with different learning rates across batch sizes of 128, 3,840, and 7,680 samples. The runs included TULU hyperparameters at learning rates of 2×10−52\times 10^{-5} and 3×10−53\times 10^{-5}, and LAB hyperparameters with learning rates ranging from 2×10−52\times 10^{-5} to 1×10−41\times 10^{-4}. As shown in Figure [12](https://arxiv.org/html/2412.13337v1#A1.F12 "Figure 12 ‣ A.5.5 Effect of Learning Rate ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs"), regardless of batch size, the lower learning rate of 2×10−52\times 10^{-5} consistently resulted in better or comparable performance on both MMLU and MTBench benchmarks. For instance, with a batch size of 128, performances were similar for both the learning rates. For larger batch sizes of 3,840 and 7,680, the 2×10−52\times 10^{-5} learning rate performed on par or better than higher learning rates.

(a) MMLU Performance Across Learning Rates

(b) MTBench Performance Across Learning Rates

Figure 12: Performance comparison across different learning rates and batch sizes on MMLU and MTBench benchmarks.

A possible explanation for our findings is that large batches yield more stable gradient estimates by averaging over more samples, which allows effective progress at lower learning rates without risking instability. Higher learning rates with large batches, however, can cause the model to take larger steps that risk moving too far (Hoffer et al., [2017](https://arxiv.org/html/2412.13337v1#bib.bib21)) from the pre-trained parameters, potentially overshooting the minima.

####  A.5.7 Adaptation to a Domain-Specific Dataset

To evaluate the generalizability of our findings to domain-specific datasets, we conducted experiments using a Math, Reasoning, and Code (MRC) dataset. This dataset specializes in mathematical problem-solving, logical reasoning, and programming tasks, representing a focused domain compared to our original diverse dataset.

We evaluated the models on several benchmarks, including GSM8K (Cobbe et al., [2021](https://arxiv.org/html/2412.13337v1#bib.bib8)), ARC (Clark et al., [2018](https://arxiv.org/html/2412.13337v1#bib.bib7)), and the Open LLM Leaderboard v2 benchmarks including MATH and MuSR. We compare the LAB and TULU hyperparameter configurations on the MRC dataset. Using the LLaMA 3B model, we fine-tuned with both configurations: LAB used a batch size of 4,000 and a constant learning rate, while TULU used a batch size of 128 with warmup and linear decay. As shown in Table [10](https://arxiv.org/html/2412.13337v1#A1.T10 "Table 10 ‣ A.5.7 Adaptation to a Domain-Specific Dataset ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs"), the LAB configuration outperforms TULU across all evaluation metrics, reaffirming that larger batch sizes and simplified learning rate schedules are beneficial even when fine-tuning on domain-specific data.

Table 10: Comparison of LAB vs. TULU Hyperparameter Configurations on the MRC Dataset Using the LLaMA 3B Model. Cells highlighted in green indicate better scores, and blue indicates higher sample efficiency (fewer samples used).

Benchmark |  Score |  Samples  
---|---|---  
LLaMA Base | LAB | TULU | LAB | TULU  
Leaderboard (MATH Lvl 5) | 0.02 | 0.04 | 0.04 | 9,980,259 | 3,468,664  
Leaderboard (MuSR) | 0.05 | 0.08 | 0.04 | 16,966,128 | 2,973,753  
ARC | 0.78 | 0.75 | 0.68 | 2,745,290 | 247,372  
GSM8K | 0.27 | 0.69 | 0.66 | 12,225,143 | 5,450,009  
  
Additionally, we fine-tuned the LLaMA 3B model using both the stacked and sequential phased training strategies with LAB hyperparameters. For phased training, as described in Appendix [A.5.1](https://arxiv.org/html/2412.13337v1#A1.SS5.SSS1 "A.5.1 Stacked Training vs. Sequential Phased Training ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs"), the dataset was partitioned into two phases based on response length: Phase I with shorter responses (bottom 50%) and Phase II with longer responses (top 50%). As shown in Table [11](https://arxiv.org/html/2412.13337v1#A1.T11 "Table 11 ‣ A.5.7 Adaptation to a Domain-Specific Dataset ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs"), stacked training demonstrates slightly higher performance and greater sample efficiency compared to phased training across all benchmarks.

Table 11: Comparison of Stacked vs. Phased Training Strategies on the MRC Dataset Using the LLaMA 3B Model. Cells highlighted in green indicate better scores, and blue indicates higher sample efficiency (fewer samples used).

Benchmark |  Score |  Samples  
---|---|---  
LLaMA Base | Stacked | Phased | Stacked | Phased  
Leaderboard (MATH Lvl 5) | 0.02 | 0.04 | 0.03 | 9,980,259 | 18,455,850  
Leaderboard (MuSR) | 0.05 | 0.08 | 0.08 | 16,966,128 | 18,206,922  
ARC | 0.78 | 0.75 | 0.71 | 2,745,290 | 14,964,367  
GSM8K | 0.27 | 0.69 | 0.67 | 12,225,143 | 14,964,367  
  
These findings demonstrate that our recommendations regarding training strategies and hyperparameters generalize to domain-specific datasets, supporting their applicability in specialized fine-tuning scenarios.

####  A.5.8 Adaptations to Different Model Sizes and Architectures

To assess the scalability and generality of our findings, we extended our experiments to different model families, architectures, and sizes, specifically testing the Mistral 7B model, the Granite 3B model, and the LLaMA 3B model.

Adaptation to a New Architecture. We performed stacked training experiments with the Mistral 7B model, varying batch sizes (128 and 3,840) and learning rates (1×10−61\times 10^{-6}, 5×10−65\times 10^{-6}, and 2×10−52\times 10^{-5}). We report downstream benchmark scores in MTBench and LLM Leaderboard v2, which includes MMLU-Pro, an enhanced version of MMLU that integrates more challenging, reasoning-focused questions and expands the choice set to better differentiate model capabilities (Wang et al., [2024](https://arxiv.org/html/2412.13337v1#bib.bib70)). Our findings, illustrated in Figure [14](https://arxiv.org/html/2412.13337v1#A1.F14 "Figure 14 ‣ A.5.8 Adaptations to Different Model Sizes and Architectures ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs"), indicate that higher batch sizes lead to improved performance on MTBench and equivalent performance on Leaderboard benchmarks. Specifically, a batch size of 4k combined with a learning rate of 1×10−61\times 10^{-6} yields the best results, as higher batch sizes and lower learning rates have a stabilizing effect on training, offering similar advantages by reducing noise/size of updates. Conversely, increasing the learning rate or reducing the batch size (e.g., using learning rates above 1×10−61\times 10^{-6} with a 4k batch size, as shown in Figure [15](https://arxiv.org/html/2412.13337v1#A1.F15 "Figure 15 ‣ A.5.8 Adaptations to Different Model Sizes and Architectures ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs"), or a batch size of 128 with a learning rate of 1×10−61\times 10^{-6}) negatively impacts downstream performance.

Figure 14: Benchmark performance comparison of different batch sizes for the Mistral 7B model.

While previous studies suggest higher learning rates are beneficial with larger batch sizes during training from scratch (Smith, [2017](https://arxiv.org/html/2412.13337v1#bib.bib59); Goyal et al., [2017](https://arxiv.org/html/2412.13337v1#bib.bib14)), our findings indicate that, for fine-tuning pre-trained models, lower learning rates are preferable to minimize forgetting and maintain downstream performance. We reason that this discrepancy arises because, starting from a pre-trained model at a local minimum in the loss landscape, we aim to avoid moving too far from that minimum during fine-tuning to prevent forgetting what was learned during pre-training. Larger batch sizes and lower learning rates reduce stochasticity in the optimization process, leading to smaller, more stable updates that help the model stay closer to the pre-trained parameters while effectively adapting to new data. This aligns with findings from (Hoffer et al., [2017](https://arxiv.org/html/2412.13337v1#bib.bib21)) that smaller batch sizes lead weights further from initialization due to higher estimation noise, while larger batch sizes keep weights closer to initialization by reducing the diffusion rate in the weight space. Therefore, using larger batch sizes and/or lower learning rates helps preserve the pre-trained knowledge while allowing the model to adapt to new tasks.

We conducted a learning rate sweep for the Mistral 7B model to determine which learning rate yields the best final performance. Our objective was to apply the methodology used for finding the optimal learning rate with the Granite models to the Mistral architecture. This methodology involves starting with a low learning rate. A low learning rate helps prevent large, destabilizing weight updates, allowing the model to fine-tune its parameters gradually and avoid overfitting. Additionally, lower learning rates facilitate more precise adjustments to the model weights, which is particularly important when adapting pre-trained models to new tasks or domains without forgetting previously learned information.

Our proposed methodology for identifying optimal hyperparameters involves starting with a baseline and iteratively testing slightly higher and lower values to detect performance improvements. For example, with learning rate, we began the search at 2×10−52\times 10^{-5} (effective for Granite) and adjusted incrementally to refine the optimal range based on empirical results. This approach serves as a general prescription for all hyperparameters, allowing systematic fine-tuning. Using this method, we identified 1×10−61\times 10^{-6} as the optimal learning rate for Mistral among the learning rates we tested.

The results are presented in Figure [15](https://arxiv.org/html/2412.13337v1#A1.F15 "Figure 15 ‣ A.5.8 Adaptations to Different Model Sizes and Architectures ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs"). We check if what we have observed before for Granite—that is, the general trend where lower gradient norms and higher loss are associated with better generalization and final performance—also applies to Mistral. Specifically, the lowest learning rate, 1×10−61\times 10^{-6}, produced the best overall performance on the MMLU benchmark. An interesting pattern emerged, similar to that observed with the Granite model: for the most effective learning rates, the gradient norm started at its lowest value and increased towards the end of training. Despite the higher gradient norm in the later stages, the associated loss remained higher throughout training (which is expected because lower learning rates typically result in higher loss values during training). This suggests that higher loss values may be an indicator of better model generalization. These observations confirm that the correlation between early training dynamics and final downstream performance is consistent across different model architectures.

Figure 15: Training dynamics for Mistral 7B with different learning rates, and their final performance on MMLU and MTBench benchmarks.

Adaptation to Different Model Sizes. We also examined whether our findings hold for smaller models by conducting experiments with the Granite 3B model. Specifically, we compared an 8k batch size with stacked training versus a 4k batch size with phased training. Our goal was to determine if the observations regarding batch size and training strategies for the Granite 7B model extend to the 3B model. In the 8k stacked setting for the Granite 3B model, we observed a lower gradient norm, higher loss, and improved MMLU performance compared to the 4k phased configuration. This trend is illustrated in Figure [16](https://arxiv.org/html/2412.13337v1#A1.F16 "Figure 16 ‣ A.5.8 Adaptations to Different Model Sizes and Architectures ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs").

Figure 16: Training dynamics for Granite 3B with different batch sizes and training strategies (8k stacked vs. 4k phased), and their final performance on MMLU and MTBench benchmarks.

The larger batch size likely improves performance by increasing data diversity within each batch, covering a range of tasks, skills, and knowledge. This diversity reduces gradient variance, promoting stable updates and helping the model retain pre-trained knowledge without significant forgetting. The lower gradient norm in the 8k stacked setting suggests that the model is settling into a flatter, more generalizable region of the loss landscape, while the higher loss indicates reduced risk of overfitting by maintaining a broader exploration. Together, these factors likely contribute to the superior performance of the 8k stacked configuration on the MMLU benchmark. These results suggest that the correlation between early training dynamics and final performance holds across different model sizes.

Generalization to a Different Model Family and Size. To assess whether our findings extend to a different model architecture and size at the same time, we conducted experiments using the LLaMA 3B model (Touvron et al., [2023](https://arxiv.org/html/2412.13337v1#bib.bib64)). We note that the Granite model shares the same architecture as the LLaMA model. Hence we believe that the findings in this paper can generalize across the LLaMA model family. We fine-tuned the model using both stacked and phased training strategies, as well as comparing the LAB and TULU hyperparameter configurations.

Table 12: Comparison of Stacked vs. Phased Training Strategies Using the LLaMA 3B Model. Cells highlighted in green indicate better scores, and blue indicates higher sample efficiency (fewer samples used).

Benchmark |  Score |  Samples  
---|---|---  
LLaMA Base | Stacked | Phased | Stacked | Phased  
Leaderboard (BBH) | 0.14 | 0.19 | 0.18 | 7,734,723 | 6,734,847  
Leaderboard (MATH Lvl 5) | 0.01 | 0.02 | 0.01 | 250,089 | 4,490,320  
Leaderboard (MuSR) | 0.05 | 0.22 | 0.11 | 10,979,309 | 4,988,983  
MMLU | 0.56 | 0.57 | 0.53 | 6,986,437 | 5,737,613  
ARC | 0.78 | 0.78 | 0.75 | 2,744,559 | 7,483,283  
GSM8K | 0.27 | 0.51 | 0.45 | 3,742,399 | 6,734,847  
MTBench | - | 5.00 | 4.30 | 9,232,227 | 6,734,847  
  
For phased training, as described in Appendix [A.5.1](https://arxiv.org/html/2412.13337v1#A1.SS5.SSS1 "A.5.1 Stacked Training vs. Sequential Phased Training ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs"), the dataset was partitioned into two phases based on response length: Phase I with shorter responses (bottom 50%) and Phase II with longer responses (top 50%). We compared the LAB configuration (batch size of 4,000 with constant learning rate) to the TULU configuration (batch size of 128 with warmup and linear decay). The models were evaluated on benchmarks including MMLU, MTBench, GSM8K, ARC, and the Open LLM Leaderboard v2 benchmarks including BBH, MATH, and MuSR.

Table 13: Comparison of LAB vs. TULU Hyperparameter Configurations on the LLaMA 3B Model. Cells highlighted in green indicate better scores, and blue indicates higher sample efficiency (fewer samples used).

Benchmark |  Score |  Samples  
---|---|---  
LLaMA Base | LAB | TULU | LAB | TULU  
Leaderboard (BBH) | 0.14 | 0.19 | 0.17 | 7,734,723 | 2,473,477  
Leaderboard (MATH Lvl 5) | 0.01 | 0.02 | 0.01 | 250,089 | 741,924  
Leaderboard (MuSR) | 0.05 | 0.22 | 0.15 | 10,979,309 | 1,731,217  
MMLU | 0.56 | 0.57 | 0.55 | 6,986,437 | 2,473,477  
ARC | 0.78 | 0.78 | 0.74 | 2,744,559 | 2,473,477  
GSM8K | 0.27 | 0.51 | 0.49 | 3,742,399 | 2,473,477  
MTBench | - | 5.00 | 4.97 | 9,232,227 | 2,473,477  
  
The results, depicted in Table [12](https://arxiv.org/html/2412.13337v1#A1.T12 "Table 12 ‣ A.5.8 Adaptations to Different Model Sizes and Architectures ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs"), indicate that the stacked training strategy achieves better performance than phased training across all benchmarks. Results in Table [13](https://arxiv.org/html/2412.13337v1#A1.T13 "Table 13 ‣ A.5.8 Adaptations to Different Model Sizes and Architectures ‣ A.5 Additional Results ‣ Appendix A Appendix ‣ Unveiling the Secret Recipe: A Guide For Supervised Fine-Tuning Small LLMs") indicate that the LAB hyperparameter configuration consistently outperforms TULU, reinforcing our earlier conclusion that larger batch sizes and a constant learning rate schedule are advantageous. These findings suggest that our recommended training strategies and hyperparameters are effective across different model architectures and sizes simultaneously, including the LLaMA family. Practitioners may consider applying these insights to fine-tune various small-sized LLMs, potentially achieving improvements in performance.