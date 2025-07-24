#!/usr/bin/env python3
"""
Example: Discourse Analysis using MCP Integration

This script demonstrates how to use the MCP orchestrator to perform
comprehensive discourse analysis across multiple sources.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.integrations.mcp import MCPOrchestrator
from src.integrations.mcp.orchestrator import SearchScope, DiscourseAnalysisResult


# Configuration
MCP_CONFIG = {
    # Enable all sources for comprehensive analysis
    'enable_semantic_scholar': True,
    'enable_arxiv_latex': True,
    'enable_youtube': True,
    'enable_google_news': True,
    'enable_dappier': True,
    'enable_content_core': True,
    
    # API Keys (replace with your actual keys or use environment variables)
    'semantic_scholar_api_key': None,  # Optional
    'openai_api_key': None,  # For YouTube Whisper
    'serp_api_key': None,  # Required for Google News
    'dappier_api_key': None,  # Required for DappierAI
    
    # Use default ports
    'semantic_scholar_url': 'http://localhost:8000',
    'arxiv_latex_url': 'http://localhost:8001',
    'youtube_url': 'http://localhost:8002',
    'google_news_url': 'http://localhost:8003',
    'dappier_url': 'http://localhost:8004',
    'content_core_url': 'http://localhost:8005'
}


async def example_unified_search():
    """Example: Unified search across all sources"""
    print("\n=== Unified Search Example ===")
    
    orchestrator = MCPOrchestrator(MCP_CONFIG)
    
    # Search across all sources
    query = "artificial intelligence ethics"
    print(f"\nSearching for: '{query}'")
    
    results = await orchestrator.unified_search(
        query=query,
        scope=SearchScope.ALL,
        limit_per_source=5
    )
    
    # Group results by source
    by_source = {}
    for result in results:
        by_source.setdefault(result.source, []).append(result)
    
    # Display results
    for source, source_results in by_source.items():
        print(f"\n{source.upper()} ({len(source_results)} results):")
        for i, result in enumerate(source_results[:3], 1):
            print(f"  {i}. {result.title}")
            print(f"     Score: {result.relevance_score:.2f}")
            print(f"     URL: {result.url}")
    
    return results


async def example_discourse_analysis():
    """Example: Comprehensive discourse analysis"""
    print("\n=== Discourse Analysis Example ===")
    
    orchestrator = MCPOrchestrator(MCP_CONFIG)
    
    topic = "climate change"
    print(f"\nAnalyzing discourse on: '{topic}'")
    
    # Perform analysis
    analysis = await orchestrator.analyze_discourse(
        topic=topic,
        time_range_days=30,
        include_sentiment=True
    )
    
    # Display results
    print(f"\nTime Range: {analysis.time_range['start'].date()} to {analysis.time_range['end'].date()}")
    print(f"Academic Papers: {len(analysis.academic_papers)}")
    print(f"News Articles: {len(analysis.news_articles)}")
    print(f"Media Content: {len(analysis.media_content)}")
    print(f"Trending Score: {analysis.trending_score:.2f}")
    
    # Top entities
    print("\nTop Entities:")
    for entity in analysis.key_entities[:5]:
        print(f"  - {entity['name']} ({entity['type']}): {entity['count']} mentions")
    
    # Sentiment
    if analysis.sentiment_analysis:
        print("\nSentiment Analysis:")
        for key, value in analysis.sentiment_analysis.items():
            print(f"  - {key}: {value:.2f}")
    
    # Cross-references
    if analysis.cross_references:
        print(f"\nCross-References Found: {len(analysis.cross_references)}")
        for ref in analysis.cross_references[:3]:
            print(f"  - {ref['type']}: {ref.get('confidence', 0):.2f} confidence")
    
    return analysis


async def example_mathematical_content():
    """Example: Extract mathematical content from ArXiv"""
    print("\n=== Mathematical Content Extraction Example ===")
    
    orchestrator = MCPOrchestrator(MCP_CONFIG)
    
    # Example ArXiv ID (replace with actual paper ID)
    arxiv_id = "2301.00001"
    print(f"\nExtracting mathematical content from: {arxiv_id}")
    
    try:
        content = await orchestrator.extract_mathematical_content(arxiv_id)
        
        if 'error' not in content:
            # LaTeX content
            latex = content['latex_content']
            print(f"\nTitle: {latex.title}")
            print(f"Sections: {len(latex.sections)}")
            
            # Equations
            equations = content['equations']
            print(f"\nEquations Found: {len(equations)}")
            for i, eq in enumerate(equations[:3], 1):
                print(f"  {i}. {eq.latex_code}")
                if eq.context:
                    print(f"     Context: {eq.context[:100]}...")
            
            # Theorems
            theorems = content['theorems']
            print(f"\nTheorems/Lemmas Found: {len(theorems)}")
        else:
            print(f"Error: {content['error']}")
            
    except Exception as e:
        print(f"Error extracting content: {e}")


async def example_video_analysis():
    """Example: Transcribe and analyze YouTube video"""
    print("\n=== Video Analysis Example ===")
    
    orchestrator = MCPOrchestrator(MCP_CONFIG)
    
    # Example YouTube URL (replace with actual video)
    video_url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"\nAnalyzing video: {video_url}")
    
    try:
        analysis = await orchestrator.transcribe_and_analyze_video(
            video_url=video_url,
            extract_topics=True
        )
        
        if 'error' not in analysis:
            video = analysis['video']
            print(f"\nTitle: {video.title}")
            print(f"Duration: {video.duration} seconds")
            print(f"Language: {video.language}")
            print(f"Total Words: {video.total_words}")
            
            # Sample transcript
            print("\nTranscript Sample:")
            for chunk in video.transcript_chunks[:3]:
                print(f"  [{chunk.start_time:.1f}s] {chunk.text[:100]}...")
            
            # Summary
            if analysis.get('summary'):
                print(f"\nSummary: {analysis['summary'].get('summary', 'N/A')}")
            
            # Topics
            if analysis.get('topic_timestamps'):
                print("\nTopic Timestamps:")
                for topic in analysis['topic_timestamps'][:5]:
                    print(f"  - {topic['topic']} at {topic['timestamp']}")
        else:
            print(f"Error: {analysis['error']}")
            
    except Exception as e:
        print(f"Error analyzing video: {e}")


async def example_comprehensive_news():
    """Example: Get comprehensive news coverage"""
    print("\n=== Comprehensive News Coverage Example ===")
    
    orchestrator = MCPOrchestrator(MCP_CONFIG)
    
    topic = "artificial intelligence regulation"
    print(f"\nGetting news coverage for: '{topic}'")
    
    coverage = await orchestrator.get_comprehensive_news_coverage(
        topic=topic,
        include_financial=True
    )
    
    # Google News
    if 'google_news' in coverage:
        gn = coverage['google_news']
        print("\nGoogle News:")
        print(f"  Headlines: {len(gn.get('headlines', []))}")
        print(f"  Topic News: {len(gn.get('topic_news', []))}")
        print(f"  Trending: {len(gn.get('trending', []))}")
        
        # Sample headlines
        for article in gn.get('headlines', [])[:3]:
            print(f"    - {article.title}")
    
    # DappierAI
    if 'dappier' in coverage:
        dappier = coverage['dappier']
        print("\nDappier Multi-Domain:")
        print(f"  Content Items: {len(dappier.get('content', []))}")
        print(f"  Trending Topics: {len(dappier.get('trending', []))}")
        
        # Sample content
        for content in dappier.get('content', [])[:3]:
            print(f"    - {content.title} ({content.domain.value})")
        
        # Financial data if available
        if 'financial' in dappier:
            print(f"\n  Financial Data: {len(dappier['financial'])} symbols")


async def example_cross_source_correlation():
    """Example: Find correlations across different sources"""
    print("\n=== Cross-Source Correlation Example ===")
    
    orchestrator = MCPOrchestrator(MCP_CONFIG)
    
    # First, search for a specific topic
    topic = "GPT-4"
    print(f"\nSearching for correlations on: '{topic}'")
    
    # Get data from multiple sources
    results = await orchestrator.unified_search(
        query=topic,
        scope=SearchScope.ALL,
        limit_per_source=10
    )
    
    # Analyze by source type
    academic_results = [r for r in results if r.source == "semantic_scholar"]
    news_results = [r for r in results if r.source in ["google_news", "dappier"]]
    
    print(f"\nFound {len(academic_results)} academic papers")
    print(f"Found {len(news_results)} news articles")
    
    # Look for temporal patterns
    if academic_results and news_results:
        # Find if news coverage follows paper publications
        for paper in academic_results[:3]:
            if paper.published_date:
                print(f"\nPaper: {paper.title}")
                print(f"Published: {paper.published_date.date()}")
                
                # Find news after paper publication
                related_news = [
                    n for n in news_results
                    if n.published_date and n.published_date > paper.published_date
                ]
                
                if related_news:
                    print(f"Related news coverage ({len(related_news)} articles):")
                    for news in related_news[:2]:
                        days_after = (news.published_date - paper.published_date).days
                        print(f"  - {news.title} ({days_after} days later)")


def save_results(results: Dict[str, Any], filename: str):
    """Save analysis results to JSON file"""
    # Convert datetime objects to strings
    def serialize(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=serialize)
    
    print(f"\nResults saved to: {filename}")


async def main():
    """Run all examples"""
    print("MCP Discourse Analysis Examples")
    print("=" * 50)
    
    # Note: Some examples may fail if MCP servers are not running
    # or API keys are not configured
    
    try:
        # 1. Unified Search
        search_results = await example_unified_search()
        
        # 2. Discourse Analysis
        discourse_analysis = await example_discourse_analysis()
        
        # 3. Mathematical Content (requires ArXiv LaTeX MCP)
        await example_mathematical_content()
        
        # 4. Video Analysis (requires YouTube MCP)
        await example_video_analysis()
        
        # 5. News Coverage
        await example_comprehensive_news()
        
        # 6. Cross-source Correlation
        await example_cross_source_correlation()
        
        # Save some results
        if discourse_analysis:
            save_results(
                {
                    'topic': discourse_analysis.topic,
                    'papers_count': len(discourse_analysis.academic_papers),
                    'news_count': len(discourse_analysis.news_articles),
                    'trending_score': discourse_analysis.trending_score,
                    'key_entities': discourse_analysis.key_entities[:10]
                },
                'discourse_analysis_results.json'
            )
        
    except Exception as e:
        print(f"\nError in examples: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())