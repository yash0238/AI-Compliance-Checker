from src.pipeline.workflow import create_workflow
import os

def visualize():
    workflow = create_workflow()
    
    # Option 1: Generate Mermaid string (can be pasted into Mermaid Live Editor)
    mermaid_graph = workflow.get_graph().draw_mermaid()
    print("--- MERMAID GRAPH START ---")
    print(mermaid_graph)
    print("--- MERMAID GRAPH END ---")
    
    # Option 2: Try to save as PNG (requires certain dependencies like pygraphviz or similar, 
    # but often works with direct web-based rendering in some environments)
    try:
        png_data = workflow.get_graph().draw_mermaid_png()
        output_path = "graph_visualization.png"
        with open(output_path, "wb") as f:
            f.write(png_data)
        print(f"Graph visualization saved to: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"Could not generate PNG: {e}")
        print("Tip: Copy the Mermaid block above to https://mermaid.live to see the graph.")

if __name__ == "__main__":
    visualize()
