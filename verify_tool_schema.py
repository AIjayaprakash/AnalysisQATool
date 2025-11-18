"""Verify playwright_get_page_metadata tool schema"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from llmops.tools.playwright_tools import playwright_get_page_metadata

print("=" * 80)
print("playwright_get_page_metadata Tool Schema")
print("=" * 80)

# Get tool schema
schema = playwright_get_page_metadata.get_input_schema()
schema_dict = schema.schema()

print("\nTool Name:", playwright_get_page_metadata.name)
print("\nDescription:", playwright_get_page_metadata.description)

print("\nInput Schema:")
print(f"  Type: {schema_dict.get('type')}")
print(f"  Properties: {list(schema_dict.get('properties', {}).keys())}")

if 'selector' in schema_dict.get('properties', {}):
    selector_schema = schema_dict['properties']['selector']
    print("\nSelector Parameter:")
    print(f"  Type: {selector_schema.get('type')}")
    print(f"  anyOf: {selector_schema.get('anyOf', 'N/A')}")
    print(f"  Default: {selector_schema.get('default', 'N/A')}")
    print(f"  Required: {'selector' in schema_dict.get('required', [])}")

print("\n" + "=" * 80)

# Check if None is acceptable
if 'selector' in schema_dict.get('properties', {}):
    selector_types = schema_dict['properties']['selector'].get('anyOf', [])
    accepts_null = any(t.get('type') == 'null' for t in selector_types)
    
    if accepts_null:
        print("✅ Tool correctly accepts None for selector parameter")
    else:
        print("⚠️  Tool may not accept None - check anyOf field")
        
    print("=" * 80)
