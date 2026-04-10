from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import gradio as gr
import uuid
import random
import time
import json
import threading
from contextlib import asynccontextmanager

# Pydantic models for OpenEnv
class SupportTicket(BaseModel):
    ticket_id: str
    query: str
    priority: str
    customer_id: str
    timestamp: int
    sentiment: float
    category: str

class SupportAction(BaseModel):
    response_type: str
    response_text: Optional[str] = None
    escalation_reason: Optional[str] = None

class SupportObservation(BaseModel):
    ticket: Optional[SupportTicket]
    success: bool
    customer_satisfaction: float
    resolution_time: float
    feedback: Optional[str] = None

class SupportState(BaseModel):
    episode_id: str
    step_count: int = 0
    total_tickets: int = 0
    resolved_tickets: int = 0
    average_satisfaction: float = 0.0
    current_ticket: Optional[SupportTicket] = None
    tickets_history: List[SupportTicket] = []
    performance_metrics: Dict[str, float] = {}

# Global environment instance
env_instance = None

class CustomerSupportEnv:
    def __init__(self):
        self.current_ticket = None
        self.step_count = 0
        self.episode_id = None
        self.ticket_pool = self._generate_tickets()
        self.current_ticket_index = 0
        
    def _generate_tickets(self) -> List[Dict]:
        """Generate ticket pool."""
        base_tickets = [
            {"query": "payment failed", "priority": "urgent", "category": "payment"},
            {"query": "hello", "priority": "low", "category": "general"},
            {"query": "refund status", "priority": "normal", "category": "billing"},
            {"query": "account hacked", "priority": "urgent", "category": "security"},
            {"query": "discount?", "priority": "low", "category": "general"},
            {"query": "system down", "priority": "urgent", "category": "technical"},
            {"query": "delivery issue", "priority": "normal", "category": "logistics"},
            {"query": "feature request", "priority": "low", "category": "product"},
            {"query": "billing question", "priority": "normal", "category": "billing"},
            {"query": "thank you", "priority": "low", "category": "general"},
        ]
        return base_tickets * 2  # 20 tickets for medium difficulty
    
    def reset(self, difficulty: str = "medium") -> SupportObservation:
        """Reset environment for OpenEnv API."""
        self.episode_id = str(uuid.uuid4())
        self.step_count = 0
        self.current_ticket_index = 0
        self.ticket_pool = self._generate_tickets()
        
        if self.ticket_pool:
            ticket_data = self.ticket_pool[self.current_ticket_index]
            self.current_ticket = SupportTicket(
                ticket_id=f"TK-{uuid.uuid4().hex[:8]}",
                query=ticket_data["query"],
                priority=ticket_data["priority"],
                customer_id="CUST-1234",
                timestamp=int(time.time()),
                sentiment=random.uniform(0.2, 0.9),
                category=ticket_data["category"]
            )
            
            return SupportObservation(
                ticket=self.current_ticket,
                success=True,
                customer_satisfaction=0.7,
                resolution_time=0.0,
                feedback="Episode started"
            )
        else:
            return SupportObservation(
                ticket=None,
                success=False,
                customer_satisfaction=0.0,
                resolution_time=0.0,
                feedback="No tickets available"
            )
    
    def step(self, action: SupportAction) -> tuple[SupportObservation, float, bool, Dict[str, Any]]:
        """Execute step for OpenEnv API."""
        if not self.current_ticket or self.current_ticket_index >= len(self.ticket_pool):
            return (
                SupportObservation(
                    ticket=None,
                    success=False,
                    customer_satisfaction=0.0,
                    resolution_time=0.0,
                    feedback="Episode ended"
                ), 0.0, True, {}
            )
        
        ticket = self.current_ticket
        action_type = action.response_type
        priority = ticket.priority
        
        # Calculate reward based on action appropriateness
        if priority == "urgent" and action_type == "escalate":
            reward = 0.9
        elif priority == "low" and action_type == "auto_reply":
            reward = 0.8
        elif priority == "normal" and action_type == "ask_info":
            reward = 0.7
        else:
            reward = 0.3
        
        self.step_count += 1
        self.current_ticket_index += 1
        
        # Check if episode is done
        done = self.current_ticket_index >= len(self.ticket_pool)
        
        if not done:
            ticket_data = self.ticket_pool[self.current_ticket_index]
            self.current_ticket = SupportTicket(
                ticket_id=f"TK-{uuid.uuid4().hex[:8]}",
                query=ticket_data["query"],
                priority=ticket_data["priority"],
                customer_id="CUST-1234",
                timestamp=int(time.time()),
                sentiment=random.uniform(0.2, 0.9),
                category=ticket_data["category"]
            )
            
            observation = SupportObservation(
                ticket=self.current_ticket,
                success=True,
                customer_satisfaction=random.uniform(0.6, 0.9),
                resolution_time=random.uniform(1.0, 10.0),
                feedback=f"Action {action_type} executed"
            )
        else:
            observation = SupportObservation(
                ticket=None,
                success=True,
                customer_satisfaction=0.8,
                resolution_time=5.0,
                feedback="Episode completed"
            )
        
        info = {
            "step": self.step_count,
            "episode_id": self.episode_id
        }
        
        return observation, reward, done, info
    
    def get_state(self) -> SupportState:
        """Get current state for OpenEnv API."""
        tickets_history = []
        for ticket_data in self.ticket_pool[:self.current_ticket_index]:
            tickets_history.append(SupportTicket(
                ticket_id=f"TK-{uuid.uuid4().hex[:8]}",
                query=ticket_data["query"],
                priority=ticket_data["priority"],
                customer_id="CUST-1234",
                timestamp=int(time.time()),
                sentiment=random.uniform(0.2, 0.9),
                category=ticket_data["category"]
            ))
        
        return SupportState(
            episode_id=self.episode_id or str(uuid.uuid4()),
            step_count=self.step_count,
            total_tickets=len(self.ticket_pool),
            resolved_tickets=self.current_ticket_index,
            average_satisfaction=0.75,
            current_ticket=self.current_ticket,
            tickets_history=tickets_history,
            performance_metrics={
                "avg_resolution_time": 5.0,
                "escalation_rate": 0.2,
                "satisfaction_score": 0.75
            }
        )

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize environment
    global env_instance
    env_instance = CustomerSupportEnv()
    yield
    # Cleanup if needed

