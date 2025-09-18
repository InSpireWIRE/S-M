import asyncio
from playwright.async_api import async_playwright
import re
import time

class AdvancedURLScraper:
    def __init__(self):
        self.max_pages = 50  # Limit to prevent infinite loops
        
    async def scrape_adobe_indesign(self, url: str) -> str:
        """Scrape multi-page Adobe InDesign documents"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            page = await browser.new_page()
            await page.add_init_script("delete Object.getPrototypeOf(navigator).webdriver")
            
            # Increase timeout and use less strict wait condition
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_timeout(5000)  # Give extra time for JavaScript
            except Exception as e:
                print(f"Initial load error: {e}")
                # Try simpler approach
                await page.goto(url, timeout=60000)
                await page.wait_for_timeout(3000)
            
            all_text = []
            pages_scraped = 0
            
            # Look for navigation elements
            next_button_selectors = [
                'button[aria-label*="next"]',
                'button[aria-label*="Next"]',
                '.next-page',
                '[class*="next"]',
                '[class*="arrow-right"]'
            ]
            
            while pages_scraped < self.max_pages:
                # Extract text from current page
                try:
                    # Wait for any text to appear
                    await page.wait_for_selector('body', timeout=5000)
                    
                    text_content = await page.evaluate('''() => {
                        const elements = document.querySelectorAll('p, div, span, h1, h2, h3, h4, h5, h6');
                        const texts = [];
                        elements.forEach(el => {
                            const text = el.innerText || el.textContent;
                            if (text && text.trim().length > 0) {
                                texts.push(text.trim());
                            }
                        });
                        return texts.join(' ');
                    }''')
                    
                    if text_content:
                        all_text.append(text_content)
                    pages_scraped += 1
                    
                    # If we got no text on first page, might be loading issue
                    if pages_scraped == 1 and not text_content:
                        print("No text found on first page, waiting longer...")
                        await page.wait_for_timeout(5000)
                        # Try again
                        text_content = await page.evaluate('() => document.body.innerText')
                        if text_content:
                            all_text.append(text_content)
                    
                except Exception as e:
                    print(f"Could not extract text from page {pages_scraped + 1}: {e}")
                    break
                
                # Try to find and click next button
                clicked = False
                for selector in next_button_selectors:
                    try:
                        next_btn = await page.query_selector(selector)
                        if next_btn:
                            is_disabled = await next_btn.get_attribute('disabled')
                            if not is_disabled:
                                await next_btn.click()
                                await page.wait_for_timeout(2000)
                                clicked = True
                                break
                    except:
                        continue
                
                if not clicked:
                    # Try keyboard navigation
                    try:
                        await page.keyboard.press('ArrowRight')
                        await page.wait_for_timeout(1000)
                        
                        # Check if content changed
                        new_content = await page.evaluate('() => document.body.innerText')
                        if new_content in all_text:
                            break  # No new content, we're done
                    except:
                        break
            
            await browser.close()
            return ' '.join(all_text)
    
    async def scrape_generic_presentation(self, url: str) -> str:
        """Generic scraper for unknown presentation types"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            page = await browser.new_page()
            await page.add_init_script("delete Object.getPrototypeOf(navigator).webdriver")
            
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_timeout(10000)  # Wait 10 seconds for Canva content to load
            
            all_text = []
            
            # Try to detect tabs or sections
            tabs = await page.query_selector_all('[role="tab"], .tab, [class*="tab-"]')
            
            if tabs and len(tabs) > 1:
                # Handle tab-based navigation
                for i, tab in enumerate(tabs):
                    try:
                        await tab.click()
                        await page.wait_for_timeout(1000)
                        
                        content = await page.evaluate('() => document.body.innerText')
                        all_text.append(f"=== Section {i+1} ===\n{content}")
                    except:
                        continue
            else:
                # Try sequential page navigation
                for i in range(self.max_pages):
                    content = await page.evaluate('() => document.body.innerText')
                    all_text.append(content)
                    
                    # Try to navigate to next page
                    await page.keyboard.press('ArrowRight')
                    await page.wait_for_timeout(1000)
                    
                    # Check if content changed
                    new_content = await page.evaluate('() => document.body.innerText')
                    if new_content == content:
                        break  # No change, we're done
            
            await browser.close()
            return ' '.join(all_text)