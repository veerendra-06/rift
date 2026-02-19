let manualData = [];
let lastResult = null;

function addTransaction() {
    const sender = document.getElementById("sender").value;
    const receiver = document.getElementById("receiver").value;

    manualData.push({
        transaction_id: Date.now(),
        sender_id: sender,
        receiver_id: receiver,
        amount: 100,
        timestamp: "2026-02-19 10:00:00"
    });

    alert("Transaction Added");
}

async function analyzeManual() {
    const response = await fetch("/analyze", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(manualData)
    });

    const data = await response.json();
    lastResult = data;
    drawGraph(data);
}

function drawGraph(data) {
    const nodes = [];
    const edges = [];

    const accounts = new Set();

    data.suspicious_accounts.forEach(acc => {
        nodes.push({
            id: acc.account_id,
            label: acc.account_id,
            color: "red",
            size: 30
        });
        accounts.add(acc.account_id);
    });

    const container = document.getElementById("network");
    const network = new vis.Network(container,
        {nodes: nodes, edges: edges}, {});
}

function downloadJSON() {
    const blob = new Blob([JSON.stringify(lastResult, null, 2)], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "fraud_result.json";
    a.click();
}
