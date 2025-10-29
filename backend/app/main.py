from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.model import TestRunRequest, TestRunResult
from app.db import init_db
from app import runner, graph_builder
import os, uuid, time
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Selenium MCP Flow Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = init_db()
runs_coll = db["test_runs"]

@app.post("/api/run", status_code=202)
async def trigger_run(req: TestRunRequest, background_tasks: BackgroundTasks):
    run_id = uuid.uuid4().hex
    run_doc = {
        "run_id": run_id,
        "test_case": req.test_case,
        "test_scenario": req.test_scenario,
        "url": req.url,
        "status": "pending",
        "started_at": None,
        "ended_at": None,
        "nodes": [],
        "edges": [],
        "logs": []
    }
    await runs_coll.insert_one(run_doc)
    # schedule background execution
    background_tasks.add_task(_execute_run, run_id, req.dict())
    return {"run_id": run_id, "status": "scheduled"}

async def _execute_run(run_id: str, req_dict):
    # update status running
    await runs_coll.update_one({"run_id": run_id}, {"$set": {"status":"running", "started_at": time.time()}})
    # execute selenium runner synchronously (calls remote webdriver)
    res = runner.run_test_flow(req_dict["url"], req_dict.get("test_steps", []))
    # build graph model
    graph = graph_builder.build_graph_from_nodes_edges(res.get("nodes", []), res.get("edges", []))
    # update doc
    await runs_coll.update_one({"run_id": run_id}, {"$set":{
        "status": res.get("status","completed"),
        "ended_at": time.time(),
        "nodes": res.get("nodes", []),
        "edges": res.get("edges", []),
        "graph": graph,
        "logs": res.get("logs", [])
    }})

@app.get("/api/result/{run_id}")
async def get_result(run_id: str):
    doc = await runs_coll.find_one({"run_id": run_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Run not found")
    # convert ObjectId if present etc.
    return doc

@app.get("/api/export/json/{run_id}")
async def export_json(run_id: str):
    doc = await runs_coll.find_one({"run_id": run_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Run not found")
    # return graph JSON
    return {"run_id": run_id, "graph": doc.get("graph", {}), "meta": {"test_case": doc.get("test_case"), "url": doc.get("url")}}
