"""
MCP Integration Demo

Demonstrates comprehensive discourse analysis using all integrated MCP services.
This example shows how to:
1. Authenticate users
2. Search across academic, news, and video sources
3. Process documents in multiple formats
4. Monitor system health and performance
5. Handle errors gracefully with circuit breakers
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import json

from src.integrations.mcp.orchestrator import MCPOrchestrator, SearchScope
from src.integrations.mcp.semantic_scholar_client import SemanticScholarMCPClient
from src.integrations.mcp.arxiv_latex_client import ArXivLatexMCPClient
from src.integrations.mcp.youtube_client import YouTubeMCPClient
from src.integrations.mcp.google_news_client import GoogleNewsMCPClient
from src.integrations.mcp.dappier_client import DappierMCPClient
from src.integrations.mcp.content_core_client import ContentCoreMCPClient
from src.integrations.mcp.markitdown_client import MarkItDownMCPClient, ConversionOptions
from src.integrations.mcp.pandoc_client import PandocMCPClient, ConversionFormat
from src.integrations.mcp.grafana_client import GrafanaMCPClient, TimeRange, AlertState
from src.integrations.mcp.auth_provider_client import AuthProviderMCPClient, AuthenticationMethod
from src.core.api_rate_limiter import APIRateLimiter
from src.core.circuit_breaker import CircuitBreakerManager


async def main():
    """Run comprehensive MCP integration demo"""
    
    # Initialize infrastructure
    rate_limiter = APIRateLimiter()
    circuit_breaker_manager = CircuitBreakerManager()
    
    # Configure rate limits for each service
    rate_limiter.configure_service("semantic_scholar", requests_per_second=3)
    rate_limiter.configure_service("arxiv_latex", requests_per_second=2)
    rate_limiter.configure_service("youtube", requests_per_second=1)
    rate_limiter.configure_service("google_news", requests_per_second=5)
    rate_limiter.configure_service("dappier", requests_per_second=5)
    
    # Initialize all MCP clients
    print("🚀 Initializing MCP clients...")
    clients = {
        'semantic_scholar': SemanticScholarMCPClient(
            "http://localhost:8001",
            rate_limiter,
            circuit_breaker_manager.get_circuit_breaker("semantic_scholar")
        ),
        'arxiv_latex': ArXivLatexMCPClient(
            "http://localhost:8002",
            rate_limiter,
            circuit_breaker_manager.get_circuit_breaker("arxiv_latex")
        ),
        'youtube': YouTubeMCPClient(
            "http://localhost:8003",
            rate_limiter,
            circuit_breaker_manager.get_circuit_breaker("youtube")
        ),
        'google_news': GoogleNewsMCPClient(
            "http://localhost:8004",
            rate_limiter,
            circuit_breaker_manager.get_circuit_breaker("google_news")
        ),
        'dappier': DappierMCPClient(
            "http://localhost:8005",
            rate_limiter,
            circuit_breaker_manager.get_circuit_breaker("dappier")
        ),
        'content_core': ContentCoreMCPClient(
            "http://localhost:8006",
            rate_limiter,
            circuit_breaker_manager.get_circuit_breaker("content_core")
        ),
        'markitdown': MarkItDownMCPClient(
            "http://localhost:8010",
            rate_limiter,
            circuit_breaker_manager.get_circuit_breaker("markitdown")
        ),
        'pandoc': PandocMCPClient(
            "http://localhost:8011",
            rate_limiter,
            circuit_breaker_manager.get_circuit_breaker("pandoc")
        ),
        'grafana': GrafanaMCPClient(
            "http://localhost:8012",
            rate_limiter,
            circuit_breaker_manager.get_circuit_breaker("grafana")
        ),
        'auth_provider': AuthProviderMCPClient(
            "http://localhost:8013",
            rate_limiter,
            circuit_breaker_manager.get_circuit_breaker("auth_provider")
        )
    }
    
    # Create orchestrator
    orchestrator = MCPOrchestrator(**clients)
    
    # Step 1: Authentication
    print("\n🔐 Step 1: Authenticating user...")
    auth_result = await clients['auth_provider'].authenticate(
        username="demo_user",
        password="demo_password",
        method=AuthenticationMethod.BASIC
    )
    
    if auth_result.success:
        print(f"✅ Authenticated as: {auth_result.data.user.username}")
        print(f"   Roles: {', '.join(auth_result.data.user.roles)}")
        access_token = auth_result.data.access_token
    else:
        print(f"❌ Authentication failed: {auth_result.error}")
        return
    
    # Step 2: Check monitoring permissions
    print("\n🔍 Step 2: Checking permissions...")
    perm_result = await clients['auth_provider'].check_permission(
        user_id=auth_result.data.user.id,
        resource="monitoring",
        action="view"
    )
    
    if perm_result.data.get("allowed"):
        print("✅ User has monitoring access")
    else:
        print("⚠️  User lacks monitoring permissions")
    
    # Step 3: Unified search across sources
    print("\n🔎 Step 3: Searching for 'artificial intelligence ethics'...")
    search_results = await orchestrator.unified_search(
        query="artificial intelligence ethics",
        scope=SearchScope.ALL
    )
    
    print(f"📊 Found {len(search_results)} results across all sources:")
    for source in ["semantic_scholar", "arxiv_latex", "youtube", "google_news", "dappier"]:
        source_results = [r for r in search_results if r.source == source]
        if source_results:
            print(f"   • {source}: {len(source_results)} results")
            # Show first result from each source
            first = source_results[0]
            print(f"     - {first.title[:60]}...")
    
    # Step 4: Analyze discourse on the topic
    print("\n📈 Step 4: Analyzing discourse patterns...")
    discourse_analysis = await orchestrator.analyze_discourse(
        topic="artificial intelligence ethics",
        include_academic=True,
        include_media=True,
        include_video=True,
        time_window_days=30
    )
    
    print(f"📊 Discourse Analysis Results:")
    print(f"   • Total items analyzed: {discourse_analysis.total_items}")
    print(f"   • Time period: {discourse_analysis.time_range['start']} to {discourse_analysis.time_range['end']}")
    print(f"   • Sources included: {len(discourse_analysis.sources)}")
    
    if discourse_analysis.cross_references:
        print(f"   • Cross-references found: {len(discourse_analysis.cross_references)}")
        for ref in discourse_analysis.cross_references[:3]:
            print(f"     - {ref['type']}: {ref['description'][:60]}...")
    
    # Step 5: Document processing
    print("\n📄 Step 5: Document processing pipeline...")
    
    # Convert a sample document
    doc_path = Path("examples/sample_research.docx")
    if doc_path.exists():
        # Convert DOCX to Markdown
        md_result = await clients['markitdown'].convert_document(
            file_path=doc_path,
            options=ConversionOptions(
                preserve_formatting=True,
                extract_tables=True
            )
        )
        
        if md_result.success:
            print(f"✅ Converted DOCX to Markdown ({md_result.data.word_count} words)")
            
            # Convert Markdown to multiple formats
            formats = [ConversionFormat.HTML, ConversionFormat.LATEX, ConversionFormat.PDF]
            conversion_results = await clients['pandoc'].batch_convert_formats(
                content=md_result.data.markdown_content,
                from_format=ConversionFormat.MARKDOWN,
                to_formats=formats
            )
            
            for i, result in enumerate(conversion_results):
                if result.success:
                    print(f"   ✅ Converted to {formats[i].value}")
                else:
                    print(f"   ❌ Failed to convert to {formats[i].value}")
    
    # Step 6: Extract mathematical content
    print("\n🔢 Step 6: Extracting mathematical content...")
    math_papers = [r for r in search_results if r.source == "arxiv_latex"][:2]
    
    for paper in math_papers:
        if hasattr(paper, 'paper_id'):
            math_result = await clients['arxiv_latex'].extract_latex_formulas(paper.paper_id)
            if math_result.success and math_result.data:
                print(f"   📐 Paper: {paper.title[:50]}...")
                print(f"      Found {len(math_result.data)} formulas")
                if math_result.data:
                    print(f"      Example: {math_result.data[0][:50]}...")
    
    # Step 7: System monitoring
    print("\n📊 Step 7: System monitoring...")
    
    # Search for KGAS dashboards
    dashboard_result = await clients['grafana'].search_dashboards(
        query="kgas",
        tags=["production"]
    )
    
    if dashboard_result.success and dashboard_result.data:
        print(f"✅ Found {len(dashboard_result.data)} monitoring dashboards")
        
        # Check for active alerts
        alerts_result = await clients['grafana'].get_alerts(
            states=[AlertState.ALERTING, AlertState.PENDING]
        )
        
        if alerts_result.success:
            if alerts_result.data:
                print(f"⚠️  Active alerts: {len(alerts_result.data)}")
                for alert in alerts_result.data[:3]:
                    print(f"   - {alert.name}: {alert.message}")
            else:
                print("✅ No active alerts")
    
    # Step 8: Service health check
    print("\n🏥 Step 8: Service health status...")
    
    for service_name, client in clients.items():
        if hasattr(client, 'get_health_status'):
            try:
                health = await client.get_health_status()
                status = health.get('service_status', 'unknown')
                cb_state = health.get('circuit_breaker_state', 'unknown')
                
                status_icon = "✅" if status == "healthy" else "❌"
                print(f"   {status_icon} {service_name}: {status} (CB: {cb_state})")
                
                # Show rate limit info
                if 'rate_limit_remaining' in health:
                    print(f"      Rate limit: {health['rate_limit_remaining']} requests remaining")
            except Exception as e:
                print(f"   ❌ {service_name}: Error checking health - {str(e)}")
    
    # Step 9: Create monitoring annotation
    print("\n📝 Step 9: Creating monitoring annotation...")
    annotation_result = await clients['grafana'].create_annotation(
        text="MCP Integration Demo completed successfully",
        tags=["demo", "integration-test"],
        time=datetime.now()
    )
    
    if annotation_result.success:
        print("✅ Created Grafana annotation for demo completion")
    
    # Summary
    print("\n" + "="*60)
    print("🎉 MCP Integration Demo Complete!")
    print("="*60)
    print(f"✅ Authenticated user with {len(auth_result.data.user.roles)} roles")
    print(f"✅ Searched {len(search_results)} items across {len(set(r.source for r in search_results))} sources")
    print(f"✅ Analyzed discourse with {discourse_analysis.total_items} items")
    print(f"✅ Processed documents through conversion pipeline")
    print(f"✅ Monitored system health across {len(clients)} services")
    print("\n💡 This demo showcases the power of unified MCP integration for")
    print("   comprehensive discourse analysis and system monitoring.")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())