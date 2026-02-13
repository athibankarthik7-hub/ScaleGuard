from models import ServiceNode, DependencyEdge, SystemGraph
import random
import networkx as nx

def generate_mock_system() -> SystemGraph:
    nodes = []
    edges = []
    
    # Define tiers
    frontend_services = ["Web App", "Mobile API", "Landing Page"]
    backend_services = ["Auth Service", "User Service", "Payment Service", "Order Service", "Search Service", "Notification Service", "Inventory Service"]
    data_stores = ["Primary DB", "User DB", "Payment DB", "Search Index (ES)", "Cache (Redis)"]
    external_services = ["Stripe API", "SendGrid", "Twilio"]
    
    # Helper to create node
    def create_node(name, type, tier):
        id = name.lower().replace(" ", "-").replace("(", "").replace(")", "")
        return ServiceNode(
            id=id,
            name=name,
            type=type,
            tier=tier,
            status="healthy",
            cpu_usage=random.uniform(5, 25),  # Lower baseline CPU
            memory_usage=random.uniform(15, 35),  # Lower baseline memory
            latency=random.uniform(10, 80),
            rpm=random.randint(50, 500),  # Lower baseline requests
            error_rate=random.uniform(0.05, 1.0),  # Lower error rates
            connection_pool_usage=random.uniform(10, 40) if type == "database" else 0.0,
            queue_depth=random.randint(0, 100) if type in ["service", "external"] else 0,
            centrality_score=0.0  # Will be calculated during simulation
        )

    # Create nodes
    for name in frontend_services:
        nodes.append(create_node(name, "service", "frontend"))
    
    for name in backend_services:
        nodes.append(create_node(name, "service", "backend"))
        
    for name in data_stores:
        nodes.append(create_node(name, "database", "data"))
        
    for name in external_services:
        nodes.append(create_node(name, "external", "external"))
        
    # Helper to find node by name
    def get_id(name):
        return name.lower().replace(" ", "-").replace("(", "").replace(")", "")
    
    # Create edges (Dependencies)
    dependencies = [
        ("Web App", "Auth Service"),
        ("Web App", "Search Service"),
        ("Web App", "Order Service"),
        ("Mobile API", "Auth Service"),
        ("Mobile API", "User Service"),
        ("Landing Page", "User Service"),
        
        ("Auth Service", "User DB"),
        ("User Service", "User DB"),
        ("User Service", "Cache (Redis)"),
        
        ("Order Service", "Payment Service"),
        ("Order Service", "Inventory Service"),
        ("Order Service", "Primary DB"),
        
        ("Payment Service", "Payment DB"),
        ("Payment Service", "Stripe API"),
        
        ("Search Service", "Search Index (ES)"),
        ("Inventory Service", "Primary DB"),
        
        ("Notification Service", "SendGrid"),
        ("Notification Service", "Twilio"),
        ("Order Service", "Notification Service") # Async event
    ]
    
    for source, target in dependencies:
        edges.append(DependencyEdge(
            source=get_id(source),
            target=get_id(target),
            type="http",
            latency=random.uniform(1, 10),
            throughput=random.randint(50, 500)
        ))
        
    return SystemGraph(nodes=nodes, edges=edges)
