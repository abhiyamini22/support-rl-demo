# 🏆 Smart Customer Support Environment (OpenEnv)

A complete, real-world OpenEnv environment where AI agents learn to handle customer support tickets efficiently through the standard `step()`/`reset()`/`state()` API.

## 🚀 Overview

This environment simulates a realistic customer support workflow where agents must:
- **Prioritize tickets** based on urgency and sentiment
- **Choose appropriate responses** (escalate, auto-reply, request info)
- **Maximize customer satisfaction** while minimizing resolution time
- **Handle diverse ticket categories** (payment, security, technical, billing, general)

## 🎯 Environment Features

### Real-World Task Simulation
- **Multiple ticket categories** with realistic customer queries
- **Priority levels** (urgent, normal, low) requiring different handling strategies
- **Customer sentiment tracking** affecting satisfaction scores
- **Resolution time monitoring** impacting performance metrics
- **Performance feedback** with partial progress signals

### OpenEnv Compliance
- ✅ **Typed models** using Pydantic for Action, Observation, State
- ✅ **Standard API**: `step()`, `reset()`, `state()` methods
- ✅ **FastAPI server** for HTTP/WebSocket communication
- ✅ **openenv.yaml** configuration with full specification
- ✅ **Docker deployment** ready for Hugging Face Spaces

## � Three Difficulty Levels

### Easy Support Handling
- **10 tickets** with clear priority indicators
- **Focus**: Basic response patterns and prioritization
- **Success**: Average satisfaction ≥ 0.6, resolution time ≤ 5 minutes
- **Pass threshold**: 50% score

### Medium Support Handling  
- **20 tickets** with mixed priorities and complex scenarios
- **Focus**: Balanced decision-making and resource allocation
- **Success**: Satisfaction ≥ 0.7, escalation rate ≤ 30%
- **Pass threshold**: 60% score

### Hard Support Handling
- **30 tickets** including ambiguous cases and edge cases
- **Focus**: Sophisticated decision-making and consistency
- **Success**: Satisfaction ≥ 0.8, escalation rate ≤ 25%
- **Pass threshold**: 75% score

## 🎮 Action Space

Agents choose from 4 response types:

| Action | Description | Best For |
|--------|-------------|----------|
| `escalate` | Escalate to human agent | Urgent security/payment issues |
| `auto_reply` | Send automated response | Low priority general inquiries |
| `ask_info` | Request more information | Normal priority billing/logistics |
| `ignore` | Ignore ticket | Generally not recommended |

## 👁️ Observation Space

Each observation contains:
- **Ticket details**: ID, query, priority, customer info, sentiment, category
- **Action outcome**: Success status, customer satisfaction, resolution time
- **Feedback**: Detailed explanation of action consequences

## 🧠 Baseline Agents

### Random Agent
- Makes random choices among all actions
- Provides performance floor for comparison

### Rule-Based Agent  
- Uses fixed keyword and priority rules
- Demonstrates deterministic logic performance

### Configurable Baseline Agent
- Combines sentiment analysis with keyword matching
- Configurable thresholds for different strategies
- Provides strong baseline for comparison

## ⚙️ Setup Instructions

### Local Development

1. **Install dependencies**:
```bash
pip install -r requirements.txt
pip install -r envs/support_env/server/requirements.txt
```

2. **Run environment server**:
```bash
cd envs/support_env/server
uvicorn app:app --host 0.0.0.0 --port 8000
```

3. **Run baseline evaluation**:
```bash
python baseline_agent.py --difficulty medium --episodes 20
```

4. **Evaluate all agents**:
```bash
python baseline_agent.py --all --episodes 10
```

### Hugging Face Spaces Deployment

1. **Push to Hugging Face Spaces**:
```bash
# The environment is ready for HF Spaces deployment
# Dockerfile and configuration are included
```

2. **Access the deployed environment**:
- Environment server runs on port 8000
- Health check available at `/health`
- Full OpenEnv API compatibility

## 📈 Evaluation Metrics

### Primary Metrics
- **Score**: Overall performance (0.0-1.0)
- **Customer Satisfaction**: Average satisfaction across tickets
- **Resolution Time**: Average time to resolve tickets
- **Escalation Rate**: Percentage of tickets escalated

### Advanced Metrics (Hard Mode)
- **Priority Handling**: Correct urgent ticket escalation rate
- **Category Performance**: Consistency across ticket categories  
- **Consistency Score**: Performance variance across episodes

## 🏗️ Architecture

```
envs/support_env/
├── models.py              # Typed models (Action, Observation, State)
├── server/
│   ├── my_environment.py  # Core environment logic
│   ├── app.py            # FastAPI server
│   ├── requirements.txt  # Server dependencies
│   └── Dockerfile        # Server container
├── client.py             # Environment client
├── graders.py           # Task graders (easy/medium/hard)
└── __init__.py          # Package exports
```

## 🧪 Quick Start

### Python API Usage

```python
from envs.support_env import SupportEnvironmentClient, SupportAction, ResponseType

# Initialize client
client = SupportEnvironmentClient("http://localhost:8000")

# Reset environment
observation = client.reset(difficulty="medium")

# Run episode
for step in range(20):
    # Select action (example: escalate urgent tickets)
    if observation.ticket.priority == "urgent":
        action = SupportAction(
            response_type=ResponseType.ESCALATE,
            escalation_reason="Urgent ticket detected"
        )
    else:
        action = SupportAction(response_type=ResponseType.ASK_INFO)
    
    # Execute action
    observation = client.step(action)
    print(f"Satisfaction: {observation.customer_satisfaction:.2f}")
    
    # Check if episode ended
    state = client.state()
    if state.current_ticket is None:
        break
```

### Command Line Evaluation

```bash
# Evaluate baseline agent on medium difficulty
python baseline_agent.py --agent baseline --difficulty medium --episodes 20

# Compare all agents across all difficulties
python baseline_agent.py --all --episodes 10

# Test specific difficulty with reproducible results
python baseline_agent.py --difficulty hard --episodes 5 --seed 123
```

## 📊 Sample Results

```
============================================================
Agent: Baseline Agent
Difficulty: medium
============================================================
Average Score: 0.742
Average Reward: 0.681
Pass Rate: 85.0% (17/20)
Score Std Dev: 0.089
```

## 🌐 Live Demo

Deployed on Hugging Face Spaces:
https://abhiyamini-support-rl-demo.hf.space

## 🔬 Research Applications

This environment is suitable for:
- **Reinforcement Learning**: Multi-step decision making with sparse rewards
- **Natural Language Understanding**: Query classification and sentiment analysis
- **Priority Management**: Resource allocation under constraints
- **Customer Service AI**: Real-world support automation
- **Curriculum Learning**: Progressive difficulty scaling

## 📝 License

This project is part of the OpenEnv framework and follows the same licensing terms.

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows OpenEnv specifications
- Tests pass for all difficulty levels
- Documentation is updated
- Docker builds successfully