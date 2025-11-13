# 🎯 playwright_get_page_metadata - Quick Reference

## Function Signature
```python
@tool
async def playwright_get_page_metadata(selector: str = None) -> str
```

## Usage Examples

### Get Page Info Only
```python
await playwright_get_page_metadata.ainvoke({"selector": None})
```

### Get Element Metadata
```python
# CSS Selector
await playwright_get_page_metadata.ainvoke({"selector": "button#submit"})

# XPath
await playwright_get_page_metadata.ainvoke({"selector": "//button[@id='submit']"})

# Text Content
await playwright_get_page_metadata.ainvoke({"selector": "text=Submit"})
```

## Metadata Collected

### Page Level (Always)
- URL, Title

### Element Level (30+ Attributes)
| Category | Attributes |
|----------|-----------|
| **Basic** | tag, id, type, name, className, text, value |
| **Links** | href, src, alt |
| **Forms** | inputType, placeholder, maxLength, pattern, min, max, step, autocomplete |
| **A11y** | ariaLabel, role, title |
| **State** | disabled, checked, selected, readonly, required, hidden, isVisible |
| **Layout** | boundingBox (x, y, width, height), tabIndex |
| **Advanced** | dataset, innerHTML, outerHTML |

## Sample Output

```
📄 Page Metadata:
  • URL: https://example.com/form
  • Title: Contact Form

🎯 Element Metadata (Found 1 element(s)):
  • Selector: input[type='email']
  • Tag: <input>
  • ID: email-field
  • Type: email
  • Name: user_email
  • Class: form-control
  • Placeholder: Enter your email
  • Input Type: email
  • Max Length: 100
  • Required: True
  • Visible: True
  • Position: (x=80.0, y=200.0)
  • Size: 300.0x35.0px
  • Tab Index: 0
```

## Tool Count
**10 Tools** (playwright_get_page_metadata is #5)

## Files Changed
1. `backend/app/llmops/tools/playwright_tools.py` - Added function
2. `backend/app/llmops/tools/__init__.py` - Updated exports

## Verification
```bash
python verify_metadata_direct.py  # ✅ All tests passed
```
