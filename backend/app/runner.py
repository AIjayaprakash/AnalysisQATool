
"""
Runner wrapper that uses the local `server.py` MCP-style helpers to execute steps
and extract node/edge information. This file provides an async `run_test_flow`
function that the rest of the backend can call. It keeps the same return shape as
previous runner: {status, started_at, ended_at, nodes, edges, logs}.

This implementation uses the functions defined in `server.py` (start_browser,
navigate, send_keys, click_element, wait_for_page_load, close_session) and the
`utils.get_driver` helper to run a small JS snippet to extract element info.
"""

import asyncio
import time
import uuid
from typing import List, Dict, Any

# Import the MCP-style helpers implemented in server.py
import server
from utils import get_driver, get_locator
from selenium_request_types import (
    BrowserType,
    BrowserOptions,
    StartBrowserRequest,
)

# JavaScript used to extract element information (id, tag, title, label, attrs, rect)
EXTRACTION_SCRIPT = """
function nodeInfo(el){
  if(!el) return null;
  const rect = el.getBoundingClientRect();
  const attrs = {};
  for(let i=0;i<el.attributes.length;i++){
    attrs[el.attributes[i].name] = el.attributes[i].value;
  }
  return {
    id: el.id || null,
    tag: el.tagName,
    title: el.title || el.getAttribute('aria-label') || null,
    label: (el.innerText && el.innerText.trim().length>0) ? el.innerText.trim() : (el.value || null),
    attributes: attrs,
    position: { x: Math.round(rect.left), y: Math.round(rect.top), width: Math.round(rect.width), height: Math.round(rect.height) }
  }
}
return nodeInfo(arguments[0]);
"""


async def _start_browser_if_needed(headless: bool = False):
    """Start a browser via server.start_browser and ensure a driver session exists."""
    # Build request
    start_req = StartBrowserRequest(browser=BrowserType.CHROME, options=BrowserOptions(headless=headless))
    resp = await server.start_browser(start_req)
    # server.start_browser sets state and current_session; we ignore resp content here
    return resp


def _selector_type(selector: str) -> str:
    """Very small heuristic to choose 'css' or 'xpath'."""
    if not selector:
        return "css"
    sel = selector.strip()
    if sel.startswith("/") or sel.startswith("(//") or sel.startswith("//"):
        return "xpath"
    return "css"


