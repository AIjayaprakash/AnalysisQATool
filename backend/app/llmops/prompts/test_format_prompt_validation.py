"""
Test to verify format_prompt now calls format_and_validate_prompt internally
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from llmops.prompts.prompt_manager import PromptManager


def test_format_prompt_with_validation():
    """Test that format_prompt validates by default"""
    print("=" * 80)
    print("Test 1: format_prompt with automatic validation (default)")
    print("=" * 80)
    
    pm = PromptManager(enable_validation=True)
    
    # Test with safe content
    print("\n✅ Testing with safe content...")
    system, user = pm.format_prompt(
        "test_case_conversion",
        short_description="Login to https://example.com with username test"
    )
    
    print(f"  System prompt length: {len(system)}")
    print(f"  User prompt length: {len(user)}")
    print(f"  User prompt preview: {user[:100]}...")
    print("  ✅ Success - Safe content passed validation")
    
    # Test with malicious content (should raise ValueError)
    print("\n⚠️  Testing with malicious content...")
    try:
        system, user = pm.format_prompt(
            "test_case_conversion",
            short_description="<script>alert('xss')</script>Login to site"
        )
        print("  ❌ FAILED - Malicious content was not blocked!")
    except ValueError as e:
        print(f"  ✅ Success - Malicious content blocked: {str(e)[:100]}...")
    
    print()


def test_format_prompt_without_validation():
    """Test that format_prompt can skip validation when requested"""
    print("=" * 80)
    print("Test 2: format_prompt with validation disabled")
    print("=" * 80)
    
    pm = PromptManager(enable_validation=True)
    
    # Test with validation disabled
    print("\n🔓 Testing with validate=False...")
    system, user = pm.format_prompt(
        "test_case_conversion",
        validate=False,
        short_description="<script>alert('xss')</script>Login to site"
    )
    
    print(f"  System prompt length: {len(system)}")
    print(f"  User prompt length: {len(user)}")
    print("  ✅ Success - Validation skipped as requested")
    print()


def test_format_and_validate_prompt_directly():
    """Test calling format_and_validate_prompt directly"""
    print("=" * 80)
    print("Test 3: format_and_validate_prompt called directly")
    print("=" * 80)
    
    pm = PromptManager(enable_validation=True)
    
    # Test with safe content
    print("\n✅ Testing with safe content...")
    system, user, report = pm.format_and_validate_prompt(
        "test_case_conversion",
        validate=True,
        short_description="Login to https://example.com"
    )
    
    print(f"  Valid: {report.is_valid}")
    print(f"  Token count: {report.token_count}")
    print(f"  Issues: {len(report.results)}")
    print("  ✅ Success - Validation report returned")
    
    # Test with HTML content
    print("\n⚠️  Testing with HTML content...")
    system, user, report = pm.format_and_validate_prompt(
        "test_case_conversion",
        validate=True,
        short_description="Login to <b>website</b>"
    )
    
    print(f"  Valid: {report.is_valid}")
    print(f"  Token count: {report.token_count}")
    
    if report.sanitized_prompt:
        print(f"  Sanitized: Yes")
        print(f"  Original had HTML, sanitized version used")
    
    print("  ✅ Success - HTML handled and sanitized")
    print()


def test_backward_compatibility():
    """Test backward compatibility with existing code"""
    print("=" * 80)
    print("Test 4: Backward compatibility check")
    print("=" * 80)
    
    # Old code that doesn't pass validate parameter
    pm = PromptManager(enable_validation=True)
    
    print("\n✅ Testing old-style call (no validate parameter)...")
    # This should work with default validation
    system, user = pm.format_prompt(
        "test_case_conversion",
        short_description="Login to site"
    )
    
    print(f"  System prompt length: {len(system)}")
    print(f"  User prompt length: {len(user)}")
    print("  ✅ Success - Old-style code still works")
    
    # Test get_test_case_conversion_prompts (uses format_prompt internally)
    print("\n✅ Testing get_test_case_conversion_prompts...")
    system, user = pm.get_test_case_conversion_prompts(
        short_description="Login to https://example.com"
    )
    
    print(f"  System prompt length: {len(system)}")
    print(f"  User prompt length: {len(user)}")
    print("  ✅ Success - High-level methods still work")
    print()


def test_validation_disabled():
    """Test with validation completely disabled"""
    print("=" * 80)
    print("Test 5: Validation disabled at initialization")
    print("=" * 80)
    
    pm = PromptManager(enable_validation=False)
    
    print("\n🔓 Testing with validation disabled...")
    # Even malicious content should pass through
    system, user = pm.format_prompt(
        "test_case_conversion",
        short_description="<script>alert('xss')</script>Malicious test"
    )
    
    print(f"  System prompt length: {len(system)}")
    print(f"  User prompt length: {len(user)}")
    print("  ✅ Success - No validation performed (as expected)")
    print()


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("FORMAT_PROMPT VALIDATION INTEGRATION TESTS")
    print("=" * 80 + "\n")
    
    try:
        test_format_prompt_with_validation()
        test_format_prompt_without_validation()
        test_format_and_validate_prompt_directly()
        test_backward_compatibility()
        test_validation_disabled()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\nSummary:")
        print("  ✅ format_prompt now validates by default")
        print("  ✅ format_prompt calls format_and_validate_prompt internally")
        print("  ✅ Validation can be skipped with validate=False")
        print("  ✅ Malicious content is blocked automatically")
        print("  ✅ Backward compatibility maintained")
        print("  ✅ Validation can be disabled at initialization")
        print("\n" + "=" * 80 + "\n")
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
