"""Command-line interface for Solomon project."""

import asyncio
import json
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

from solomon.config import settings
from solomon.agents.orchestrator import AgentOrchestrator, OrchestrationRequest, AnalysisType
from solomon.database import DatabaseManager
from solomon.database.models import TextType
from solomon.scraping.scraping_manager import ScrapingManager

app = typer.Typer(
    name="solomon",
    help="Solomon-Sophia: AI-powered analysis of spiritual and religious texts",
    add_completion=False
)
console = Console()


@app.command()
def analyze(
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Text to analyze"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="File containing text to analyze"),
    analysis_type: str = typer.Option("full", "--type", help="Analysis type (full, themes, doctrines, fallacies)"),
    tradition: Optional[str] = typer.Option(None, "--tradition", help="Religious tradition"),
    denomination: Optional[str] = typer.Option(None, "--denomination", help="Denomination"),
    language: str = typer.Option("english", "--language", help="Text language"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for results"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Analyze spiritual text using Solomon agents."""
    
    # Get text content
    if file:
        if not file.exists():
            console.print(f"[red]Error: File {file} not found[/red]")
            raise typer.Exit(1)
        text = file.read_text(encoding='utf-8')
    elif not text:
        console.print("[red]Error: Either --text or --file must be provided[/red]")
        raise typer.Exit(1)
    
    # Validate analysis type
    analysis_types = {
        "full": AnalysisType.FULL_ANALYSIS,
        "themes": AnalysisType.THEME_ANALYSIS,
        "doctrines": AnalysisType.DOCTRINE_ANALYSIS,
        "fallacies": AnalysisType.FALLACY_DETECTION,
        "translation": AnalysisType.TRANSLATION_ANALYSIS,
        "cross-ref": AnalysisType.CROSS_REFERENCE
    }
    
    if analysis_type not in analysis_types:
        console.print(f"[red]Error: Invalid analysis type. Choose from: {', '.join(analysis_types.keys())}[/red]")
        raise typer.Exit(1)
    
    # Run analysis
    asyncio.run(_run_analysis(
        text=text,
        analysis_type=analysis_types[analysis_type],
        tradition=tradition,
        denomination=denomination,
        language=language,
        output=output,
        verbose=verbose
    ))


async def _run_analysis(
    text: str,
    analysis_type: AnalysisType,
    tradition: Optional[str],
    denomination: Optional[str],
    language: str,
    output: Optional[Path],
    verbose: bool
):
    """Run the analysis asynchronously."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Initialize orchestrator
        task = progress.add_task("Initializing agents...", total=None)
        orchestrator = AgentOrchestrator()
        
        # Check agent health
        progress.update(task, description="Checking agent health...")
        health_status = await orchestrator.health_check()
        
        if not all(health_status.values()):
            console.print("[yellow]Warning: Some agents are not healthy[/yellow]")
            if verbose:
                for agent, status in health_status.items():
                    status_icon = "✓" if status else "✗"
                    console.print(f"  {status_icon} {agent}")
        
        # Prepare request
        progress.update(task, description="Preparing analysis request...")
        request = OrchestrationRequest(
            analysis_type=analysis_type,
            text=text,
            tradition=tradition,
            denomination=denomination,
            language=language
        )
        
        # Execute analysis
        progress.update(task, description=f"Running {analysis_type.value} analysis...")
        result = await orchestrator.execute_analysis(request)
        
        progress.update(task, description="Analysis complete!", completed=True)
    
    # Display results
    if result.success:
        console.print(f"[green]✓ Analysis completed successfully[/green]")
        console.print(f"[dim]Execution time: {result.execution_time:.2f}s[/dim]")
        
        _display_results(result.results, analysis_type, verbose)
        
        # Save to file if requested
        if output:
            output_data = {
                "request_id": result.request_id,
                "analysis_type": result.analysis_type.value,
                "results": result.results,
                "execution_time": result.execution_time,
                "timestamp": result.timestamp.isoformat()
            }
            
            output.write_text(json.dumps(output_data, indent=2, default=str))
            console.print(f"[green]Results saved to {output}[/green]")
    
    else:
        console.print(f"[red]✗ Analysis failed: {result.error}[/red]")
        raise typer.Exit(1)
    
    # Cleanup
    await orchestrator.close()


def _display_results(results: dict, analysis_type: AnalysisType, verbose: bool):
    """Display analysis results in a formatted way."""
    
    if analysis_type == AnalysisType.FULL_ANALYSIS:
        _display_full_analysis(results, verbose)
    elif analysis_type == AnalysisType.THEME_ANALYSIS:
        _display_theme_analysis(results, verbose)
    elif analysis_type == AnalysisType.DOCTRINE_ANALYSIS:
        _display_doctrine_analysis(results, verbose)
    elif analysis_type == AnalysisType.FALLACY_DETECTION:
        _display_fallacy_analysis(results, verbose)
    else:
        # Generic display
        console.print(Panel(
            Syntax(json.dumps(results, indent=2, default=str), "json"),
            title="Analysis Results"
        ))


def _display_full_analysis(results: dict, verbose: bool):
    """Display full analysis results."""
    
    # Summary
    summary = results.get("analysis_summary", {})
    console.print(Panel(
        f"[bold]Themes detected:[/bold] {summary.get('themes_detected', 0)}\n"
        f"[bold]Doctrines detected:[/bold] {summary.get('doctrines_detected', 0)}\n"
        f"[bold]Fallacies detected:[/bold] {summary.get('fallacies_detected', 0)}\n"
        f"[bold]Overall score:[/bold] {summary.get('overall_score', 0):.2f}",
        title="Analysis Summary"
    ))
    
    # Insights
    insights = results.get("insights", [])
    if insights:
        console.print("\n[bold]Key Insights:[/bold]")
        for i, insight in enumerate(insights, 1):
            console.print(f"  {i}. {insight}")
    
    # Cross-tradition connections
    connections = results.get("cross_tradition_connections", [])
    if connections:
        console.print("\n[bold]Cross-Tradition Connections:[/bold]")
        for conn in connections:
            console.print(f"  • {conn.get('description', 'Unknown connection')}")
    
    if verbose:
        # Detailed results
        themes = results.get("themes", {})
        if themes.get("themes"):
            _display_theme_details(themes["themes"])
        
        doctrines = results.get("doctrines", {})
        if doctrines.get("doctrines"):
            _display_doctrine_details(doctrines["doctrines"])
        
        fallacies = results.get("fallacies", {})
        if fallacies.get("fallacies"):
            _display_fallacy_details(fallacies["fallacies"])


def _display_theme_analysis(results: dict, verbose: bool):
    """Display theme analysis results."""
    themes = results.get("themes", [])
    
    if not themes:
        console.print("[yellow]No themes detected[/yellow]")
        return
    
    console.print(f"[green]Found {len(themes)} spiritual themes:[/green]\n")
    _display_theme_details(themes)


def _display_theme_details(themes: List[dict]):
    """Display detailed theme information."""
    table = Table(title="Detected Themes")
    table.add_column("Theme", style="cyan")
    table.add_column("Confidence", style="green")
    table.add_column("Excerpts", style="yellow")
    
    for theme in themes:
        excerpts = theme.get("text_excerpts", [])
        excerpt_text = excerpts[0][:100] + "..." if excerpts else "N/A"
        
        table.add_row(
            theme.get("theme_name", "Unknown"),
            f"{theme.get('confidence_score', 0):.2f}",
            excerpt_text
        )
    
    console.print(table)


def _display_doctrine_analysis(results: dict, verbose: bool):
    """Display doctrine analysis results."""
    doctrines = results.get("doctrines", [])
    
    if not doctrines:
        console.print("[yellow]No doctrines detected[/yellow]")
        return
    
    console.print(f"[green]Found {len(doctrines)} religious doctrines:[/green]\n")
    _display_doctrine_details(doctrines)


def _display_doctrine_details(doctrines: List[dict]):
    """Display detailed doctrine information."""
    table = Table(title="Detected Doctrines")
    table.add_column("Doctrine", style="cyan")
    table.add_column("Tradition", style="blue")
    table.add_column("Confidence", style="green")
    table.add_column("Context", style="yellow")
    
    for doctrine in doctrines:
        excerpts = doctrine.get("text_excerpts", [])
        context = excerpts[0][:80] + "..." if excerpts else "N/A"
        
        table.add_row(
            doctrine.get("doctrine_name", "Unknown"),
            doctrine.get("tradition", "Unknown"),
            f"{doctrine.get('confidence_score', 0):.2f}",
            context
        )
    
    console.print(table)


def _display_fallacy_analysis(results: dict, verbose: bool):
    """Display fallacy analysis results."""
    fallacies = results.get("fallacies", [])
    
    if not fallacies:
        console.print("[green]No logical fallacies detected[/green]")
        return
    
    console.print(f"[yellow]Found {len(fallacies)} potential logical fallacies:[/yellow]\n")
    _display_fallacy_details(fallacies)


def _display_fallacy_details(fallacies: List[dict]):
    """Display detailed fallacy information."""
    table = Table(title="Detected Fallacies")
    table.add_column("Fallacy Type", style="red")
    table.add_column("Confidence", style="green")
    table.add_column("Context", style="yellow")
    table.add_column("Explanation", style="dim")
    
    for fallacy in fallacies:
        table.add_row(
            fallacy.get("fallacy_type", "Unknown").replace("_", " ").title(),
            f"{fallacy.get('confidence_score', 0):.2f}",
            fallacy.get("context", "N/A")[:60] + "...",
            fallacy.get("explanation", "N/A")[:80] + "..."
        )
    
    console.print(table)


@app.command()
def serve(
    host: str = typer.Option(settings.api_host, "--host", help="Host to bind to"),
    port: int = typer.Option(settings.api_port, "--port", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
    log_level: str = typer.Option(settings.log_level.lower(), "--log-level", help="Log level")
):
    """Start the Solomon API server."""
    import uvicorn
    
    console.print(f"[green]Starting Solomon API server on {host}:{port}[/green]")
    console.print(f"[dim]Docs available at: http://{host}:{port}/docs[/dim]")
    
    uvicorn.run(
        "solomon.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )


@app.command()
def init_db():
    """Initialize the database."""
    console.print("[yellow]Initializing database...[/yellow]")
    
    try:
        db_manager = DatabaseManager()
        db_manager.create_tables()
        console.print("[green]✓ Database initialized successfully[/green]")
    except Exception as e:
        console.print(f"[red]✗ Database initialization failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def health():
    """Check system health."""
    asyncio.run(_health_check())


async def _health_check():
    """Run health check asynchronously."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Checking system health...", total=None)
        
        # Check agents
        orchestrator = AgentOrchestrator()
        agent_health = await orchestrator.health_check()
        
        progress.update(task, description="Health check complete!", completed=True)
    
    # Display results
    table = Table(title="System Health")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    for agent, status in agent_health.items():
        status_text = "✓ Healthy" if status else "✗ Unhealthy"
        status_style = "green" if status else "red"
        table.add_row(agent.replace("_", " ").title(), f"[{status_style}]{status_text}[/{status_style}]")
    
    console.print(table)
    
    # Overall status
    all_healthy = all(agent_health.values())
    if all_healthy:
        console.print("\n[green]✓ All systems operational[/green]")
    else:
        console.print("\n[red]✗ Some systems are unhealthy[/red]")
        raise typer.Exit(1)
    
    await orchestrator.close()


@app.command()
def config():
    """Show current configuration."""
    table = Table(title="Solomon Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    config_items = [
        ("Debug Mode", settings.debug),
        ("Log Level", settings.log_level),
        ("API Host", settings.api_host),
        ("API Port", settings.api_port),
        ("Database URL", settings.database_url.split("@")[-1]),  # Hide credentials
        ("HF Model", settings.hf_model_name),
        ("HF Embedding", settings.hf_embedding_model),
        ("Embedding Dim", settings.embedding_dimension),
        ("Use Local Only", settings.use_local_models_only),
        ("TensorFlow", settings.use_tensorflow),
        ("TF Model", settings.tf_model_name),
        ("Ollama Host", settings.ollama_host),
        ("Ollama Model", settings.ollama_model),
        ("Use Ollama", settings.use_ollama),
        ("Qdrant Host", f"{settings.qdrant_host}:{settings.qdrant_port}"),
    ]
    
    for setting, value in config_items:
        table.add_row(setting, str(value))
    
    console.print(table)


@app.command()
def scrape(
    text_types: Optional[List[str]] = typer.Option(None, "--types", "-t", help="Text types to scrape (bible, quran, bhagavad_gita, upanishads, dhammapada)"),
    bible_books: Optional[List[str]] = typer.Option(None, "--bible-books", help="Bible books to scrape"),
    bible_versions: Optional[List[str]] = typer.Option(None, "--bible-versions", help="Bible versions to scrape"),
    quran_surahs: Optional[List[int]] = typer.Option(None, "--quran-surahs", help="Quran surahs to scrape"),
    gita_chapters: Optional[List[int]] = typer.Option(None, "--gita-chapters", help="Bhagavad Gita chapters to scrape"),
    dhammapada_chapters: Optional[List[int]] = typer.Option(None, "--dhammapada-chapters", help="Dhammapada chapters to scrape"),
    include_sanskrit: bool = typer.Option(True, "--sanskrit/--no-sanskrit", help="Include Sanskrit texts"),
    include_arabic: bool = typer.Option(True, "--arabic/--no-arabic", help="Include Arabic texts"),
    include_pali: bool = typer.Option(True, "--pali/--no-pali", help="Include Pali texts"),
    min_quality: float = typer.Option(0.3, "--min-quality", help="Minimum quality score for texts"),
    max_texts: int = typer.Option(100, "--max-texts", help="Maximum texts per type"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Export scraped data to file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Scrape spiritual texts from online sources and add to database."""
    
    # Default text types if none specified
    if not text_types:
        text_types = ["bible", "quran", "bhagavad_gita"]
    
    # Validate text types
    valid_types = ["bible", "quran", "bhagavad_gita", "upanishads", "dhammapada"]
    invalid_types = [t for t in text_types if t not in valid_types]
    if invalid_types:
        console.print(f"[red]Error: Invalid text types: {', '.join(invalid_types)}[/red]")
        console.print(f"Valid types: {', '.join(valid_types)}")
        raise typer.Exit(1)
    
    # Convert to TextType enums
    type_mapping = {
        "bible": TextType.BIBLE,
        "quran": TextType.QURAN,
        "bhagavad_gita": TextType.BHAGAVAD_GITA,
        "upanishads": TextType.UPANISHADS,
        "dhammapada": TextType.DHAMMAPADA
    }
    
    selected_types = [type_mapping[t] for t in text_types]
    
    console.print(f"[green]Starting scraping for: {', '.join(text_types)}[/green]")
    
    # Run scraping
    asyncio.run(_run_scraping(
        selected_types,
        bible_books=bible_books,
        bible_versions=bible_versions,
        quran_surahs=quran_surahs,
        gita_chapters=gita_chapters,
        dhammapada_chapters=dhammapada_chapters,
        include_sanskrit=include_sanskrit,
        include_arabic=include_arabic,
        include_pali=include_pali,
        min_quality=min_quality,
        max_texts=max_texts,
        output=output,
        verbose=verbose
    ))


async def _run_scraping(
    text_types: List[TextType],
    bible_books: Optional[List[str]] = None,
    bible_versions: Optional[List[str]] = None,
    quran_surahs: Optional[List[int]] = None,
    gita_chapters: Optional[List[int]] = None,
    dhammapada_chapters: Optional[List[int]] = None,
    include_sanskrit: bool = True,
    include_arabic: bool = True,
    include_pali: bool = True,
    min_quality: float = 0.3,
    max_texts: int = 100,
    output: Optional[Path] = None,
    verbose: bool = False
):
    """Run the scraping process asynchronously."""
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        await db_manager.initialize()
        
        # Initialize scraping manager
        scraping_manager = ScrapingManager(db_manager)
        
        # Create scraping configuration
        config = scraping_manager.create_scraping_config(
            text_types,
            bible_books=bible_books or ['genesis', 'matthew', 'john'],
            bible_versions=bible_versions or ['NIV', 'ESV'],
            quran_surahs=quran_surahs or list(range(1, 6)),
            gita_chapters=gita_chapters or list(range(1, 4)),
            dhammapada_chapters=dhammapada_chapters or list(range(1, 4)),
            include_sanskrit=include_sanskrit,
            include_arabic=include_arabic,
            include_pali=include_pali,
            min_quality=min_quality,
            max_texts_per_type=max_texts
        )
        
        if verbose:
            console.print("[blue]Scraping configuration:[/blue]")
            console.print(json.dumps(config, indent=2, default=str))
        
        # Run scraping with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Scraping texts...", total=None)
            
            results = await scraping_manager.scrape_and_store(text_types, config)
            
            progress.update(task, description="Scraping completed!")
        
        # Display results
        _display_scraping_results(results, verbose)
        
        # Export data if requested
        if output:
            export_path = await scraping_manager.export_scraped_data(
                str(output), text_types, 'json'
            )
            console.print(f"[green]Data exported to: {export_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error during scraping: {str(e)}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


def _display_scraping_results(results: dict, verbose: bool = False):
    """Display scraping results in a formatted way."""
    
    # Summary panel
    summary_text = f"""
    [green]✓[/green] Scraping completed successfully
    [blue]Started:[/blue] {results['started_at']}
    [blue]Completed:[/blue] {results['completed_at']}
    [blue]Text Types:[/blue] {', '.join(results['text_types'])}
    """
    
    console.print(Panel(summary_text, title="Scraping Summary", border_style="green"))
    
    # Results table
    table = Table(title="Scraping Results")
    table.add_column("Text Type", style="cyan")
    table.add_column("Scraped", justify="right", style="yellow")
    table.add_column("Saved", justify="right", style="green")
    
    total_scraped = sum(results['scraped_counts'].values())
    total_saved = results['saved_counts'].get('total', 0)
    
    for text_type in results['text_types']:
        scraped_count = results['scraped_counts'].get(text_type, 0)
        table.add_row(text_type, str(scraped_count), "")
    
    table.add_row("", "", "")  # Separator
    table.add_row("TOTAL", str(total_scraped), str(total_saved))
    
    console.print(table)
    
    # Processing stats
    if 'processing_stats' in results and results['processing_stats']:
        stats = results['processing_stats']
        
        stats_text = f"""
        [blue]Total Texts Processed:[/blue] {stats.get('total_texts', 0)}
        [blue]Total Words:[/blue] {stats.get('total_words', 0):,}
        [blue]Average Words per Text:[/blue] {stats.get('average_words_per_text', 0):.1f}
        [blue]Average Quality Score:[/blue] {stats.get('average_quality_score', 0):.2f}
        [blue]High Quality Texts:[/blue] {stats.get('high_quality_texts', 0)}
        """
        
        console.print(Panel(stats_text, title="Processing Statistics", border_style="blue"))
        
        # Theme distribution
        if verbose and 'theme_distribution' in stats:
            theme_table = Table(title="Theme Distribution")
            theme_table.add_column("Theme", style="cyan")
            theme_table.add_column("Count", justify="right", style="yellow")
            
            for theme, count in sorted(stats['theme_distribution'].items(), key=lambda x: x[1], reverse=True):
                theme_table.add_row(theme, str(count))
            
            console.print(theme_table)
    
    # Errors
    if results.get('errors'):
        console.print(f"\n[yellow]Warnings/Errors ({len(results['errors'])}):[/yellow]")
        for error in results['errors'][:5]:  # Show first 5 errors
            console.print(f"  • {error}")
        
        if len(results['errors']) > 5:
            console.print(f"  ... and {len(results['errors']) - 5} more")


@app.command()
def scrape_status():
    """Show current status of scraped texts in database."""
    asyncio.run(_show_scraping_status())


async def _show_scraping_status():
    """Show scraping status asynchronously."""
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        await db_manager.initialize()
        
        # Initialize scraping manager
        scraping_manager = ScrapingManager(db_manager)
        
        # Get status
        status = await scraping_manager.get_scraping_status()
        
        # Display status
        console.print(Panel(f"[green]Database Status[/green]\n[blue]Total Texts:[/blue] {status['total_texts']}\n[blue]Recent Additions:[/blue] {status['recent_additions']}", title="Scraping Status"))
        
        # Texts by type table
        table = Table(title="Texts by Type")
        table.add_column("Text Type", style="cyan")
        table.add_column("Count", justify="right", style="yellow")
        
        for text_type, count in status['texts_by_type'].items():
            table.add_row(text_type, str(count))
        
        console.print(table)
        
        # Supported types
        console.print(f"\n[blue]Supported Text Types:[/blue] {', '.join(status['supported_types'])}")
        
    except Exception as e:
        console.print(f"[red]Error getting status: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def scrape_specific(
    config_file: Path = typer.Argument(..., help="JSON configuration file for specific scraping requests"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Scrape specific texts based on detailed configuration file."""
    
    if not config_file.exists():
        console.print(f"[red]Error: Configuration file {config_file} not found[/red]")
        raise typer.Exit(1)
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error parsing configuration file: {str(e)}[/red]")
        raise typer.Exit(1)
    
    if 'requests' not in config:
        console.print("[red]Error: Configuration file must contain 'requests' array[/red]")
        raise typer.Exit(1)
    
    console.print(f"[green]Processing {len(config['requests'])} scraping requests[/green]")
    
    # Run specific scraping
    asyncio.run(_run_specific_scraping(config['requests'], verbose))


async def _run_specific_scraping(requests: List[dict], verbose: bool = False):
    """Run specific scraping requests asynchronously."""
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        await db_manager.initialize()
        
        # Initialize scraping manager
        scraping_manager = ScrapingManager(db_manager)
        
        # Run scraping with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Processing requests...", total=None)
            
            results = await scraping_manager.scrape_specific_texts(requests)
            
            progress.update(task, description="Processing completed!")
        
        # Display results
        console.print(Panel(
            f"[green]✓[/green] Processed {results['requests_processed']} requests\n"
            f"[blue]Texts Scraped:[/blue] {results['texts_scraped']}\n"
            f"[blue]Texts Saved:[/blue] {results['texts_saved']}",
            title="Specific Scraping Results"
        ))
        
        if results.get('errors') and verbose:
            console.print(f"\n[yellow]Errors ({len(results['errors'])}):[/yellow]")
            for error in results['errors']:
                console.print(f"  • {error}")
        
    except Exception as e:
        console.print(f"[red]Error during specific scraping: {str(e)}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