app = FastAPI(
    title="Customer Support Environment",
    description="OpenEnv-compatible customer support environment",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenEnv API endpoints
@app.post("/reset")
async def reset_endpoint(difficulty: str = "medium"):
    """Reset environment endpoint."""
    try:
        if env_instance is None:
            env_instance = CustomerSupportEnv()
        
        observation = env_instance.reset(difficulty)
        return observation.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step")
async def step_endpoint(action: SupportAction):
    """Step endpoint."""
    try:
        if env_instance is None:
            env_instance = CustomerSupportEnv()
        
        observation, reward, done, info = env_instance.step(action)
        
        return {
            "observation": observation.dict(),
            "reward": reward,
            "done": done,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def state_endpoint():
    """State endpoint."""
    try:
        if env_instance is None:
            env_instance = CustomerSupportEnv()
        
        state = env_instance.get_state()
        return state.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_endpoint():
    """Health check endpoint."""
    return {"status": "healthy", "openenv_available": True}

# Gradio interface functions
def gradio_reset(difficulty: str):
    """Gradio reset function."""
    if env_instance is None:
        env_instance = CustomerSupportEnv()
    
    observation = env_instance.reset(difficulty)
    return json.dumps(observation.dict(), indent=2)

def gradio_step(action_json: str):
    """Gradio step function."""
    try:
        if env_instance is None:
            env_instance = CustomerSupportEnv()
        
        action_data = json.loads(action_json)
        action = SupportAction(**action_data)
        
        observation, reward, done, info = env_instance.step(action)
        
        result = {
            "observation": observation.dict(),
            "reward": reward,
            "done": done,
            "info": info
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

def gradio_state():
    """Gradio state function."""
    if env_instance is None:
        env_instance = CustomerSupportEnv()
    
    state = env_instance.get_state()
    return json.dumps(state.dict(), indent=2)

def gradio_health():
    """Gradio health function."""
    return json.dumps({"status": "healthy", "openenv_available": True}, indent=2)

# Create Gradio interface
def create_gradio_interface():
    """Create the Gradio interface."""
    with gr.Blocks(title="Customer Support Environment") as interface:
        gr.Markdown("# Customer Support Environment")
        
        with gr.Tabs():
            with gr.Tab("API Endpoints"):
                with gr.Tab("Reset"):
                    difficulty_input = gr.Dropdown(
                        choices=["easy", "medium", "hard"],
                        value="medium",
                        label="Difficulty"
                    )
                    reset_btn = gr.Button("Reset Environment")
                    reset_output = gr.Textbox(label="Reset Response", lines=15)
                    reset_btn.click(gradio_reset, inputs=difficulty_input, outputs=reset_output)
                
                with gr.Tab("Step"):
                    action_input = gr.Textbox(
                        label='Action JSON',
                        placeholder='{"response_type": "escalate"}',
                        lines=3
                    )
                    step_btn = gr.Button("Execute Step")
                    step_output = gr.Textbox(label="Step Response", lines=15)
                    step_btn.click(gradio_step, inputs=action_input, outputs=step_output)
                
                with gr.Tab("State"):
                    state_btn = gr.Button("Get State")
                    state_output = gr.Textbox(label="State Response", lines=15)
                    state_btn.click(gradio_state, inputs=[], outputs=state_output)
                
                with gr.Tab("Health"):
                    health_btn = gr.Button("Health Check")
                    health_output = gr.Textbox(label="Health Response", lines=5)
                    health_btn.click(gradio_health, inputs=[], outputs=health_output)
            
            with gr.Tab("Demo"):
                gr.Markdown("## Customer Support Demo")
                gr.Markdown("This is a real-world OpenEnv environment for customer support ticket handling.")
                
                with gr.Row():
                    demo_difficulty = gr.Dropdown(
                        choices=["easy", "medium", "hard"],
                        value="medium",
                        label="Difficulty"
                    )
                    demo_steps = gr.Slider(5, 30, value=10, label="Max Steps")
                
                demo_btn = gr.Button("Run Demo Episode")
                demo_output = gr.Textbox(label="Demo Results", lines=20)
                
                def run_demo(difficulty, max_steps):
                    if env_instance is None:
                        env_instance = CustomerSupportEnv()
                    
                    # Reset and run a demo episode
                    obs = env_instance.reset(difficulty)
                    results = [f"Episode started with ticket: {obs.ticket.query if obs.ticket else 'None'}"]
                    
                    for i in range(max_steps):
                        if env_instance.current_ticket is None:
                            break
                        
                        # Simple action selection
                        query = env_instance.current_ticket.query.lower()
                        if "hacked" in query or "payment" in query:
                            action_type = "escalate"
                        elif "hello" in query or "thank" in query:
                            action_type = "auto_reply"
                        else:
                            action_type = "ask_info"
                        
                        action = SupportAction(response_type=action_type)
                        obs, reward, done, info = env_instance.step(action)
                        
                        results.append(f"Step {i+1}: {action_type} -> reward: {reward:.2f}")
                        
                        if done:
                            break
                    
                    return "\n".join(results)
                
                demo_btn.click(run_demo, inputs=[demo_difficulty, demo_steps], outputs=demo_output)
    
    return interface

# Mount Gradio app
gradio_app = create_gradio_interface()
app = gr.mount_gradio_app(app, gradio_app, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
