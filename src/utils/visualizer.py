# src/utils/visualizer.py

from src.pipeline.workflow import create_workflow

def get_mermaid_graph() -> str:
    """
    Returns the Mermaid string for the compiled LangGraph.
    """
    # Note: We compile without checkpointer here just to get the diagram
    workflow = create_workflow()
    return workflow.get_graph().draw_mermaid()

def get_interactive_mermaid_html(mermaid_code: str) -> str:
    """
    Returns an HTML string that uses mermaid.js to render the graph with zoom/pan.
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
        <style>
            #graph-container {{
                width: 100%;
                height: 600px;
                overflow: hidden;
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                cursor: grab;
            }}
            #mermaid-graph {{
                width: 100%;
                height: 100%;
            }}
        </style>
    </head>
    <body>
        <div id="graph-container">
            <pre class="mermaid" id="mermaid-graph">
                {mermaid_code}
            </pre>
        </div>

        <script>
            mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
            
            // Wait for mermaid to render, then add zoom/pan
            setTimeout(() => {{
                const svg = d3.select("#graph-container svg");
                const container = d3.select("#graph-container");
                
                const zoom = d3.zoom()
                    .scaleExtent([0.1, 10])
                    .on("zoom", (event) => {{
                        svg.attr("transform", event.transform);
                    }});
                
                container.call(zoom);
                
                // Initial center
                const initialTransform = d3.zoomIdentity.translate(50, 50).scale(0.8);
                container.call(zoom.transform, initialTransform);
            }}, 1000);
        </script>
    </body>
    </html>
    """
    return html
