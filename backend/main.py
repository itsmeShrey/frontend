from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Node(BaseModel):
    id: str
    type: str

class Edge(BaseModel):
    source: str
    target: str

class PipelineRequest(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

def is_directed_acyclic_graph(nodes: List[Node], edges: List[Edge]) -> bool:
    # Create adjacency list representation
    graph = {node.id: [] for node in nodes}
    for edge in edges:
        graph[edge.source].append(edge.target)
    
    # Track visited and recursion stack for cycle detection
    visited = set()
    rec_stack = set()
    
    def has_cycle(node):
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    # Check for cycles in the graph
    for node in graph:
        if node not in visited:
            if has_cycle(node):
                return False
    
    return True

@app.post("/pipelines/parse")
async def parse_pipeline(request: PipelineRequest):
    try:
        # Calculate number of nodes and edges
        num_nodes = len(request.nodes)
        num_edges = len(request.edges)
        
        # Check if the graph is a DAG
        is_dag = is_directed_acyclic_graph(request.nodes, request.edges)
        
        return {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "is_dag": is_dag
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# You can keep other existing routes/configurations