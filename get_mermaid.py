from src.pipeline.workflow import create_workflow

def get_mermaid():
    workflow = create_workflow()
    print(workflow.get_graph().draw_mermaid())

if __name__ == "__main__":
    get_mermaid()
