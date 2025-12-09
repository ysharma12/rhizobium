"""
HTML to PDF Converter
Converts the HTML visualization report to PDF format.
"""

import sys
from pathlib import Path

def convert_html_to_pdf(html_path: str, pdf_path: str = None) -> str:
    """Convert HTML file to PDF using available library."""
    html_file = Path(html_path)
    
    if not html_file.exists():
        print(f"❌ HTML file not found: {html_path}")
        return None
    
    if pdf_path is None:
        pdf_path = html_file.with_suffix('.pdf')
    
    # Try weasyprint first (most reliable)
    try:
        from weasyprint import HTML
        print(f"📄 Converting HTML to PDF using weasyprint...")
        HTML(filename=str(html_file), encoding='utf-8').write_pdf(pdf_path)
        print(f"✓ PDF created: {pdf_path}")
        return str(pdf_path)
    except ImportError:
        pass
    
    # Try pdfkit (requires wkhtmltopdf installed)
    try:
        import pdfkit
        print(f"📄 Converting HTML to PDF using pdfkit...")
        options = {'encoding': 'UTF-8'}
        pdfkit.from_file(str(html_file), str(pdf_path), options=options)
        print(f"✓ PDF created: {pdf_path}")
        return str(pdf_path)
    except (ImportError, OSError):
        pass
    
    # Try pyppeteer (headless Chrome)
    try:
        import asyncio
        from pyppeteer import launch
        
        async def convert():
            print(f"📄 Converting HTML to PDF using pyppeteer...")
            browser = await launch()
            page = await browser.newPage()
            await page.goto(f'file://{html_file.absolute()}', {'waitUntil': 'networkidle0'})
            await page.pdf({'path': str(pdf_path), 'format': 'A4', 'printBackground': True})
            await browser.close()
        
        asyncio.get_event_loop().run_until_complete(convert())
        print(f"✓ PDF created: {pdf_path}")
        return str(pdf_path)
    except ImportError:
        pass
    
    print("\n❌ No PDF conversion library found!")
    print("\nPlease install one of the following:")
    print("  1. weasyprint (recommended):")
    print("     pip install weasyprint")
    print("\n  2. pdfkit (requires wkhtmltopdf):")
    print("     pip install pdfkit")
    print("     sudo apt-get install wkhtmltopdf")
    print("\n  3. pyppeteer:")
    print("     pip install pyppeteer")
    print()
    return None


def main():
    """Main function."""
    if len(sys.argv) < 2:
        html_path = "visualizations/visualizations_report.html"
    else:
        html_path = sys.argv[1]
    
    if len(sys.argv) >= 3:
        pdf_path = sys.argv[2]
    else:
        pdf_path = None
    
    convert_html_to_pdf(html_path, pdf_path)


if __name__ == "__main__":
    main()

