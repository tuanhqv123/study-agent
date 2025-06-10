#!/usr/bin/env python3
"""
Script để test và so sánh output giữa Brave Search và Google Custom Search API
"""

import asyncio
import json
import httpx
from datetime import datetime

class SearchComparison:
    def __init__(self):
        # Brave Search credentials
        self.BRAVE_API_KEY = "BSAZNoNkz9pcKr2p29Vgu42om-CCbLb"
        self.BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"
        
        # Google Custom Search credentials (cần thay đổi)
        self.GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
        self.GOOGLE_SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE_ID"
        self.GOOGLE_API_URL = "https://www.googleapis.com/customsearch/v1"

    async def search_brave(self, query):
        """Test Brave Search API"""
        try:
            params = {"q": query, "count": 5, "search_lang": "vi"}
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.BRAVE_API_KEY
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.BRAVE_API_URL,
                    params=params,
                    headers=headers
                )
                
                if response.status_code != 200:
                    return {"error": f"Brave API error: {response.status_code}"}
                
                result = response.json()
                
                # Format results
                formatted_results = []
                web_results = result.get('web', {}).get('results', [])
                
                for item in web_results[:5]:
                    formatted_results.append({
                        'title': item.get('title', 'Untitled'),
                        'url': item.get('url', '#'),
                        'snippet': item.get('description', '')
                    })
                
                return {
                    "source": "Brave Search",
                    "query": query,
                    "total_results": len(formatted_results),
                    "results": formatted_results,
                    "raw_structure": {
                        "top_level_keys": list(result.keys()),
                        "web_keys": list(result.get('web', {}).keys()) if 'web' in result else None
                    }
                }
                
        except Exception as e:
            return {"error": f"Brave Search error: {str(e)}"}

    async def search_google(self, query):
        """Test Google Custom Search API"""
        try:
            params = {
                "key": self.GOOGLE_API_KEY,
                "cx": self.GOOGLE_SEARCH_ENGINE_ID,
                "q": query,
                "num": 5,
                "lr": "lang_vi",
                "safe": "medium"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.GOOGLE_API_URL,
                    params=params
                )
                
                if response.status_code != 200:
                    return {"error": f"Google API error: {response.status_code}"}
                
                result = response.json()
                
                # Check for API errors
                if 'error' in result:
                    return {"error": f"Google API error: {result['error'].get('message', 'Unknown error')}"}
                
                # Format results
                formatted_results = []
                items = result.get('items', [])
                
                for item in items[:5]:
                    formatted_results.append({
                        'title': item.get('title', 'Untitled'),
                        'url': item.get('link', '#'),
                        'snippet': item.get('snippet', '')
                    })
                
                return {
                    "source": "Google Custom Search",
                    "query": query,
                    "total_results": len(formatted_results),
                    "results": formatted_results,
                    "raw_structure": {
                        "top_level_keys": list(result.keys()),
                        "search_info": result.get('searchInformation', {})
                    }
                }
                
        except Exception as e:
            return {"error": f"Google Search error: {str(e)}"}

    async def compare_searches(self, query):
        """So sánh kết quả từ cả 2 API"""
        print(f"\n{'='*60}")
        print(f"COMPARING SEARCH RESULTS FOR: '{query}'")
        print(f"{'='*60}")
        
        # Test cả 2 API song song
        brave_task = self.search_brave(query)
        google_task = self.search_google(query)
        
        brave_result, google_result = await asyncio.gather(brave_task, google_task)
        
        # In kết quả Brave
        print(f"\n{'-'*30} BRAVE SEARCH {'-'*30}")
        if "error" in brave_result:
            print(f"❌ ERROR: {brave_result['error']}")
        else:
            print(f"✅ SUCCESS: Found {brave_result['total_results']} results")
            print(f"Raw structure: {brave_result['raw_structure']}")
            print("\nResults:")
            for i, result in enumerate(brave_result['results'], 1):
                print(f"{i}. {result['title'][:60]}...")
                print(f"   URL: {result['url']}")
                print(f"   Snippet: {result['snippet'][:100]}...")
                print()
        
        # In kết quả Google
        print(f"\n{'-'*30} GOOGLE SEARCH {'-'*30}")
        if "error" in google_result:
            print(f"❌ ERROR: {google_result['error']}")
        else:
            print(f"✅ SUCCESS: Found {google_result['total_results']} results")
            print(f"Raw structure: {google_result['raw_structure']}")
            print("\nResults:")
            for i, result in enumerate(google_result['results'], 1):
                print(f"{i}. {result['title'][:60]}...")
                print(f"   URL: {result['url']}")
                print(f"   Snippet: {result['snippet'][:100]}...")
                print()
        
        # So sánh
        print(f"\n{'-'*30} COMPARISON {'-'*30}")
        if "error" not in brave_result and "error" not in google_result:
            print(f"Brave results: {brave_result['total_results']}")
            print(f"Google results: {google_result['total_results']}")
            print("\nTitle comparison (first 3 results):")
            for i in range(min(3, len(brave_result['results']), len(google_result['results']))):
                print(f"{i+1}. Brave: {brave_result['results'][i]['title'][:50]}...")
                print(f"   Google: {google_result['results'][i]['title'][:50]}...")
                print()

async def main():
    """Test script chính"""
    if __name__ == "__main__":
        print("🔍 SEARCH API COMPARISON TOOL")
        print("="*60)
        
        comparison = SearchComparison()
        
        # Kiểm tra credentials
        print("📋 Checking credentials...")
        if comparison.GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY":
            print("⚠️  WARNING: Google API credentials chưa được cấu hình!")
            print("   Vui lòng cập nhật GOOGLE_API_KEY và GOOGLE_SEARCH_ENGINE_ID")
            print("   Xem hướng dẫn trong file GOOGLE_SEARCH_SETUP.md")
            print("\n   Chỉ test Brave Search...")
            
            # Test chỉ Brave
            test_queries = ["python programming", "machine learning", "web development"]
            for query in test_queries:
                print(f"\n🔍 Testing Brave Search: '{query}'")
                result = await comparison.search_brave(query)
                if "error" in result:
                    print(f"❌ ERROR: {result['error']}")
                else:
                    print(f"✅ SUCCESS: Found {result['total_results']} results")
                    for i, res in enumerate(result['results'][:2], 1):
                        print(f"{i}. {res['title'][:60]}...")
        else:
            print("✅ Credentials configured. Testing both APIs...")
            
            # Test cả 2 API
            test_queries = ["python programming", "artificial intelligence"]
            for query in test_queries:
                await comparison.compare_searches(query)

if __name__ == "__main__":
    asyncio.run(main()) 