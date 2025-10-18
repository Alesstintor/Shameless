"""
Command-line interface for Shameless Sentiment Analyser.

Provides commands for scraping and analyzing sentiment.
"""

import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from sentiment_analyser.config import get_settings
from sentiment_analyser.models import SentimentAnalyzer, TextPreprocessor
from sentiment_analyser.scraper import DataStorage, TwitterCollector
from sentiment_analyser.utils import setup_logger

console = Console()
logger = setup_logger(__name__)


@click.group()
@click.version_option(version="0.1.0")
def main():
    """🎭 Shameless Sentiment Analyser CLI"""
    pass


@main.command()
@click.option("--query", "-q", help="Search query for tweets.")
@click.option("--user", "-U", help="Twitter user account to scrape tweets from.")
@click.option("--limit", "-l", default=100, help="Maximum number of tweets to collect.")
@click.option("--since", "-s", help="Start date (YYYY-MM-DD). Only for --query.")
@click.option("--until", "-u", help="End date (YYYY-MM-DD). Only for --query.")
@click.option("--output", "-o", help="Output file path.", type=click.Path())
@click.option("--format", "-f", type=click.Choice(["json", "csv", "parquet"]), default="json")
def scrape(
    query: Optional[str],
    user: Optional[str],
    limit: int,
    since: Optional[str],
    until: Optional[str],
    output: Optional[str],
    format: str,
):
    """
    Scrape tweets from Twitter/X by query or from a specific user.

    Examples:
        shameless scrape -q "python" -l 100 -o tweets.json
        shameless scrape -U "elonmusk" -l 50 -o elon_tweets.json
    """
    # Validate inputs
    if not query and not user:
        console.print("[bold red]❌ Error:[/bold red] Please provide either a [cyan]--query[/cyan] or a [cyan]--user[/cyan].")
        return
    if query and user:
        console.print("[bold red]❌ Error:[/bold red] Options [cyan]--query[/cyan] and [cyan]--user[/cyan] are mutually exclusive.")
        return

    settings = get_settings()
    collector = TwitterCollector(rate_limit=settings.SCRAPER_RATE_LIMIT)
    storage = DataStorage(settings.RAW_DATA_DIR)
    
    iterator = None
    task_description = ""
    
    if query:
        console.print(f"[bold blue]🐦 Scraping tweets for query:[/bold blue] {query}")
        console.print(f"[dim]Limit: {limit} | Since: {since or 'N/A'} | Until: {until or 'N/A'}[/dim]\n")
        iterator = collector.search(query=query, limit=limit, since=since, until=until)
        task_description = f"Collecting tweets for '{query}'..."
    
    elif user:
        if since or until:
            console.print("[bold yellow]⚠️ Warning:[/bold yellow] --since and --until are ignored when scraping by user.\n")
        console.print(f"[bold blue]🐦 Scraping tweets from user:[/bold blue] @{user}")
        console.print(f"[dim]Limit: {limit}[/dim]\n")
        iterator = collector.get_user_tweets(username=user, limit=limit)
        task_description = f"Collecting tweets from @{user}..."

    tweets = []
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description=task_description, total=limit)
            for i, tweet in enumerate(iterator):
                tweets.append(tweet.to_dict())
                progress.update(task, advance=1, description=f"Collected {i + 1} tweets...")
    except Exception as e:
        console.print(f"[bold red]❌ An unexpected error occurred during scraping:[/bold red] {e}")
        return

    if not tweets:
        console.print("[yellow]No tweets were collected.[/yellow]")
        return

    # Save data
    if output:
        filename = output
    else:
        safe_name = ""
        if query:
            safe_name = query.replace(" ", "_")[:30]
        elif user:
            safe_name = f"user_{user}"
        filename = f"{safe_name}_{len(tweets)}.{format}"

    try:
        if format == "json":
            filepath = storage.save_json(tweets, filename)
        elif format == "csv":
            filepath = storage.save_csv(tweets, filename)
        else:  # parquet
            filepath = storage.save_parquet(tweets, filename)
        console.print(f"\n[bold green]✅ Saved {len(tweets)} tweets to:[/bold green] {filepath}")
    except Exception as e:
        console.print(f"[bold red]❌ Error saving data:[/bold red] {e}")


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output file path", type=click.Path())
@click.option("--model", "-m", default="distilbert-base-uncased-finetuned-sst-2-english")
@click.option("--batch-size", "-b", default=32, help="Batch size for processing")
def analyze(input_file: str, output: Optional[str], model: str, batch_size: int):
    """
    Analyze sentiment of tweets from a file.
    
    Example:
        shameless analyze tweets.json -o analysis.csv
    """
    settings = get_settings()
    
    console.print(f"[bold blue]🤖 Analyzing sentiment:[/bold blue] {input_file}")
    console.print(f"[dim]Model: {model} | Batch size: {batch_size}[/dim]\n")
    
    # Load data
    storage = DataStorage(Path(input_file).parent)
    filename = Path(input_file).name
    
    try:
        if filename.endswith(".json"):
            data = storage.load_json(filename)
        elif filename.endswith(".csv"):
            data = storage.load_csv(filename).to_dict("records")
        elif filename.endswith(".parquet"):
            data = storage.load_parquet(filename).to_dict("records")
        else:
            console.print("[bold red]❌ Unsupported file format[/bold red]")
            return
            
        console.print(f"[green]Loaded {len(data)} records[/green]\n")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error loading data:[/bold red] {e}")
        return
    
    # Initialize analyzer
    preprocessor = TextPreprocessor()
    analyzer = SentimentAnalyzer(model_name=model, preprocess=False)
    
    # Extract texts
    texts = [item.get("content", item.get("text", "")) for item in data]
    
    # Preprocess
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Preprocessing texts...", total=len(texts))
        clean_texts = preprocessor.clean_batch(texts)
        progress.update(task, completed=len(texts))
    
    # Analyze sentiment
    console.print("\n[bold]Analyzing sentiment...[/bold]")
    
    try:
        results = analyzer.analyze_batch(clean_texts, batch_size=batch_size)
        
        # Add results to data
        for item, result in zip(data, results):
            item["sentiment"] = result["sentiment"]
            item["sentiment_score"] = result["score"]
            item["sentiment_label"] = result["label"]
            
    except Exception as e:
        console.print(f"[bold red]❌ Error during analysis:[/bold red] {e}")
        return
    
    # Display summary
    display_summary(data)
    
    # Save results
    if output:
        output_path = Path(output)
        storage_out = DataStorage(output_path.parent)
        
        try:
            if output_path.suffix == ".json":
                filepath = storage_out.save_json(data, output_path.name)
            elif output_path.suffix == ".csv":
                filepath = storage_out.save_csv(data, output_path.name)
            else:
                filepath = storage_out.save_parquet(data, output_path.name)
                
            console.print(f"\n[bold green]✅ Results saved to:[/bold green] {filepath}")
            
        except Exception as e:
            console.print(f"[bold red]❌ Error saving results:[/bold red] {e}")


def display_summary(data):
    """Display sentiment analysis summary."""
    from collections import Counter
    
    sentiments = [item["sentiment"] for item in data]
    sentiment_counts = Counter(sentiments)
    
    table = Table(title="\n📊 Sentiment Analysis Summary")
    table.add_column("Sentiment", style="cyan", justify="left")
    table.add_column("Count", style="magenta", justify="right")
    table.add_column("Percentage", style="green", justify="right")
    
    total = len(data)
    for sentiment, count in sentiment_counts.most_common():
        percentage = (count / total) * 100
        table.add_row(sentiment.capitalize(), str(count), f"{percentage:.1f}%")
    
    console.print(table)
    
    # Average confidence
    avg_confidence = sum(item["sentiment_score"] for item in data) / total
    console.print(f"\n[bold]Average Confidence:[/bold] {avg_confidence:.2%}")


if __name__ == "__main__":
    main()
