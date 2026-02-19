from flask import Flask, render_template, request, jsonify
import pandas as pd
import networkx as nx
import time
import uuid

app = Flask(__name__)

def detect_patterns(G):
    suspicious_accounts = {}
    fraud_rings = []
    ring_count = 1

    # ---- Cycle Detection ----
    cycles = list(nx.simple_cycles(G))
    for cycle in cycles:
        if 3 <= len(cycle) <= 5:
            ring_id = f"RING_{ring_count:03}"
            fraud_rings.append({
                "ring_id": ring_id,
                "member_accounts": cycle,
                "pattern_type": "cycle",
                "risk_score": 90.0
            })
            for acc in cycle:
                suspicious_accounts[acc] = suspicious_accounts.get(acc, 0) + 40
            ring_count += 1

    # ---- Fan-in / Fan-out ----
    for node in G.nodes():
        if G.in_degree(node) >= 5:
            suspicious_accounts[node] = suspicious_accounts.get(node, 0) + 30
        if G.out_degree(node) >= 5:
            suspicious_accounts[node] = suspicious_accounts.get(node, 0) + 30

    # ---- Format Suspicious Output ----
    suspicious_list = []
    for acc, score in suspicious_accounts.items():
        suspicious_list.append({
            "account_id": acc,
            "suspicion_score": min(score, 100),
            "detected_patterns": ["cycle_or_smurfing"],
            "ring_id": "MULTI"
        })

    suspicious_list = sorted(suspicious_list,
                             key=lambda x: x["suspicion_score"],
                             reverse=True)

    return suspicious_list, fraud_rings

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    start_time = time.time()

    if 'file' in request.files:
        file = request.files['file']
        df = pd.read_csv(file)
    else:
        data = request.json
        df = pd.DataFrame(data)

    G = nx.DiGraph()

    for _, row in df.iterrows():
        G.add_edge(row['sender_id'], row['receiver_id'])

    suspicious_accounts, fraud_rings = detect_patterns(G)

    result = {
        "suspicious_accounts": suspicious_accounts,
        "fraud_rings": fraud_rings,
        "summary": {
            "total_accounts_analyzed": len(G.nodes),
            "suspicious_accounts_flagged": len(suspicious_accounts),
            "fraud_rings_detected": len(fraud_rings),
            "processing_time_seconds": round(time.time() - start_time, 2)
        }
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run()
