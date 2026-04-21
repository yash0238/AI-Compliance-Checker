# run.py

import os
import json
import argparse
import sqlite3
from dotenv import load_dotenv

from langgraph.checkpoint.sqlite import SqliteSaver
from src.utils.annotate_csv import convert_m2_json_to_csv
from src.utils.pdf_writer import write_contract_pdf
from src.pipeline.workflow import create_workflow

load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Shared SQLite DB for persistence
DB_PATH = os.path.join("data", "checkpoint.sqlite")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def run_pipeline(pdf_path, thread_id="default_thread", progress_callback=None):
    """
    Executes the contract compliance pipeline using LangGraph with SQLite persistence.
    """
    try:
        print(f"\n==============================")
        print(f" AI-POWERED CONTRACT COMPLIANCE PIPELINE (LANGGRAPH) ")
        print(f" Thread ID: {thread_id} ")
        print(f"==============================\n")

        def update_progress(percent, message):
            if progress_callback:
                progress_callback(percent, message)

        # 1. Initialize Graph with Persistence
        # SqliteSaver.from_conn_string() is a context manager in newer langgraph versions
        with SqliteSaver.from_conn_string(DB_PATH) as memory:
            workflow = create_workflow().compile(checkpointer=memory)
            
            config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 50}

            # 2. Initial State
            initial_state = {
                "pdf_path": pdf_path,
                "raw_text": "",
                "clean_text": "",
                "original_header": "",
                "clauses": [],
                "assessed_clauses": [],
                "regulatory_updates": {},
                "amendments": {},
                "updated_contract_text": "",
                "compliance_report": {},
                "current_step": "Initializing",
                "progress_percentage": 5,
                "iteration_count": 0,
                "max_iterations": 2
            }

            # 3. Execute Graph with progression callback
            update_progress(5, "Initializing LangGraph Pipeline")
            
            # Check if we have an existing state to pick up from
            state = workflow.get_state(config)
            if not state.values:
                print("No existing state found. Starting new run.")
                run_input = initial_state
            else:
                print(f"Resuming existing state from step: {state.values.get('current_step')}")
                run_input = None  # When run_input is None, it resumes from checkpoint

            # Streaming execution
            for event in workflow.stream(run_input, config):
                # event is a dict of the node that just finished and its state updates
                for node_name, state_update in event.items():
                    curr_step_str = state_update.get("current_step", "Processing...")
                    pct = state_update.get("progress_percentage", 50)
                    update_progress(pct, curr_step_str)
            
            # 4. Final state retrieval after completion
            final_state = workflow.get_state(config).values

            # --------------------------------------------------
            # 5: SAVE FINAL OUTPUTS TO FILES
            # --------------------------------------------------
            base_name = os.path.basename(pdf_path).replace(".pdf", "")
            
            # A. Milestone 2 Data
            m2_json = os.path.join(OUTPUT_DIR, f"{base_name}_m2_output.json")
            with open(m2_json, "w", encoding="utf-8") as f:
                json.dump(final_state["assessed_clauses"], f, indent=2, ensure_ascii=False)
                
            m2_csv = os.path.join(OUTPUT_DIR, f"{base_name}_m2_annotations.csv")
            convert_m2_json_to_csv(m2_json, m2_csv)
            
            # B. Milestone 3 Data
            report_path = os.path.join(OUTPUT_DIR, f"{base_name}_m3_compliance_report.json")
            contract_path = os.path.join(OUTPUT_DIR, f"{base_name}_updated_contract.txt")
            pdf_contract_path = os.path.join(OUTPUT_DIR, f"{base_name}_updated_contract.pdf")

            write_contract_pdf(final_state["updated_contract_text"], pdf_contract_path)

            with open(report_path, "w", encoding="utf-8") as f:
                json.dump({
                    "compliance_report": final_state["compliance_report"],
                    "amended_clauses": list(final_state.get("amendments", {}).keys()),
                    "regulatory_updates": final_state.get("regulatory_updates", {}),
                    "thread_id": thread_id
                }, f, indent=2)

            with open(contract_path, "w", encoding="utf-8") as f:
                f.write(final_state["updated_contract_text"])

            update_progress(100, "Completed")
            print("\n==============================")
            print(" PIPELINE COMPLETED SUCCESSFULLY ")
            print("==============================")
        
    except Exception as e:
        print(f"Pipeline Failed: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run AI-Powered Contract Compliance Pipeline with Persistence"
    )
    parser.add_argument("--pdf", required=True, help="Path to contract PDF file")
    parser.add_argument("--thread", default="cli_run", help="Unique thread ID for persistence")

    args = parser.parse_args()
    run_pipeline(args.pdf, thread_id=args.thread)
