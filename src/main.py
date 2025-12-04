"""
Main Entry Point

Can run in two modes:
1. CLI mode: Interactive terminal-based agent
2. Server mode: FastAPI server for web UI
"""

import argparse
import os
import sys
import uuid


def run_cli():
    """Run the agent in CLI mode"""
    from .schema import SessionState
    from .agent import Agent
    from .outputs import save_all_outputs
    
    print("=" * 60)
    print("  TERM SHEET GENERATOR")
    print("  AI-powered document generation with human-in-the-loop")
    print("=" * 60)
    print()
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Run: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Initialize
    session = SessionState(session_id=str(uuid.uuid4()))
    agent = Agent()
    
    print("Starting term sheet extraction...")
    print("Type 'quit' to exit, 'generate' to create final document")
    print()
    
    # Initial extraction
    response = agent.process_message(session, "Start extraction")
    print(f"\n🤖 Agent: {response}\n")
    
    # Chat loop
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting...")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nExiting...")
            break
        
        response = agent.process_message(session, user_input)
        print(f"\n🤖 Agent: {response}\n")
        
        # Check if complete
        if session.agent_state.value == "complete":
            print("\n" + "=" * 60)
            print("Saving outputs to out/ directory...")
            
            outputs = save_all_outputs(session)
            
            print("\nGenerated files:")
            for name, path in outputs.items():
                print(f"  ✓ {path}")
            
            print("\nDone! You can view the term sheet at out/term_sheet.md")
            break


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server"""
    import uvicorn
    from .api import app
    
    print(f"Starting server at http://{host}:{port}")
    print("API docs available at http://localhost:8000/docs")
    
    uvicorn.run(app, host=host, port=port)


def main():
    parser = argparse.ArgumentParser(description="Term Sheet Generator")
    parser.add_argument(
        "--mode",
        choices=["cli", "server"],
        default="server",
        help="Run mode: 'cli' for terminal, 'server' for web API (default: server)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "cli":
        run_cli()
    else:
        run_server(args.host, args.port)


if __name__ == "__main__":
    main()
