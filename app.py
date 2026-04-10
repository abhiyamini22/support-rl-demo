import gradio as gr
import os
from typing import Dict, Any

# Simple demo for Hugging Face Spaces
class CustomerSupportDemo:
    def __init__(self):
        pass
    
    def smart_action(self, query: str) -> str:
        """Simple rule-based action selection."""
        query = query.lower()
        
        if "hacked" in query or "payment" in query or "system down" in query:
            return "escalate"
        elif "refund" in query or "delivery" in query or "feature" in query:
            return "ask_info"
        elif "hello" in query or "thank" in query or "discount" in query or "hi" in query:
            return "auto_reply"
        else:
            return "ask_info"
    
    def simulate_episode(self, difficulty: str = "medium", max_steps: int = 10) -> Dict[str, Any]:
        """Run a demo episode simulation."""
        import uuid
        import time
        import random
        
        # Demo ticket scenarios
        demo_tickets = [
            ("payment failed", "urgent"),
            ("hello", "low"),
            ("refund status", "normal"),
            ("account hacked", "urgent"),
            ("discount?", "low"),
            ("system down", "urgent"),
            ("delivery issue", "normal"),
            ("feature request", "low"),
            ("billing question", "normal"),
            ("thank you", "low")
        ]
        
        logs = []
        total_reward = 0
        
        for i, (query, priority) in enumerate(demo_tickets[:max_steps]):
            action = self.smart_action(query)
            
            # Mock reward based on action appropriateness
            if priority == "urgent" and action == "escalate":
                reward = 0.9
            elif priority == "low" and action == "auto_reply":
                reward = 0.8
            elif priority == "normal" and action == "ask_info":
                reward = 0.7
            else:
                reward = 0.3
            
            total_reward += reward
            
            logs.append({
                "step": i + 1,
                "query": query,
                "priority": priority,
                "action": action,
                "satisfaction": random.uniform(0.6, 0.9),
                "resolution_time": random.uniform(1.0, 10.0),
                "reward": reward,
                "feedback": f"Demo feedback for {action}"
            })
        
        # Format logs for display
        output = ["Step | Query | Priority | Action | Satisfaction | Time | Reward", 
                 "-----|-------|----------|--------|--------------|------|-------"]
        
        for log in logs:
            output.append(
                f"{log['step']:4} | {log['query'][:15]:15} | {log['priority']:8} | "
                f"{log['action']:6} | {log['satisfaction']:11.2f} | {log['resolution_time']:4.1f} | {log['reward']:5.2f}"
            )
        
        log_text = "\n".join(output)
        
        return {
            "logs": log_text,
            "total_reward": total_reward,
            "steps": len(logs),
            "avg_reward": total_reward / len(logs) if logs else 0
        }
    
    def test_query(self, query: str) -> str:
        """Test a single query."""
        action = self.smart_action(query)
        
        explanations = {
            "escalate": "This query requires immediate human attention due to urgency/security concerns.",
            "auto_reply": "This is a low-priority query that can be handled automatically.",
            "ask_info": "This requires more information to provide proper assistance.",
            "ignore": "This query does not require action."
        }
        
        explanation = explanations.get(action, "Action selected based on query analysis.")
        
        return f"**Predicted Action:** {action.upper()}\n\n**Reason:** {explanation}"

# Create demo instance
demo = CustomerSupportDemo()

# Create Gradio interfaces
def create_simulation_interface():
    """Create the simulation interface."""
    def run_simulation(difficulty, max_steps):
        result = demo.simulate_episode(difficulty, max_steps)
        return (
            result["logs"],
            f"Total Reward: {result['total_reward']:.2f}\n"
            f"Steps: {result['steps']}\n"
            f"Average Reward: {result['avg_reward']:.2f}"
        )
    
    return gr.Interface(
        fn=run_simulation,
        inputs=[
            gr.Dropdown(
                choices=["easy", "medium", "hard"],
                value="medium",
                label="Difficulty Level"
            ),
            gr.Slider(
                minimum=5,
                maximum=30,
                value=10,
                step=1,
                label="Max Steps"
            )
        ],
        outputs=[
            gr.Textbox(
                label="Episode Logs",
                lines=15,
                max_lines=20
            ),
            gr.Textbox(
                label="Summary"
            )
        ],
        title="Customer Support Simulation",
        description="Run a full episode simulation of the customer support environment"
    )

def create_query_interface():
    """Create the single query testing interface."""
    return gr.Interface(
        fn=demo.test_query,
        inputs=gr.Textbox(
            label="Customer Query",
            placeholder="Enter a customer support query...",
            lines=3
        ),
        outputs=gr.Markdown(label="Action Prediction"),
        title="Query Action Predictor",
        description="Test how the agent would respond to individual customer queries"
    )

def create_info_interface():
    """Create information interface about the environment."""
    info_content = """
# Customer Support Environment

## Environment Overview
This is a real-world environment where AI agents learn to handle customer support tickets efficiently.

## Key Features
- **Real-world task**: Customer support ticket triage and response
- **Three difficulty levels**: Easy (10 tickets), Medium (20 tickets), Hard (30 tickets)
- **Multiple actions**: Escalate, Auto-reply, Ask for info, Ignore
- **Rich observations**: Ticket details, customer sentiment, resolution metrics
- **Dense rewards**: Partial progress signals throughout episodes

## Action Space
| Action | Best For | Description |
|--------|----------|-------------|
| ESCALATE | Urgent issues | Send to human agent |
| AUTO_REPLY | Low priority | Automated response |
| ASK_INFO | Normal priority | Request more details |
| IGNORE | Spam/irrelevant | Generally not recommended |

## Performance Metrics
- **Customer Satisfaction**: Primary success metric (0.0-1.0)
- **Resolution Time**: Efficiency measure
- **Escalation Rate**: Resource utilization
- **Priority Handling**: Correct urgent ticket processing

## Usage
1. Use the Simulation tab to run full episodes
2. Use the Query Test tab to test individual queries
3. Check environment logs for detailed performance metrics

## OpenEnv Compliance
- Typed models (Pydantic)
- Standard API (step/reset/state)
- FastAPI server
- Docker deployment ready
- openenv.yaml configuration
    """
    
    return gr.Interface(
        fn=lambda: info_content,
        inputs=[],
        outputs=gr.Markdown(label="Environment Information"),
        title="Environment Information",
        description="Learn about the Customer Support Environment"
    )

# Create the main app
simulation_demo = create_simulation_interface()
query_demo = create_query_interface()
info_demo = create_info_interface()

# Launch with tabbed interface
app = gr.TabbedInterface(
    [simulation_demo, query_demo, info_demo],
    ["Simulation", "Query Test", "Info"],
    title="Customer Support Environment"
)

if __name__ == "__main__":
    # Launch the app
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
