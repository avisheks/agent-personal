---
title: "RecSim NG Framework"
summary: "Google's probabilistic, differentiable, multi-agent simulator for recommender ecosystems that functions as a world model framework, used for YouTube Music preference elicitation."
sources:
  - world-models/world-models-in-recommendation-systems.md
createdAt: 2026-06-15T11:42:30.118697+00:00
updatedAt: 2026-06-15T11:42:30.118697+00:00
---
# RecSim NG Framework

RecSim NG (Recommender System Simulation Next Generation) is a probabilistic, differentiable, multi-agent simulator framework developed by Google for modeling recommender system ecosystems. It serves as a world model framework for recommendation systems, enabling researchers to simulate complex user-item-platform interactions and evaluate recommendation policies offline. ^[world-models-in-recommendation-systems.md]

## Overview

RecSim NG functions as a [[World Models — Overview and SOTA|world model]] for recommendation systems by providing a structured environment where user behavior, platform dynamics, and catalog interactions can be modeled probabilistically. The framework maps traditional world model concepts to recommendation system equivalents: the environment represents user behavior combined with platform dynamics and item catalogs, states capture latent user preferences and interaction history, actions correspond to recommendation decisions, and transitions model how user preferences evolve after receiving recommendations. ^[world-models-in-recommendation-systems.md]

## Architecture and Components

The framework implements a four-component architecture that includes user models, item dynamics, platform mechanics, and recommendation policies. RecSim NG is designed to handle the unique challenges of recommendation systems that make direct application of traditional world model approaches like Dreamer or MuZero impractical, including massive action spaces with millions of items, per-user dynamics where each user represents a different environment, extreme partial observability of user preferences, and multi-agent interactions between users, creators, and platforms. ^[world-models-in-recommendation-systems.md]

## Industry Applications

Google has deployed RecSim NG for YouTube Music preference elicitation, as documented in SIGIR 2024 research. The framework is used primarily for offline policy evaluation, allowing researchers to test recommendation strategies without direct user experimentation. This application demonstrates the practical utility of world model approaches in large-scale recommendation systems. ^[world-models-in-recommendation-systems.md]

## Relationship to World Models

RecSim NG represents part of the emerging field of world models in recommendation systems, which has experienced rapid growth from 2024-2026. While world model concepts have been implicitly used in recommendation systems since 2019-2020 under different names like "user simulators" and "environment models," explicit world model framing emerged around 2021 and has accelerated significantly in recent years. The framework addresses the fundamental challenge that traditional world model architectures cannot be directly applied to recommendation systems due to their unique characteristics. ^[world-models-in-recommendation-systems.md]

## Technical Capabilities

The framework enables multi-step user trajectory simulation through rollout and imagination capabilities, allowing researchers to predict how users might respond to sequences of recommendations over time. This probabilistic and differentiable design supports gradient-based optimization of recommendation policies and enables sophisticated modeling of user preference evolution and platform dynamics. ^[world-models-in-recommendation-systems.md]