async def run_test_flow(url: str, steps: List[Dict[str, Any]], headless: bool = False):
    """
    Executes the provided steps using the server MCP helpers and returns
    nodes/edges/logs in the same format as the previous runner.

    - url: target page URL
    - steps: list of dicts with keys selector (string), action (click|send_keys|submit|hover), value (for send_keys)
    - headless: whether to start the browser headless
    """
    run_nodes: Dict[str, Dict[str, Any]] = {}
    run_edges: List[Dict[str, Any]] = []
    logs: List[str] = []
    started = time.time()

    try:
        # Start browser session
        await _start_browser_if_needed(headless=headless)

        # Navigate to url
        await server.navigate(type('Req', (), {'url': url}))  # simple NavigateRequest-like object
        # Wait for page to load
        await server.wait_for_page_load()

        prev_node_id = None

        for idx, step in enumerate(steps):
            sel = step.get('selector')
            action = step.get('action')
            value = step.get('value')

            if not sel:
                logs.append(f"Step {idx}: empty selector, skipping")
                continue

            by = _selector_type(sel)

            # Try to find element using server.find_element (which only returns simple success messages)
            # We'll directly use the driver to find element so we can extract it and perform actions.
            try:
                by_strategy, locator = get_locator(by, sel)
                driver = get_driver()

                # Use server.find_element to wait for presence/clickability instead of direct driver.find_element
                try:
                    find_resp = await server.find_element(type('Loc', (), {'by': by, 'value': sel, 'timeout': 5000}))
                    # simple check for error in response
                    contents = find_resp.get('content', []) if isinstance(find_resp, dict) else []
                    if any('Error' in c.get('text', '') for c in contents):
                        logs.append(f"Step {idx}: server.find_element reported error for {sel} - {contents}")
                        continue
                except Exception as e:
                    logs.append(f"Step {idx}: server.find_element exception for {sel} - {e}")
                    continue

                # extract node info using JS that locates element by CSS or XPath in the page
                try:
                    if by == 'css':
                        js = (
                            "const sel = arguments[0];\n"
                            "function nodeInfoWrapper(s){" + EXTRACTION_SCRIPT + "}\n"
                            "return nodeInfoWrapper(sel);"
                        )
                        info = driver.execute_script(js, sel) or {}
                    else:  # xpath
                        js = (
                            "const sel = arguments[0];\n"
                            "function nodeInfoWrapper(s){" 
                            "  const res = document.evaluate(s, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);"
                            "  const el = res.singleNodeValue;"
                            + EXTRACTION_SCRIPT + "\n"
                            "  return nodeInfo(el);"
                            "}\n"
                            "return nodeInfoWrapper(sel);"
                        )
                        info = driver.execute_script(js, sel) or {}
                except Exception as ee:
                    info = {"error": str(ee)}

                node_uid = info.get('id') or f"node-{uuid.uuid4().hex[:8]}"
                node = {
                    'id': node_uid,
                    'label': info.get('label') or info.get('title') or info.get('tag'),
                    'type': info.get('tag').lower() if info.get('tag') else None,
                    'attributes': info.get('attributes', {}),
                    'position': info.get('position', {})
                }
                run_nodes[node_uid] = node

                # perform action via server helpers where appropriate
                if action == 'click':
                    # use server.click_element which expects an ElementLocator-like object
                    await server.click_element(type('Loc', (), {'by': by, 'value': sel, 'timeout': 5000}))
                    # small delay to let navigation happen
                    await server.wait_for_page_load()
                    await asyncio.sleep(0.2)
                elif action == 'send_keys':
                    await server.send_keys(type('Req', (), {'by': by, 'value': sel, 'timeout': 5000, 'text': value or ''}))
                    await asyncio.sleep(0.1)
                elif action == 'submit':
                        # submit via JavaScript using selector (works for CSS or XPath)
                        try:
                            if by == 'css':
                                js = (
                                    "const sel = arguments[0];\n"
                                    "const el = document.querySelector(sel);\n"
                                    "if(el && typeof el.submit === 'function'){ el.submit(); return true;} return false;"
                                )
                                driver.execute_script(js, sel)
                            else:
                                js = (
                                    "const sel = arguments[0];\n"
                                    "const res = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);\n"
                                    "const el = res.singleNodeValue;\n"
                                    "if(el && typeof el.submit === 'function'){ el.submit(); return true;} return false;"
                                )
                                driver.execute_script(js, sel)
                        except Exception as se:
                            logs.append(f"Step {idx}: submit failed - {se}")
                        await server.wait_for_page_load()
                        await asyncio.sleep(0.2)
                elif action == 'hover':
                    # perform hover via JS dispatching mouseover (avoids needing Selenium element object)
                    try:
                        if by == 'css':
                            js = (
                                "const sel = arguments[0];\n"
                                "const el = document.querySelector(sel);\n"
                                "if(el){ el.scrollIntoView({block: 'center'}); const ev = new MouseEvent('mouseover', {bubbles:true, cancelable:true}); el.dispatchEvent(ev); return true;} return false;"
                            )
                            driver.execute_script(js, sel)
                        else:
                            js = (
                                "const sel = arguments[0];\n"
                                "const res = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);\n"
                                "const el = res.singleNodeValue;\n"
                                "if(el){ el.scrollIntoView({block: 'center'}); const ev = new MouseEvent('mouseover', {bubbles:true, cancelable:true}); el.dispatchEvent(ev); return true;} return false;"
                            )
                            driver.execute_script(js, sel)
                        await asyncio.sleep(0.1)
                    except Exception as he:
                        logs.append(f"Step {idx}: hover failed - {he}")
                else:
                    logs.append(f"Step {idx}: unknown action {action}, skipping")

                # build edge
                if prev_node_id:
                    edge = {
                        'id': f"edge-{uuid.uuid4().hex[:8]}",
                        'source': prev_node_id,
                        'target': node_uid,
                        'action': action
                    }
                    run_edges.append(edge) 

                prev_node_id = node_uid

            except Exception as e:
                logs.append(f"Step {idx} error: {str(e)}")
                continue

        ended = time.time()

        # close session
        try:
            await server.close_session()
        except Exception:
            pass

        result = {
            'status': 'success',
            'started_at': started,
            'ended_at': ended,
            'nodes': list(run_nodes.values()),
            'edges': run_edges,
            'logs': logs
        }
        return result

    except Exception as exc:
        logs.append(str(exc))
        # attempt cleanup
        try:
            await server.close_session()
        except Exception:
            pass
        return {'status': 'error', 'nodes': list(run_nodes.values()), 'edges': run_edges, 'logs': logs}


async def open_browser(headless: bool = False):
    """Convenience helper to explicitly start a browser session from other callers.

    Returns the response from `server.start_browser` so callers can inspect the session id.
    """
    return await _start_browser_if_needed(headless=headless)


# Allow running this file directly for quick debugging (runs in asyncio event loop)
if __name__ == '__main__':
    sample_steps = [
    {"selector": "//button[@type='submit' and contains(@class, 'btn-primary')]", "action": "click"}
]
    # Run sample flow with visible browser for local debugging
    print(asyncio.run(run_test_flow(url='https://acme-test.uipath.com/login', steps=sample_steps, headless=False)))