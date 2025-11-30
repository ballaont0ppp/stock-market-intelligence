"""
Run all accessibility tests and generate comprehensive report
"""
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import config


def run_tests():
    """Run all accessibility tests using pytest"""
    print("=" * 80)
    print("ACCESSIBILITY TESTING SUITE")
    print("=" * 80)
    print(f"Target Application: {config.APP_URL}")
    print(f"WCAG Level: {config.WCAG_LEVEL}")
    print(f"WCAG Version: {config.WCAG_VERSION}")
    print(f"Browser: {config.BROWSER}")
    print("=" * 80)
    print()
    
    # Prepare pytest arguments
    pytest_args = [
        'pytest',
        '-v',
        '--tb=short',
        f'--html={config.REPORTS_DIR}/accessibility_report.html',
        '--self-contained-html',
        '--color=yes'
    ]
    
    # Run tests
    print("Running accessibility tests...")
    print()
    
    result = subprocess.run(pytest_args, cwd=Path(__file__).parent)
    
    print()
    print("=" * 80)
    
    if result.returncode == 0:
        print("✓ All accessibility tests passed!")
    else:
        print("✗ Some accessibility tests failed. Check the report for details.")
    
    print(f"Report generated: {config.REPORTS_DIR}/accessibility_report.html")
    print("=" * 80)
    
    return result.returncode


def generate_summary_report():
    """Generate a summary report from all test results"""
    print("\nGenerating summary report...")
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'config': {
            'app_url': config.APP_URL,
            'wcag_level': config.WCAG_LEVEL,
            'wcag_version': config.WCAG_VERSION,
            'browser': config.BROWSER
        },
        'results': {}
    }
    
    # Collect all result files
    result_files = list(config.RESULTS_DIR.glob('*.json'))
    
    for result_file in result_files:
        try:
            with open(result_file, 'r') as f:
                data = json.load(f)
                test_name = result_file.stem
                summary['results'][test_name] = data
        except Exception as e:
            print(f"Warning: Could not read {result_file}: {e}")
    
    # Save summary
    summary_path = config.REPORTS_DIR / 'accessibility_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary report saved: {summary_path}")
    
    # Generate human-readable summary
    generate_readable_summary(summary)


def generate_readable_summary(summary):
    """Generate a human-readable summary report"""
    report_path = config.REPORTS_DIR / 'ACCESSIBILITY_SUMMARY.md'
    
    with open(report_path, 'w') as f:
        f.write("# Accessibility Testing Summary\n\n")
        f.write(f"**Date:** {summary['timestamp']}\n\n")
        f.write(f"**Application:** {summary['config']['app_url']}\n\n")
        f.write(f"**WCAG Compliance Target:** Level {summary['config']['wcag_level']} ({summary['config']['wcag_version']})\n\n")
        f.write(f"**Browser:** {summary['config']['browser']}\n\n")
        f.write("---\n\n")
        
        f.write("## Test Results Overview\n\n")
        
        # Visual Accessibility
        f.write("### Visual Accessibility\n\n")
        if 'color_contrast_results' in summary['results']:
            contrast_data = summary['results']['color_contrast_results']
            total_pages = len([k for k in contrast_data.keys() if k != 'timestamp'])
            pages_with_violations = sum(1 for k, v in contrast_data.items() 
                                       if isinstance(v, dict) and v.get('violations', 0) > 0)
            f.write(f"- **Color Contrast:** {total_pages - pages_with_violations}/{total_pages} pages passed\n")
        
        if 'image_alt_text_results' in summary['results']:
            alt_data = summary['results']['image_alt_text_results']
            total_images = sum(v.get('total_images', 0) for v in alt_data.values() if isinstance(v, dict))
            missing_alt = sum(len(v.get('missing_alt', [])) for v in alt_data.values() if isinstance(v, dict))
            f.write(f"- **Image Alt Text:** {total_images - missing_alt}/{total_images} images have alt text\n")
        
        f.write("\n")
        
        # Motor Accessibility
        f.write("### Motor Accessibility\n\n")
        if 'keyboard_navigation_results' in summary['results']:
            kbd_data = summary['results']['keyboard_navigation_results']
            accessible_pages = sum(1 for v in kbd_data.values() 
                                  if isinstance(v, dict) and v.get('keyboard_accessible', False))
            total_pages = len([k for k in kbd_data.keys() if isinstance(kbd_data[k], dict)])
            f.write(f"- **Keyboard Navigation:** {accessible_pages}/{total_pages} pages fully keyboard accessible\n")
        
        if 'click_target_sizes_results' in summary['results']:
            target_data = summary['results']['click_target_sizes_results']
            avg_compliance = sum(v.get('compliance_rate', 0) for v in target_data.values() 
                               if isinstance(v, dict)) / max(len([k for k in target_data.keys() 
                               if isinstance(target_data[k], dict)]), 1)
            f.write(f"- **Touch Target Sizes:** {avg_compliance:.1f}% average compliance\n")
        
        f.write("\n")
        
        # Cognitive Accessibility
        f.write("### Cognitive Accessibility\n\n")
        if 'navigation_clarity_results' in summary['results']:
            nav_data = summary['results']['navigation_clarity_results']
            pages_with_titles = sum(1 for v in nav_data.values() 
                                   if isinstance(v, dict) and v.get('has_clear_title', False))
            total_pages = len([k for k in nav_data.keys() if isinstance(nav_data[k], dict) and k != 'navigation_consistency'])
            f.write(f"- **Navigation Clarity:** {pages_with_titles}/{total_pages} pages have clear titles\n")
        
        if 'consistent_layout_results' in summary['results']:
            layout_data = summary['results']['consistent_layout_results']
            proper_headings = sum(1 for v in layout_data.values() 
                                 if isinstance(v, dict) and v.get('proper_heading_order', False))
            total_pages = len([k for k in layout_data.keys() if isinstance(layout_data[k], dict) and k != 'layout_consistency'])
            f.write(f"- **Consistent Layout:** {proper_headings}/{total_pages} pages have proper heading hierarchy\n")
        
        f.write("\n")
        
        f.write("## Recommendations\n\n")
        f.write("1. Review detailed test results in `accessibility_report.html`\n")
        f.write("2. Address any critical violations found in color contrast tests\n")
        f.write("3. Ensure all images have appropriate alt text\n")
        f.write("4. Verify keyboard navigation works for all interactive elements\n")
        f.write("5. Maintain consistent navigation and layout across all pages\n")
        f.write("\n")
        
        f.write("## Next Steps\n\n")
        f.write("- [ ] Fix identified accessibility issues\n")
        f.write("- [ ] Add ARIA labels where needed\n")
        f.write("- [ ] Improve semantic HTML structure\n")
        f.write("- [ ] Enhance keyboard navigation\n")
        f.write("- [ ] Document accessibility features\n")
        f.write("- [ ] Conduct user testing with assistive technologies\n")
    
    print(f"Readable summary saved: {report_path}")


if __name__ == '__main__':
    exit_code = run_tests()
    generate_summary_report()
    sys.exit(exit_code)
